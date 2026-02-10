import os
import cv2
import numpy as np
import zmq
from msgpack import packb, unpackb
from PyQt5.QtCore import QThread, pyqtSignal


class CaptureThread(QThread):
    """
    Binocular-capable capture thread for Pupil Core.

    - Subscribes to frame.eye.0 / frame.eye.1
    - Subscribes to pupil.0 / pupil.1 (fallback to pupil.* with id field)
    - Displays two 640x480 eye images in monitor_1 (two rows)
    - Exposes eye0/eye1 images + ellipse parameters for saving thread
    """
    save_frame_signal = pyqtSignal()
    save_information_signal = pyqtSignal()

    def __init__(self, manage):
        super().__init__()
        self.manage = manage

        # Desired output resolution (request to Pupil)
        self.width = 640
        self.height = 480

        self.is_running = True
        self.last_frame_time = 0.0
        self.frame_interval = 1.0 / float(self.manage.hyperparameters.fps)
        self.frame_count = 0

        # latest frames (original, ellipse-overlay)
        self.recent_eye0_original = None
        self.recent_eye1_original = None
        self.recent_eye0_ellipse = None
        self.recent_eye1_ellipse = None

        # latest ellipse params (for CSV saving)
        self.frame_axis = (0, 0)          # eye0
        self.frame_diameter = (0, 0)      # eye0
        self.angle = 0.0                 # eye0

        self.frame_axis_1 = (0, 0)        # eye1
        self.frame_diameter_1 = (0, 0)    # eye1
        self.angle_1 = 0.0               # eye1

        self.isCaptured = False
        self.original_path = "Datas/Original"  # base/original
        self.ellipse_path = "Datas/GT"         # base/gt
        self.frame_name = ""

        self.color = (0, 255, 0)  # green
        self.mean = 128

        # Pupil remote
        addr = "127.0.0.1"
        req_port = "50020"
        self.context = zmq.Context.instance()
        self.req = self.context.socket(zmq.REQ)
        self.req.connect(f"tcp://{addr}:{req_port}")

        # Ask for SUB port
        self.req.send_string("SUB_PORT")
        sub_port = self.req.recv_string()

        # One SUB socket for both frame + pupil topics (avoids ordering issues)
        self.sub = self.context.socket(zmq.SUB)
        self.sub.connect(f"tcp://{addr}:{sub_port}")
        for t in ("frame.eye.0", "frame.eye.1", "pupil.0", "pupil.1", "pupil."):
            self.sub.setsockopt_string(zmq.SUBSCRIBE, t)

        self.poller = zmq.Poller()
        self.poller.register(self.sub, zmq.POLLIN)

        # Request frame format
        self.FRAME_FORMAT = "bgr"
        self._configure_stream()

        # Latest pupil messages per eye
        self._last_pupil = {0: None, 1: None}

    def __del__(self):
        try:
            self.is_running = False
            self.wait(500)
        except Exception:
            pass

    # ---- Pupil Remote helpers ----
    def notify(self, notification: dict) -> str:
        topic = "notify." + notification["subject"]
        payload = packb(notification, use_bin_type=True)
        self.req.send_string(topic, flags=zmq.SNDMORE)
        self.req.send(payload)
        return self.req.recv_string()

    def _configure_stream(self):
        # Ask Pupil to publish frames in desired format/resolution.
        # Some setups may still output jpeg at times; we handle both robustly.
        self.notify({
            "subject": "frame_publishing.set_format",
            "format": self.FRAME_FORMAT,
            "width": self.width,
            "height": self.height
        })

    def recv_from_sub(self):
        topic = self.sub.recv_string()
        payload = unpackb(self.sub.recv(), raw=False)

        extra_frames = []
        while self.sub.get(zmq.RCVMORE):
            extra_frames.append(self.sub.recv())
        if extra_frames:
            payload["__raw_data__"] = extra_frames
        return topic, payload

    # ---- Image utils ----
    @staticmethod
    def adjust_brightness_to_target_mean(image, target_mean=128):
        current_mean = float(np.mean(image)) if image is not None else 0.0
        if current_mean <= 1e-6:
            return image
        return cv2.convertScaleAbs(image, alpha=target_mean / current_mean)

    @staticmethod
    def _decode_frame(msg):
        fmt = msg.get("format", None)
        buf = None
        if "__raw_data__" in msg and msg["__raw_data__"]:
            buf = msg["__raw_data__"][0]
        elif "data" in msg:
            buf = msg["data"]

        if buf is None:
            return None

        if fmt == "bgr":
            w, h = int(msg["width"]), int(msg["height"])
            arr = np.frombuffer(buf, dtype=np.uint8)
            expected = w * h * 3
            if arr.size != expected:
                # fallback: try decode as jpeg
                jpg = np.frombuffer(buf, dtype=np.uint8)
                return cv2.imdecode(jpg, cv2.IMREAD_COLOR)
            return arr.reshape(h, w, 3)

        if fmt == "jpeg":
            jpg = np.frombuffer(buf, dtype=np.uint8)
            return cv2.imdecode(jpg, cv2.IMREAD_COLOR)

        # Unknown format: best effort
        jpg = np.frombuffer(buf, dtype=np.uint8)
        return cv2.imdecode(jpg, cv2.IMREAD_COLOR)

    def _ellipse_to_params(self, ellipse_dict, w, h):
        # Keep the project's existing convention (x2 scaling + mirrored center)
        def mul2(x): return x * 2

        center = tuple(map(mul2, ellipse_dict["center"]))
        axes = tuple(map(mul2, ellipse_dict["axes"]))
        angle = float(ellipse_dict["angle"])

        axis = (w - center[0], h - center[1])
        diameter = axes
        return axis, diameter, angle

    def _render_overlay(self, original, axis, diameter, angle):
        if original is None:
            return None
        out = original.copy()
        try:
            out = cv2.ellipse(out, (axis, diameter, angle), self.color, thickness=2)
        except Exception:
            # In case ellipse params are invalid
            pass
        return out

    # ---- Main loop ----
    def run(self):
        print("캡처 스레드 실행 중 (binocular)")
        while self.is_running:
            socks = dict(self.poller.poll(timeout=50))  # 20 fps-ish loop; actual saving is time-gated
            if self.sub not in socks:
                continue

            try:
                topic, msg = self.recv_from_sub()
            except Exception:
                continue

            # FRAME
            if topic.startswith("frame.eye."):
                eye_id = 0 if topic.endswith(".0") else 1
                img = self._decode_frame(msg)
                if img is None:
                    continue

                # Keep existing transform pipeline
                img = self.adjust_brightness_to_target_mean(cv2.add(img, 1), target_mean=128)
                img = cv2.flip(img, flipCode=-1)
                img = cv2.resize(img, (self.width, self.height))

                if eye_id == 0:
                    self.recent_eye0_original = img
                    pupil_msg = self._last_pupil.get(0)
                    if pupil_msg and "ellipse" in pupil_msg:
                        self.frame_axis, self.frame_diameter, self.angle = self._ellipse_to_params(
                            pupil_msg["ellipse"], self.width, self.height
                        )
                    self.recent_eye0_ellipse = self._render_overlay(
                        self.recent_eye0_original, self.frame_axis, self.frame_diameter, self.angle
                    )
                    # UI
                    if hasattr(self.manage.monitor_1_ui, "Camera_view0"):
                        self.manage.monitor_1_ui.Camera_view0.setScreen(self.recent_eye0_ellipse)
                    else:
                        # backward compatibility
                        self.manage.monitor_1_ui.Camera_view.setScreen(self.recent_eye0_ellipse)

                else:
                    self.recent_eye1_original = img
                    pupil_msg = self._last_pupil.get(1)
                    if pupil_msg and "ellipse" in pupil_msg:
                        self.frame_axis_1, self.frame_diameter_1, self.angle_1 = self._ellipse_to_params(
                            pupil_msg["ellipse"], self.width, self.height
                        )
                    self.recent_eye1_ellipse = self._render_overlay(
                        self.recent_eye1_original, self.frame_axis_1, self.frame_diameter_1, self.angle_1
                    )
                    # UI
                    if hasattr(self.manage.monitor_1_ui, "Camera_view1"):
                        self.manage.monitor_1_ui.Camera_view1.setScreen(self.recent_eye1_ellipse)

                # Saving trigger: require both eyes if binocular saving is desired
                current_time = float(msg.get("timestamp", 0.0))
                if self.isCaptured and (current_time - self.last_frame_time >= self.frame_interval or current_time - self.last_frame_time < 0):
                    # Only save when both eyes are available (binocular)
                    if self.recent_eye0_original is not None and self.recent_eye1_original is not None:
                        if not os.path.exists(self.original_path):
                            os.makedirs(self.original_path, exist_ok=True)
                        if not os.path.exists(self.ellipse_path):
                            os.makedirs(self.ellipse_path, exist_ok=True)

                        self.manage.current_frame_no += 1
                        self.frame_name = f"{self.manage.current_phase}_{self.manage.current_frame_no}"
                        self.last_frame_time = current_time
                        self.save_information_signal.emit()

                self.save_frame_signal.emit()
                continue

            # PUPIL
            if topic.startswith("pupil"):
                # Determine eye id
                eye_id = None
                if topic == "pupil.0":
                    eye_id = 0
                elif topic == "pupil.1":
                    eye_id = 1
                else:
                    # generic pupil.* topic: check 'id' field
                    if "id" in msg:
                        try:
                            eye_id = int(msg["id"])
                        except Exception:
                            eye_id = None

                if eye_id in (0, 1):
                    self._last_pupil[eye_id] = msg
                continue
