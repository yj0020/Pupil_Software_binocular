from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtSlot
import os
import random
from datetime import datetime
from HyperParameters import HyperParameters
import numpy as np
import cv2


def _extract_image_index(filename: str):
    """Extract integer index from names like NEG1.jpg / POS15.jpg."""
    try:
        base = os.path.splitext(os.path.basename(filename))[0]
        digits = ""
        for ch in reversed(base):
            if ch.isdigit():
                digits = ch + digits
            else:
                break
        return int(digits) if digits else None
    except Exception:
        return None


def _resolve_neg_pos_path(base_dir: str, filename: str):
    """NEG/POS: 1~15 -> high/, 16~ -> low/"""
    idx = _extract_image_index(filename)
    if idx is None:
        return os.path.join(base_dir, filename)
    sub = "high" if 1 <= idx <= 15 else "low"
    return os.path.join(base_dir, sub, filename)

class Monitor_2_ui(QtWidgets.QWidget):
    put_person_info_q_signal = pyqtSignal()
    start_capture_signal = pyqtSignal()
    stop_capture_signal = pyqtSignal()
    #begin_signal = pyqtSignal()
    end_signal = pyqtSignal()

    def __init__(self, manage):
        super().__init__()
        self.manage = manage
        self.hyperparameters = HyperParameters()
        self.trial_count = 0
        self.trial = self.hyperparameters.Trial
        self.p1, self.p2, self.p3 = self.Random_phase()
        self.phase_measure_count = {"p1": 0, "p2": 0, "p3": 0}  # 각 phase 측정 카운트를 저장
        self.check_duplicate = []
        self._level_choice = {'NEG': None, 'POS': None}
        self.monitor_w = None
        self.monitor_h = None
        self.setupUi()
        self.show()
        self.isStart = False
        self.index = 0

    def setupUi(self):
        self.resize(1920, 1080)
        # self.showMaximized()

        self.stackedWidget = QtWidgets.QStackedWidget(self)
        self.stackedWidget.setGeometry(QtCore.QRect(0, 0, 1920, 1080))

        self.First_Page = QtWidgets.QWidget()
        self.First_Page.setStyleSheet("QWidget {\n"
                                      "    font-family: 'pretendard';\n"
        
                                      "    font-size: 20pt;\n"
                                      "     background-color: #FFFFFF; \n"
                                      "}\n"
                                      "QLineEdit {\n"
                                      "    background-color: #D9D9D9; \n"
                                      "}\n"
                                      "QPushButton {\n"
                                      "    background-color: #FFC8C8; \n"
                                      "    border: none;\n"
                                      "    border-radius: 11px;\n"
                                      "}")
        self.First_Page.setObjectName("First_Page")

        self.pushButton = QtWidgets.QPushButton(self.First_Page)
        self.pushButton.setGeometry(QtCore.QRect(589, 796, 794, 73))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText("START")

        self.Name_input_monitor2 = QtWidgets.QLineEdit(self.First_Page)
        self.Name_input_monitor2.setGeometry(QtCore.QRect(589, 327, 794, 73))
        self.Name_input_monitor2.setObjectName("Name_input_monitor2")

        self.Age_input_monitor2 = QtWidgets.QLineEdit(self.First_Page)
        self.Age_input_monitor2.setGeometry(QtCore.QRect(589, 430, 794, 73))
        self.Age_input_monitor2.setObjectName("Age_input_monitor2")

        self.Sex_input_monitor2 = QtWidgets.QLineEdit(self.First_Page)
        self.Sex_input_monitor2.setGeometry(QtCore.QRect(589, 533, 794, 73))
        self.Sex_input_monitor2.setObjectName("Sex_input_monitor2")

        self.Major_input_monitor2 = QtWidgets.QLineEdit(self.First_Page)
        self.Major_input_monitor2.setGeometry(QtCore.QRect(589, 636, 794, 73))
        self.Major_input_monitor2.setObjectName("Major_input_monitor2")

        self.label = QtWidgets.QLabel(self.First_Page)
        self.label.setGeometry(QtCore.QRect(494, 653, 59, 39))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.label.setText("전공")

        self.label_2 = QtWidgets.QLabel(self.First_Page)
        self.label_2.setGeometry(QtCore.QRect(494, 550, 59, 39))
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.label_2.setText("성별")

        self.label_3 = QtWidgets.QLabel(self.First_Page)
        self.label_3.setGeometry(QtCore.QRect(494, 447, 59, 39))
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.label_3.setText("연령")

        self.label_4 = QtWidgets.QLabel(self.First_Page)
        self.label_4.setGeometry(QtCore.QRect(494, 344, 59, 39))
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.label_4.setText("이름")

        self.stackedWidget.addWidget(self.First_Page)

        self.Calibration_Notice = QtWidgets.QWidget()
        self.Calibration_Notice.setStyleSheet("QWidget {\n"
                                              "    font-family: 'pretendard';\n"
                                              "    font-size: 20pt;\n"
                                              "     background-color: #FFFFFF; \n"
                                              "}\n"
                                              "QLabel {\n"
                                              "    background-color: #D9D9D9; \n"
                                              "}\n"
                                              "QPushButton {\n"
                                              "    background-color: #FFC8C8; \n"
                                              "    border: none;\n"
                                              "    border-radius: 11px;\n"
                                              "}")
        self.Calibration_Notice.setObjectName("Calibration_Notice")

        self.pushButton_2 = QtWidgets.QPushButton(self.Calibration_Notice)
        self.pushButton_2.setGeometry(QtCore.QRect(589, 796, 794, 73))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setText("NEXT")

        base_path = self.hyperparameters.base_path

        self.label_5 = QtWidgets.QLabel(self.Calibration_Notice)
        self.label_5.setGeometry(QtCore.QRect(234, 193, 1508, 542))
        self.label_5.setText("")
        self.label_5.setPixmap(QtGui.QPixmap(os.path.join(base_path, "Image", "calibration_notice.PNG")))
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.stackedWidget.addWidget(self.Calibration_Notice)

        self.Rest_1 = QtWidgets.QWidget()
        self.Rest_1.setStyleSheet("")
        self.Rest_1.setObjectName("Rest_1")
        self.label_6 = QtWidgets.QLabel(self.Rest_1)
        self.label_6.setGeometry(QtCore.QRect(0, 0, 1920, 1080))
        self.label_6.setText("")
        self.label_6.setPixmap(QtGui.QPixmap(os.path.join(base_path, "Image", "Rest.png")))
        self.label_6.setScaledContents(True)
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.stackedWidget.addWidget(self.Rest_1)

        self.Base_Measure = QtWidgets.QWidget()
        self.Base_Measure.setObjectName("Base_Measure")
        self.label_7 = QtWidgets.QLabel(self.Base_Measure)
        self.label_7.setGeometry(QtCore.QRect(0, 0, 1920, 1080))
        self.label_7.setText("")
        self.label_7.setPixmap(QtGui.QPixmap(os.path.join(base_path, "Image", "base_measure.png")))
        self.label_7.setScaledContents(True)
        self.label_7.setAlignment(QtCore.Qt.AlignCenter)
        self.label_7.setObjectName("label_7")
        self.stackedWidget.addWidget(self.Base_Measure)

        self.Min_Measure = QtWidgets.QWidget()
        self.Min_Measure.setObjectName("Min_Measure")
        self.label_8 = QtWidgets.QLabel(self.Min_Measure)
        self.label_8.setGeometry(QtCore.QRect(0, 0, 1920, 1080))
        self.label_8.setText("")
        self.label_8.setPixmap(QtGui.QPixmap(os.path.join(base_path, "Image", "min_measure.png")))
        self.label_8.setScaledContents(True)
        self.label_8.setAlignment(QtCore.Qt.AlignCenter)
        self.label_8.setObjectName("label_8")
        self.stackedWidget.addWidget(self.Min_Measure)

        self.Rest_2 = QtWidgets.QWidget()
        self.Rest_2.setObjectName("Rest_2")
        self.label_10 = QtWidgets.QLabel(self.Rest_2)
        self.label_10.setGeometry(QtCore.QRect(0, 0, 1920, 1080))
        self.label_10.setText("")
        self.label_10.setPixmap(QtGui.QPixmap(os.path.join(base_path, "Image", "Rest.png")))
        self.label_10.setScaledContents(True)
        self.label_10.setAlignment(QtCore.Qt.AlignCenter)
        self.label_10.setObjectName("label_10")
        self.stackedWidget.addWidget(self.Rest_2)

        self.Max_measure = QtWidgets.QWidget()
        self.Max_measure.setObjectName("Max_measure")
        self.label_9 = QtWidgets.QLabel(self.Max_measure)
        self.label_9.setGeometry(QtCore.QRect(0, 0, 1920, 1080))
        self.label_9.setText("")
        self.label_9.setPixmap(QtGui.QPixmap(os.path.join(base_path, "Image", "max_measure.png")))
        self.label_9.setAlignment(QtCore.Qt.AlignCenter)
        self.label_9.setObjectName("label_9")
        self.stackedWidget.addWidget(self.Max_measure)

        self.Experiment_Notice = QtWidgets.QWidget()
        self.Experiment_Notice.setStyleSheet("QWidget {\n"
                                             "    font-family: 'pretendard';\n"
                                             "    font-size: 20pt;\n"
                                             "     background-color: #FFFFFF; \n"
                                             "}\n"
                                             "QLabel {\n"
                                             "    background-color: #D9D9D9; \n"
                                             "}\n"
                                             "QPushButton {\n"
                                             "    background-color: #FFC8C8; \n"
                                             "    border: none;\n"
                                             "    border-radius: 11px;\n"
                                             "}")
        self.Experiment_Notice.setObjectName("Experiment_Notice")
        self.pushButton_3 = QtWidgets.QPushButton(self.Experiment_Notice)
        self.pushButton_3.setGeometry(QtCore.QRect(589, 796, 794, 73))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.setText("NEXT")

        self.label_11 = QtWidgets.QLabel(self.Experiment_Notice)
        self.label_11.setGeometry(QtCore.QRect(234, 193, 1508, 542))
        self.label_11.setText("")
        self.label_11.setPixmap(QtGui.QPixmap(os.path.join(base_path, "Image", "experiment_notice.PNG")))
        self.label_11.setScaledContents(False)
        self.label_11.setAlignment(QtCore.Qt.AlignCenter)
        self.label_11.setObjectName("label_11")
        self.stackedWidget.addWidget(self.Experiment_Notice)

        self.Rest3 = QtWidgets.QWidget()
        self.Rest3.setObjectName("Rest3")
        self.label_12 = QtWidgets.QLabel(self.Rest3)
        self.label_12.setGeometry(QtCore.QRect(0, 0, 1920, 1080))
        self.label_12.setText("")
        self.label_12.setPixmap(QtGui.QPixmap(os.path.join(base_path, "Image", "Rest.png")))
        self.label_12.setScaledContents(True)
        self.label_12.setAlignment(QtCore.Qt.AlignCenter)
        self.label_12.setObjectName("label_12")
        self.stackedWidget.addWidget(self.Rest3)

        self.Experience_Page_1 = QtWidgets.QWidget()
        self.Experience_Page_1.setObjectName("Experience_Page_1")
        self.label_13 = QtWidgets.QLabel(self.Experience_Page_1)
        self.label_13.setGeometry(QtCore.QRect(0, 0, 1920, 1080))
        self.label_13.setScaledContents(True)
        self.label_13.setAlignment(QtCore.Qt.AlignCenter)
        self.label_13.setObjectName("label_13")
        self.stackedWidget.addWidget(self.Experience_Page_1)

        self.Rest_4 = QtWidgets.QWidget()
        self.Rest_4.setObjectName("Rest_4")
        self.label_14 = QtWidgets.QLabel(self.Rest_4)
        self.label_14.setGeometry(QtCore.QRect(0, 0, 1920, 1080))
        self.label_14.setText("")
        self.label_14.setPixmap(QtGui.QPixmap(os.path.join(base_path, "Image", "Rest.png")))
        self.label_14.setScaledContents(True)
        self.label_14.setAlignment(QtCore.Qt.AlignCenter)
        self.label_14.setObjectName("label_14")
        self.stackedWidget.addWidget(self.Rest_4)

        # 새 페이지 추가 시작

        self.Experience_Page_2 = QtWidgets.QWidget()
        self.Experience_Page_2.setObjectName("Experience_Page_2")
        self.label_15 = QtWidgets.QLabel(self.Experience_Page_2)
        self.label_15.setGeometry(QtCore.QRect(0, 0, 1920, 1080))
        self.label_15.setScaledContents(True)
        self.label_15.setAlignment(QtCore.Qt.AlignCenter)
        self.label_15.setObjectName("label_15")
        self.stackedWidget.addWidget(self.Experience_Page_2)

        self.Rest_5 = QtWidgets.QWidget()
        self.Rest_5.setObjectName("Rest_5")
        self.label_17 = QtWidgets.QLabel(self.Rest_5)
        self.label_17.setGeometry(QtCore.QRect(0, 0, 1920, 1080))
        self.label_17.setText("")
        self.label_17.setPixmap(QtGui.QPixmap(os.path.join(base_path, "Image", "Rest.png")))
        self.label_17.setScaledContents(True)
        self.label_17.setAlignment(QtCore.Qt.AlignCenter)
        self.label_17.setObjectName("label_17")
        self.stackedWidget.addWidget(self.Rest_5)

        self.Experience_Page_3 = QtWidgets.QWidget()
        self.Experience_Page_3.setObjectName("Experience_Page_3")
        self.label_18 = QtWidgets.QLabel(self.Experience_Page_3)
        self.label_18.setGeometry(QtCore.QRect(0, 0, 1920, 1080))
        self.label_18.setScaledContents(True)
        self.label_18.setAlignment(QtCore.Qt.AlignCenter)
        self.label_18.setObjectName("label_18")
        self.stackedWidget.addWidget(self.Experience_Page_3)

        self.Rest_6 = QtWidgets.QWidget()
        self.Rest_6.setObjectName("Rest_6")
        self.label_19 = QtWidgets.QLabel(self.Rest_6)
        self.label_19.setGeometry(QtCore.QRect(0, 0, 1920, 1080))
        self.label_19.setText("")
        self.label_19.setPixmap(QtGui.QPixmap(os.path.join(base_path, "Image", "Rest.png")))
        self.label_19.setScaledContents(True)
        self.label_19.setAlignment(QtCore.Qt.AlignCenter)
        self.label_19.setObjectName("label_19")
        self.stackedWidget.addWidget(self.Rest_6)

        # 새 페이지 추가 끝

        self.Last_Page = QtWidgets.QWidget()
        self.Last_Page.setStyleSheet("QWidget {\n"
                                     "    font-family: 'pretendard';\n"
                                     "    font-size: 20pt;\n"
                                     "     background-color: #FFFFFF; \n"
                                     "}\n"
                                     "QLabel {\n"
                                     "    background-color: #D9D9D9; \n"
                                     "}\n"
                                     "QPushButton {\n"
                                     "    background-color: #FFC8C8; \n"
                                     "    border: none;\n"
                                     "    border-radius: 11px;\n"
                                     "}")
        self.Last_Page.setObjectName("Last_Page")
        self.pushButton_4 = QtWidgets.QPushButton(self.Last_Page)
        self.pushButton_4.setGeometry(QtCore.QRect(589, 796, 794, 73))
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.setText("FINISH")
        self.label_16 = QtWidgets.QLabel(self.Last_Page)
        self.label_16.setGeometry(QtCore.QRect(234, 193, 1508, 542))
        self.label_16.setText("")
        self.label_16.setPixmap(QtGui.QPixmap(os.path.join(base_path, "Image", "end_notice.PNG")))
        self.label_16.setAlignment(QtCore.Qt.AlignCenter)
        self.label_16.setObjectName("label_16")
        self.stackedWidget.addWidget(self.Last_Page)

        # QtCore.QMetaObject.connectSlotsByName(self)
        # self.setCentralWidget(self.stackedWidget)

        self.timer = QtCore.QTimer(self)  # QTimer 객체 생성
        self.timer.timeout.connect(self.go_to_next_page_auto)

        self.pushButton.clicked.connect(self.send_info_data_to_queue)
        self.pushButton_2.clicked.connect(self.calibration_notice_to_rest_1)
        self.pushButton_3.clicked.connect(self.experiment_notice_to_rest_3)
        self.pushButton_4.clicked.connect(self.finish_operation)

        self.set_timer_for_page(self.stackedWidget.currentIndex())

    def resizeEvent(self, event):
        size = self.size()
        self.monitor_w = size.width()
        self.monitor_h = size.height()
        print(f"Monitor Width: {self.monitor_w}, Monitor Height: {self.monitor_h}")
        super().resizeEvent(event)

    def send_info_data_to_queue(self):
        name = self.Name_input_monitor2.text()
        age = self.Age_input_monitor2.text()
        sex = self.Sex_input_monitor2.text()
        major = self.Major_input_monitor2.text()
        now = datetime.now()
        date = str(now.date())
        data = {
            "name": name,
            "age": age,
            "sex": sex,
            "major": major,
            "date": date
        }

        if all(data.values()):
            self.manage.person_info_q.put_nowait(data)
            self.put_person_info_q_signal.emit()
            self.first_page_to_calibration_notice()
        else:
            print("All fields must be filled")

    def start_timer(self, duration):
        # print(f"Starting timer with duration: {duration}")  # 디버깅용 출력
        self.timer.start(duration)

    def stop_timer(self):
        # print("Stopping timer")  # 디버깅용 출력
        self.timer.stop()

    def go_to_next_page_auto(self):
        current_index = self.stackedWidget.currentIndex()

        if current_index == 2:
            self.rest_1_to_base_measure()
        elif current_index == 3:
            self.base_measure_to_min_measure()
        elif current_index == 4:
            self.min_measure_to_rest_2()
        elif current_index == 5:
            self.rest_2_to_max_measure()
        elif current_index == 6:
            self.max_measure_to_experiment_notice()
        elif current_index == 8:
            self.rest_3_to_experience_page_1()
        elif current_index == 9:
            self.experience_page_1_to_rest_4()
        elif current_index == 10:
            trial_result = self.check_trial()
            print(f"Check trial result (from Rest 4): {trial_result}")
            if trial_result:
                self.rest_4_to_experience_page_2()
            else:
                self.rest_4_to_experience_page_1()
        elif current_index == 11:
            self.experience_page_2_to_rest_5()
        elif current_index == 12:
            trial_result = self.check_trial()
            print(f"Check trial result (from Rest 5): {trial_result}")
            if trial_result:
                self.rest_5_to_experience_page_3()
            else:
                self.rest_5_to_experience_page_2()
        elif current_index == 13:
            self.experience_page_3_to_rest_6()
        elif current_index == 14:
            trial_result = self.check_trial()
            print(f"Check trial result (from Rest 6): {trial_result}")
            if trial_result:
                self.rest_6_to_last()
            else:
                self.rest_6_to_experience_page_3()

    def first_page_to_calibration_notice(self):
        # print("Moving from First_Page to Calibration_Notice")
        self.manage.current_frame_no = 0
        self.index = 1
        self.stackedWidget.setCurrentIndex(self.index)
        #self.manage.save_data_thread.open_book()
        self.manage.current_phase = 'No Capture'
        self.set_timer_for_page(self.index)
        self.isStart = True

    def calibration_notice_to_rest_1(self):
        # print("Moving from Calibration_Notice to Rest_1")
        self.manage.current_frame_no = 0
        self.index = 2
        self.stackedWidget.setCurrentIndex(self.index)
        self.set_timer_for_page(self.index)

    def rest_1_to_base_measure(self):
        # print("Moving from Rest_1 to Base_Measure")
        self.manage.current_frame_no = 0
        self.index = 3
        self.stackedWidget.setCurrentIndex(self.index)
        self.manage.current_phase = 'BASE'
        self.manage.stimuli_no = "GREY"
        print(self.manage.current_phase)
        self.start_capture_signal.emit()
        self.set_timer_for_page(self.index)

    def base_measure_to_min_measure(self):
        # print("Moving from Base_Measure to Min_Measure")
        # Compute BASE stats per eye (for table.csv) and averaged BASE stats (for D-Ratio).
        sdt = self.manage.save_data_thread
        base0 = self.manage.monitor_1_ui.min_max_mean_eye(idx=0, eye=0)
        base1 = self.manage.monitor_1_ui.min_max_mean_eye(idx=0, eye=1)
        sdt.base_min_max_mean_eye0 = base0
        sdt.base_min_max_mean_eye1 = base1
        sdt.base_min_max_mean = (
            (base0[0] + base1[0]) / 2.0,
            (base0[1] + base1[1]) / 2.0,
            (base0[2] + base1[2]) / 2.0,
        )
        self.manage.current_frame_no = 0
        self.index = 4
        self.stackedWidget.setCurrentIndex(self.index)
        self.manage.current_phase = 'MIN'
        self.manage.stimuli_no = "WHITE"
        print(self.manage.current_phase)
        self.start_capture_signal.emit()
        self.set_timer_for_page(self.index)

    def min_measure_to_rest_2(self):
        self.manage.current_frame_no = 0
        self.stop_capture_signal.emit()
        # self.manage.monitor_1_ui.Frame_No_output.setText("No Capture")
        self.index = 5
        self.stackedWidget.setCurrentIndex(self.index)
        self.set_timer_for_page(self.index)

    def rest_2_to_max_measure(self):
        self.manage.current_frame_no = 0
        self.index = 6
        self.stackedWidget.setCurrentIndex(self.index)
        self.manage.current_phase = 'MAX'
        self.manage.stimuli_no = "BLACK"
        self.start_capture_signal.emit()
        print(self.manage.current_phase)

        #self.start_capture_signal.emit()
        self.set_timer_for_page(self.index)

    def max_measure_to_experiment_notice(self):
        self.manage.monitor_1_ui.Frame_No_output.setText("No Capture")
        self.stop_capture_signal.emit()
        self.manage.current_frame_no = 0
        # print("Moving from Max_measure to Experiment_Notice")
        self.index = 7
        self.stackedWidget.setCurrentIndex(self.index)
        self.manage.current_phase = 'No Capture'
        self.set_timer_for_page(self.index)

    def experiment_notice_to_rest_3(self):
        self.manage.current_frame_no = 0
        self.stop_capture_signal.emit()
        self.manage.monitor_1_ui.Frame_No_output.setText("No Capture")
        print("Moving from Experiment_Notice to Rest3")
        self.index = 8
        self.stackedWidget.setCurrentIndex(self.index)

        self.set_timer_for_page(self.index)

    def rest_3_to_experience_page_1(self):
        self.manage.current_frame_no = 0
        print("Moving from Rest3 to Experience_Page_1")
        self.index = 9
        self.display_random_image(1)
        self.phase_measure_count['p1'] += 1
        self.stackedWidget.setCurrentIndex(self.index)
        self.manage.current_phase = f"{self.p1}_{self.phase_measure_count['p1']}"
        self.manage.stimuli_no = self.p1_selected_image
        self.start_capture_signal.emit()
        print(self.manage.current_phase)
        #self.start_capture_signal.emit()
        self.set_timer_for_page(self.index)

    def experience_page_1_to_rest_4(self):
        self.manage.current_frame_no = 0
        self.stop_capture_signal.emit()
        self.manage.monitor_1_ui.Frame_No_output.setText("No Capture")
        print("Moving from Experience_Page_1 to Rest_4")
        self.stackedWidget.setCurrentIndex(10)
        print(self.manage.current_phase)
        #self.start_capture_signal.emit()
        self.set_timer_for_page(10)

    def rest_4_to_experience_page_1(self):
        self.manage.current_frame_no = 0
        print("Moving from Rest_4 to Experience_Page_1")
        self.index = 9
        self.display_random_image(1)
        self.phase_measure_count['p1'] += 1
        self.stackedWidget.setCurrentIndex(self.index)
        self.manage.current_phase = f"{self.p1}_{self.phase_measure_count['p1'] }"
        self.manage.stimuli_no = self.p1_selected_image
        self.start_capture_signal.emit()
        print(self.manage.current_phase)
        #self.start_capture_signal.emit()
        self.set_timer_for_page(self.index)

    def rest_4_to_experience_page_2(self):
        self.manage.current_frame_no = 0
        print("Moving from Rest_4 to Experience_Page_2")
        self.index = 11
        self.display_random_image(2)
        self.phase_measure_count['p2'] += 1
        self.stackedWidget.setCurrentIndex(self.index)
        self.manage.current_phase = f"{self.p2}_{self.phase_measure_count['p2'] }"
        self.manage.stimuli_no = self.p2_selected_image
        self.start_capture_signal.emit()
        print(self.manage.current_phase)
        #self.start_capture_signal.emit()
        self.set_timer_for_page(self.index)

    def experience_page_2_to_rest_5(self):
        self.manage.current_frame_no = 0
        self.stop_capture_signal.emit()
        self.manage.monitor_1_ui.Frame_No_output.setText("No Capture")
        print("Moving from Experience_Page_2 to Rest_5")
        self.index = 12
        self.stackedWidget.setCurrentIndex(self.index)
        print(self.manage.current_phase)
        #self.start_capture_signal.emit()
        self.set_timer_for_page(self.index)

    def rest_5_to_experience_page_2(self):
        self.manage.current_frame_no = 0
        print("Moving from Rest_5 to Experience_Page_2")
        self.index = 11
        self.display_random_image(2)
        self.phase_measure_count['p2'] += 1
        self.stackedWidget.setCurrentIndex(self.index)
        self.manage.current_phase = f"{self.p2}_{self.phase_measure_count['p2']}"
        self.manage.stimuli_no = self.p2_selected_image
        self.start_capture_signal.emit()
        print(self.manage.current_phase)
        #self.start_capture_signal.emit()
        self.set_timer_for_page(self.index)

    def rest_5_to_experience_page_3(self):
        self.manage.current_frame_no = 0
        print("Moving from Rest_5 to Experience_Page_3")
        self.index = 13
        self.display_random_image(3)
        self.phase_measure_count['p3'] += 1
        self.stackedWidget.setCurrentIndex(self.index)
        self.manage.current_phase = f"{self.p3}_{self.phase_measure_count['p3']}"
        self.manage.stimuli_no = self.p3_selected_image
        self.start_capture_signal.emit()
        print(self.manage.current_phase)
        #self.start_capture_signal.emit()
        self.set_timer_for_page(self.index)

    def experience_page_3_to_rest_6(self):
        self.manage.current_frame_no = 0
        self.stop_capture_signal.emit()
        self.manage.monitor_1_ui.Frame_No_output.setText("No Capture")
        self.manage.current_phase = 'No Capture'
        print("Moving from Experience_Page_3 to Rest_6")
        self.index = 14
        self.stackedWidget.setCurrentIndex(self.index)
        print(self.manage.current_phase)
        #self.start_capture_signal.emit()
        self.set_timer_for_page(self.index)

    def rest_6_to_experience_page_3(self):
        self.manage.current_frame_no = 0
        print("Moving from Rest_6 to Experience_Page_3")
        self.index = 13
        self.display_random_image(3)
        self.phase_measure_count['p3'] += 1
        self.stackedWidget.setCurrentIndex(self.index)
        self.manage.current_phase = f"{self.p3}_{self.phase_measure_count['p3']}"
        self.manage.stimuli_no = self.p3_selected_image
        self.start_capture_signal.emit()
        #self.start_capture_signal.emit()
        self.set_timer_for_page(self.index)
        

    def rest_6_to_last(self):
        self.stop_capture_signal.emit()
        self.manage.current_frame_no = 0
        self.manage.monitor_1_ui.Frame_No_output.setText("No Capture")
        print("Moving from Rest_6 to Last_Page")
        self.index = 15
        self.stackedWidget.setCurrentIndex(self.index)
        self.manage.current_phase = 'No Capture'
        self.set_timer_for_page(self.index)

    def check_trial(self):
        if self.trial_count < self.trial - 1:
            self.trial_count += 1
            return False
        else:
            self.trial_count = 0
            return True

    def set_timer_for_page(self, page_index):
        print(f"Setting timer for page {page_index}")  # 디버깅용 출력
        if page_index in [8, 10, 12, 14]:  # Rest 페이지
            duration = self.hyperparameters.Rest_time
        elif page_index in [9, 11, 13]:  # Min, Base, Max, Experience 페이지
            duration = self.hyperparameters.Calibration_time
        elif page_index in [2, 3, 4, 5, 6]:
            duration = self.hyperparameters.Start_time
        elif page_index in [8]:
            duration = self.hyperparameters.Ready_time
        else:
            #self.stop_capture_signal.emit()
            self.stop_timer()
            return
        self.start_timer(duration)

    def Random_phase(self):
        phase = ['NEG', 'POS', 'NEU']
        p1, p2, p3 = random.sample(phase, 3)
        return p1, p2, p3

    def finish_operation(self):
        self.reset_fields()
        self.index = 0
        self.stackedWidget.setCurrentIndex(self.index)  # 첫 번째 페이지로 이동
        self.trial_count = 0  # trial_count 초기화
        self.p1, self.p2, self.p3 = self.Random_phase()
        self.phase_measure_count = {"p1": 0, "p2": 0, "p3": 0}  # 측정 카운트 초기화
        self._level_choice = {'NEG': None, 'POS': None}
        self.manage.monitor_1_ui.abort_operation()
        self.check_duplicate.clear()
        self.end_signal.emit()

    def reset_fields(self):
        self.Name_input_monitor2.setText("")
        self.Age_input_monitor2.setText("")
        self.Sex_input_monitor2.setText("")
        self.Major_input_monitor2.setText("")
        # 필요 시 추가 초기화 로직

    def handle_abort_slot(self):
        self.stop_timer()  # 타이머 중지
        self.index = 0
        self.stackedWidget.setCurrentIndex(self.index)  # 첫 번째 페이지로 이동
        self.reset_fields()
        self.p1, self.p2, self.p3 = self.Random_phase()
        self.trial_count = 0  # trial_count 초기화
        self.phase_measure_count = {"p1": 0, "p2": 0, "p3": 0}  # 측정 카운트 초기화
        self._level_choice = {'NEG': None, 'POS': None}
        #self.check_duplicate.clear()
        self.end_signal.emit()


    def _choose_level_folder(self, emotion: str):
        """For NEG/POS, randomly choose 'high' or 'low' ONCE per run, then keep using it."""
        if emotion not in ("NEG", "POS"):
            return None
        if not hasattr(self, "_level_choice") or self._level_choice is None:
            self._level_choice = {"NEG": None, "POS": None}
        if self._level_choice.get(emotion) is None:
            self._level_choice[emotion] = random.choice(["high", "low"])
            print(f"[stim] {emotion} folder chosen -> {self._level_choice[emotion]}")
        return self._level_choice[emotion]

    def _list_stim_images(self, dir_path: str):
        """Return sorted list of image filenames in a directory."""
        try:
            files = [
                f for f in os.listdir(dir_path)
                if os.path.isfile(os.path.join(dir_path, f))
                and f.lower().endswith((".jpg", ".jpeg", ".png"))
            ]
        except Exception:
            return []
        files.sort()
        return files

    def _pick_unique_from_dir(self, dir_path: str):
        """Pick a non-duplicate image filename from a directory."""
        candidates = self._list_stim_images(dir_path)
        if not candidates:
            return None
        # Try up to N times to avoid duplicates
        for _ in range(len(candidates) * 2):
            fname = random.choice(candidates)
            if fname not in self.check_duplicate:
                self.check_duplicate.append(fname)
                return fname
        # If all are duplicates
        return None

    def select_random_image(self, exp):
        if exp == 1:
            if self.p1 == 'NEG':
                # Choose 'high' or 'low' once, then sample only within that folder
                base_dir = self.hyperparameters.NEG_Image_Base_Path
                level = self._choose_level_folder('NEG')
                p1_images_path = os.path.join(base_dir, level) if level else base_dir

                candidates = self._list_stim_images(p1_images_path)
                self.trial = len(candidates)

                p1_selected_image = self._pick_unique_from_dir(p1_images_path)
                if p1_selected_image is None:
                    print('No more unique images available in the folder.')
                    return None

                self.p1_selected_image = p1_selected_image
                p1_dir = os.path.join(p1_images_path, p1_selected_image)

            elif self.p1 == 'NEU':
                self.trial = len(self.hyperparameters.NEU_Images)
                p1_images_path = self.hyperparameters.NEU_Image_Base_Path

                p1_images = os.listdir(p1_images_path)

                for _ in range(len(p1_images)):
                    p1_selected_image = random.choice(p1_images)
                    if p1_selected_image not in self.check_duplicate:
                        self.check_duplicate.append(p1_selected_image)
                        self.p1_selected_image = p1_selected_image
                        p1_dir = os.path.join(p1_images_path, p1_selected_image)
                        break
                    else:
                        print("duplicate!! retry")
                else:
                    print("No more unique images available in the folder.")
                    return None

            elif self.p1 == 'POS':
                # Choose 'high' or 'low' once, then sample only within that folder
                base_dir = self.hyperparameters.POS_Image_Base_Path
                level = self._choose_level_folder('POS')
                p1_images_path = os.path.join(base_dir, level) if level else base_dir

                candidates = self._list_stim_images(p1_images_path)
                self.trial = len(candidates)

                p1_selected_image = self._pick_unique_from_dir(p1_images_path)
                if p1_selected_image is None:
                    print('No more unique images available in the folder.')
                    return None

                self.p1_selected_image = p1_selected_image
                p1_dir = os.path.join(p1_images_path, p1_selected_image)

            else:
                print("select_random_image_error_EXP1")
                return None

            return p1_dir

        elif exp == 2:
            if self.p2 == 'NEG':
                # Choose 'high' or 'low' once, then sample only within that folder
                base_dir = self.hyperparameters.NEG_Image_Base_Path
                level = self._choose_level_folder('NEG')
                p2_images_path = os.path.join(base_dir, level) if level else base_dir

                candidates = self._list_stim_images(p2_images_path)
                self.trial = len(candidates)

                p2_selected_image = self._pick_unique_from_dir(p2_images_path)
                if p2_selected_image is None:
                    print('No more unique images available in the folder.')
                    return None

                self.p2_selected_image = p2_selected_image
                p2_dir = os.path.join(p2_images_path, p2_selected_image)

            elif self.p2 == 'NEU':
                self.trial = len(self.hyperparameters.NEU_Images)
                p2_images_path = self.hyperparameters.NEU_Image_Base_Path

                p2_images = os.listdir(p2_images_path)

                for _ in range(len(p2_images)):
                    p2_selected_image = random.choice(p2_images)
                    if p2_selected_image not in self.check_duplicate:
                        self.check_duplicate.append(p2_selected_image)
                        self.p2_selected_image = p2_selected_image
                        p2_dir = os.path.join(p2_images_path, p2_selected_image)
                        break
                    else:
                        print("duplicate!! retry")
                else:
                    print("No more unique images available in the folder.")
                    return None

            elif self.p2 == 'POS':
                # Choose 'high' or 'low' once, then sample only within that folder
                base_dir = self.hyperparameters.POS_Image_Base_Path
                level = self._choose_level_folder('POS')
                p2_images_path = os.path.join(base_dir, level) if level else base_dir

                candidates = self._list_stim_images(p2_images_path)
                self.trial = len(candidates)

                p2_selected_image = self._pick_unique_from_dir(p2_images_path)
                if p2_selected_image is None:
                    print('No more unique images available in the folder.')
                    return None

                self.p2_selected_image = p2_selected_image
                p2_dir = os.path.join(p2_images_path, p2_selected_image)

            else:
                print("select_random_image_error_EXP2")
                return None

            return p2_dir

        elif exp == 3:
            if self.p3 == 'NEG':
                # Choose 'high' or 'low' once, then sample only within that folder
                base_dir = self.hyperparameters.NEG_Image_Base_Path
                level = self._choose_level_folder('NEG')
                p3_images_path = os.path.join(base_dir, level) if level else base_dir

                candidates = self._list_stim_images(p3_images_path)
                self.trial = len(candidates)

                p3_selected_image = self._pick_unique_from_dir(p3_images_path)
                if p3_selected_image is None:
                    print('No more unique images available in the folder.')
                    return None

                self.p3_selected_image = p3_selected_image
                p3_dir = os.path.join(p3_images_path, p3_selected_image)

            elif self.p3 == 'NEU':
                self.trial = len(self.hyperparameters.NEU_Images)
                p3_images_path = self.hyperparameters.NEU_Image_Base_Path

                p3_images = os.listdir(p3_images_path)

                for _ in range(len(p3_images)):
                    p3_selected_image = random.choice(p3_images)
                    if p3_selected_image not in self.check_duplicate:
                        self.check_duplicate.append(p3_selected_image)
                        self.p3_selected_image = p3_selected_image
                        p3_dir = os.path.join(p3_images_path, p3_selected_image)
                        break
                    else:
                        print("duplicate!! retry")
                else:
                    print("No more unique images available in the folder.")
                    return None

            elif self.p3 == 'POS':
                # Choose 'high' or 'low' once, then sample only within that folder
                base_dir = self.hyperparameters.POS_Image_Base_Path
                level = self._choose_level_folder('POS')
                p3_images_path = os.path.join(base_dir, level) if level else base_dir

                candidates = self._list_stim_images(p3_images_path)
                self.trial = len(candidates)

                p3_selected_image = self._pick_unique_from_dir(p3_images_path)
                if p3_selected_image is None:
                    print('No more unique images available in the folder.')
                    return None

                self.p3_selected_image = p3_selected_image
                p3_dir = os.path.join(p3_images_path, p3_selected_image)

            else:
                print("select_random_image_error_EXP3")
                return None

            return p3_dir


        else:
            print("select_random_image_error")

    def display_random_image(self, exp):
        image_path = self.select_random_image(exp)
        if image_path:
            pixmap = QtGui.QPixmap(image_path)
            if exp == 1:
                self.label_13.setPixmap(pixmap)
            elif exp == 2:
                self.label_15.setPixmap(pixmap)
            elif exp == 3:
                self.label_18.setPixmap(pixmap)
