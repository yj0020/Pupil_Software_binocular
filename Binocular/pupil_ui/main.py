import sys
import queue
import cv2
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, QObject

import monitor_1
import monitor_2
import capture
from HyperParameters import HyperParameters
import save_data
import happy


class ManageProgram(QObject):
    start_detector_signal = pyqtSignal()
    stop_detector_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.hyperparameters = HyperParameters()
        self.stimuli_no = None
        self.current_phase = None
        self.current_frame_no = 0

        # queue init
        self.person_info_q = queue.Queue()

        self.monitor_1_ui = monitor_1.Monitor_1_ui(self)
        self.monitor_2_ui = monitor_2.Monitor_2_ui(self)

        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

        self.IsCapture = False

        # capture thread (binocular-capable)
        self.capture_thread = capture.CaptureThread(self)
        self.capture_thread.daemon = True
        self.capture_thread.start()

        self.happy_thread = happy.HappyThread(self)
        self.happy_thread.daemon = True
        self.happy_thread.start()

        self.save_data_thread = save_data.save_data_thread(self)
        self.save_data_thread.daemon = True
        self.save_data_thread.start()

        self.screen_height = 1920
        self.screen_width = 1080

        self.monitor_2_ui.put_person_info_q_signal.connect(self.get_person_info_q_slot)
        self.monitor_2_ui.start_capture_signal.connect(self.start_capture_slot)
        self.monitor_2_ui.stop_capture_signal.connect(self.stop_capture_slot)
        self.monitor_1_ui.abort_signal.connect(self.monitor_2_ui.handle_abort_slot)

        self.capture = []

        self.monitor_2_ui.end_signal.connect(self.end_slot)
        self.save_data_thread.path_signal.connect(self.path_slot)
        self.capture_thread.save_frame_signal.connect(self.frame_slot)
        self.capture_thread.save_information_signal.connect(self.save_data_thread.infomation_slot)
        self.capture_thread.save_information_signal.connect(self.happy_thread.save_image)
        self.capture_thread.save_information_signal.connect(self.monitor_1_ui.set_text)

    def start_capture_slot(self):
        print("capture_start")
        self.capture_thread.frame_count = 0
        self.capture_thread.isCaptured = True
        self.IsCapture = True

    def stop_capture_slot(self):
        print("capture_stop")
        print(f"frame_count = {self.capture_thread.frame_count}")
        if self.current_phase == "No Capture" or self.current_phase is None:
            self.current_phase = "No Capture"
        self.capture_thread.isCaptured = False
        if self.monitor_2_ui.index == 6:
            self.monitor_1_ui.table_print()

    def frame_slot(self):
        # show eye0 diameter by default (keep existing UI semantics)
        self.monitor_1_ui.Diameter_output.setText("{:.1f}".format(self.capture_thread.frame_diameter[1]))

    def end_slot(self):
        self.capture_thread.isCaptured = False
        self.IsCapture = False
        self.save_data_thread.save_data_slot()
        self.stimuli_no = None
        self.current_phase = None
        self.current_frame_no = 0
        self.save_data_thread.diameters = [[], [], []]
        self.capture_thread.last_frame_time = 0
        self.save_data_thread.d_ratio = -1
        self.save_data_thread.base = []
        self.base_min_max_mean = [-1, -1, -1]

    def path_slot(self):
        # base paths (per-eye subdirs are created by saving threads)
        self.capture_thread.ellipse_path = self.save_data_thread.frame_file_path + "/gt"
        self.capture_thread.original_path = self.save_data_thread.frame_file_path + "/original"
        self.save_data_thread.entire_count = 7

        # also used by monitor_1 to write table.csv
        self.monitor_1_ui.csv_path = self.save_data_thread.frame_file_path

    def get_person_info_q_slot(self):
        self.monitor_1_ui.data = self.person_info_q.get_nowait()
        self.monitor_1_ui.Name_Input.setText(self.monitor_1_ui.data.get("name", ""))
        self.monitor_1_ui.Age_Input.setText(self.monitor_1_ui.data.get("age", ""))
        self.monitor_1_ui.Sex_Input.setText(self.monitor_1_ui.data.get("sex", ""))
        self.monitor_1_ui.Major_Input.setText(self.monitor_1_ui.data.get("major", ""))
        self.monitor_1_ui.Date_Input.setText(self.monitor_1_ui.data.get("date", ""))
        self.save_data_thread.make_path(self.monitor_1_ui.data)
        self.save_data_thread.entire_count = 7

    def set_resolution(self, cap):
        width = 640
        height = 480
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print(f"Resolution requested: {width}x{height}, actual: {actual_width}x{actual_height}")
        self.screen_width = actual_width
        self.screen_height = actual_height


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    program_start = ManageProgram()
    sys.exit(app.exec_())
