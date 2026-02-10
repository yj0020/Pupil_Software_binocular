import cv2
import numpy as np
import zmq
from msgpack import unpackb, packb

context = zmq.Context()
addr = "127.0.0.1"
req_port = "50020"
req = context.socket(zmq.REQ)
req.connect(f"tcp://{addr}:{req_port}")

req.send_string("SUB_PORT")
sub_port = req.recv_string()

def notify(notification):
    topic = "notify." + notification["subject"]
    payload = packb(notification, use_bin_type=True)
    req.send_string(topic, flags=zmq.SNDMORE)
    req.send(payload)
    return req.recv_string()

sub = context.socket(zmq.SUB)
sub.connect(f"tcp://{addr}:{sub_port}")
sub.setsockopt_string(zmq.SUBSCRIBE, "frame.")
sub.setsockopt_string(zmq.SUBSCRIBE, "pupil.")

def recv_from_sub():
    topic = sub.recv_string()
    payload = unpackb(sub.recv(), raw=False)
    extra_frames = []
    while sub.get(zmq.RCVMORE):
        extra_frames.append(sub.recv())
    if extra_frames:
        payload["__raw_data__"] = extra_frames
    return topic, payload

def has_new_data_available():
    return sub.get(zmq.EVENTS) & zmq.POLLIN

recent_world = None
recent_eye0 = None
recent_eye1 = None

FRAME_FORMAT = "bgr"

notify({"subject": "frame_publishing.set_format", "format": FRAME_FORMAT})

# 원하는 해상도 설정
desired_width = 640
desired_height = 480

try:
    while True:
        while has_new_data_available():
            topic, msg = recv_from_sub()

            if topic.startswith("frame.") and msg["format"] != FRAME_FORMAT:
                print(f"different frame format ({msg['format']}); skipping frame from {topic}")
                continue

            if topic == "frame.world":
                recent_world = np.frombuffer(msg["__raw_data__"][0], dtype=np.uint8).reshape(msg["height"], msg["width"], 3)
                if recent_world is not None:
                    recent_world = cv2.resize(recent_world, (desired_width, desired_height))

            elif topic == "frame.eye.0":
                recent_eye0 = np.frombuffer(msg["__raw_data__"][0], dtype=np.uint8).reshape(msg["height"], msg["width"], 3)
                if recent_eye0 is not None:
                    recent_eye0 = cv2.resize(recent_eye0, (desired_width, desired_height))

            elif topic == "frame.eye.1":
                recent_eye1 = np.frombuffer(msg["__raw_data__"][0], dtype=np.uint8).reshape(msg["height"], msg["width"], 3)
                if recent_eye1 is not None:
                    recent_eye1 = cv2.resize(recent_eye1, (desired_width, desired_height))

            elif topic.startswith("pupil."):
                print(f"Pupil data: {msg}")

        if recent_world is not None:
            cv2.imshow("World Camera", recent_world)
        if recent_eye0 is not None:
            recent_eye0_gray = cv2.cvtColor(recent_eye0, cv2.COLOR_BGR2GRAY)
            if "ellipse" in msg:
                ellipse = msg["ellipse"]
                center = tuple(map(int, ellipse["center"]))
                axes = tuple(map(int, ellipse["axes"]))
                angle = ellipse["angle"]
                cv2.ellipse(recent_eye0_gray, center, axes, angle, 0, 360, (0, 0, 255), 1)
            cv2.imshow("Eye Camera 0", recent_eye0_gray)
        if recent_eye1 is not None:
            cv2.imshow("Eye Camera 1", recent_eye1)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    pass
finally:
    cv2.destroyAllWindows()
