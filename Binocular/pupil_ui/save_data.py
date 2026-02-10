# import os
# import pandas as pd
# from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
# from openpyxl import load_workbook
# import time

# class save_data_thread(QThread):
#     path_signal = pyqtSignal()
#     def __init__(self, manage):
#         QThread.__init__(self)
#         self.manage = manage
#         self.data = None
#         self.data_file_path = None
#         self.frame_file_path = None
#         self.entire_count = 7
#         self.book = None  # 엑셀 파일 핸들링을 위한 변수
#         self.sheet = None
#         self.category = None
#         self.frame_no = None
#         self.stimuli_no = None
#         self.diameter_1 = None
#         self.diameter_2 = None
#         self.x_axis = None
#         self.y_axis = None

#     def __del__(self):
#         self.wait()

#     def run(self):
#         print("run save_data_Thread")
#         self.exec_()  # 이벤트 루프 시작

#     def make_path(self, info_data):
#         self.data = info_data
#         base_path = os.path.join(self.manage.hyperparameters.base_path, "Datas")
#         date_folder = os.path.join(base_path, self.data.get("date", ""))
#         name_folder = os.path.join(date_folder, self.data.get("name", ""))

#         current_time = time.strftime("%H-%M-%S")
#         time_folder = os.path.join(name_folder, current_time)
#         os.makedirs(time_folder, exist_ok=True)

#         file_name = self.data.get("name", "") + "_data.xlsx"
#         file_path = os.path.join(time_folder, file_name)

#         counter = 1
#         while os.path.exists(file_path):
#             file_name = self.data.get("name", "") + f"_data({counter}).xlsx"
#             file_path = os.path.join(time_folder, file_name)
#             counter += 1

#         self.data_file_path = file_path
#         self.frame_file_path = os.path.join(time_folder, "frames")
#         os.makedirs(self.frame_file_path, exist_ok=True)
#         #self.manage.save_frame_thread.img_base_path = self.frame_file_path

#         df = pd.DataFrame()
#         df.to_excel(self.data_file_path, index=False)
#         self.init_excel()    

#         print(f"Excel file created at: {self.data_file_path}")
#         self.path_signal.emit()

#     def init_excel(self):
#         self.open_book()
        
#         self.sheet['A1'] = "NAME"
#         self.sheet['A2'] = "AGE"
#         self.sheet['A3'] = "SEX"
#         self.sheet['A4'] = "MAJOR"
#         self.sheet['A5'] = "DATE"
        
#         self.sheet['B1'] = self.data.get('name', '')
#         self.sheet['B2'] = self.data.get('age', '')
#         self.sheet['B3'] = self.data.get('sex', '')
#         self.sheet['B4'] = self.data.get('major', '')
#         self.sheet['B5'] = self.data.get('date', '')

#         self.sheet['A7'] = 'CATEGORY'
#         self.sheet['B7'] = 'FRAME_NO'
#         self.sheet['C7'] = 'STIMULI_NO'
#         self.sheet['D7'] = 'DIAMETER_1'
#         self.sheet['E7'] = 'DIAMETER_2'
#         self.sheet['F7'] = 'X_AXIS'
#         self.sheet['G7'] = 'Y_AXIS'
#         self.sheet['H7'] = 'D_RATIO'

#         self.save_and_close_book()

#         print(f"Data written to Excel at: {self.data_file_path}")

#     def open_book(self):
#         """엑셀 파일 열기 및 시트 핸들링"""
#         self.book = load_workbook(self.data_file_path)
#         self.sheet = self.book.active

#     def save_and_close_book(self):
#         """엑셀 파일 저장 및 닫기"""
#         if self.book is not None:
#             self.book.save(self.data_file_path)
#             self.book.close()
#             self.book = None
#             self.sheet = None
#             print(f"Excel file saved and closed at: {self.data_file_path}")

#     def save_data_slot(self):
#         if self.manage.IsCapture:
#             if self.data_file_path != None and (self.book is None or self.sheet is None):
#                 self.open_book()  # 파일을 열고 sheet를 초기화
#             if self.sheet is None:
#                 print("Error: Sheet is None, cannot write data.")
#                 return
#             #print(f"{fframe.phase} {fframe.frame_count} saved {fframe.od_circles}")
            
#             self.entire_count += 1
#             self.sheet[f'A{self.entire_count}'] = self.category
#             self.sheet[f'B{self.entire_count}'] = self.frame_no
#             self.sheet[f'C{self.entire_count}'] = self.stimuli_no
#             self.sheet[f'D{self.entire_count}'] = self.diameter_1
#             self.sheet[f'E{self.entire_count}'] = self.diameter_2
#             self.sheet[f'F{self.entire_count}'] = self.x_axis
#             self.sheet[f'G{self.entire_count}'] = self.y_axis
        
#         else:
#             self.save_and_close_book()
#             self.book = None
#             self.data_file_path = None
#             # 만약 IsCapture가 False로 변경되면 파일 저장 후 닫기

import os
import csv
from PyQt5.QtCore import QThread, pyqtSignal
import time

class save_data_thread(QThread):
    path_signal = pyqtSignal()

    def __init__(self, manage):
        super().__init__()
        self.manage = manage
        self.data = None
        self.data_file_path = None
        self.frame_file_path = None
        self.entire_count = 7
        self.data_entries = []  # List to hold data entries
        self.category = None
        self.frame_no = None
        self.stimuli_no = None
        self.diameter_1 = None
        self.diameter_2 = None
        self.x_axis = None
        self.y_axis = None
        # eye1 params
        self.diameter_1_eye1 = None
        self.diameter_2_eye1 = None
        self.x_axis_eye1 = None
        self.y_axis_eye1 = None
        # calibration uses avg of eye0/eye1
        self.diameter_1_avg = None
        self.x_axis_avg = None
        self.y_axis_avg = None
        # diameters for calibration/table: [base, min, max]
        self.diameters = [[], [], []]          # avg (backward compatible)
        self.diameters_eye0 = [[], [], []]
        self.diameters_eye1 = [[], [], []]
        self.d_ratio = -1
        self.d_ratio_eye1 = -1
        self.base = []
        self.base_min_max_mean = [-1, -1, -1]

    def __del__(self):
        self.wait()

    def run(self):
        print("run SaveDataThread")
        self.exec_()  # Start the event loop

    def make_path(self, info_data):
        self.data = info_data
        base_path = os.path.join(self.manage.hyperparameters.base_path, "Datas")
        date_folder = os.path.join(base_path, self.data.get("date", ""))
        name_folder = os.path.join(date_folder, self.data.get("name", ""))

        current_time = time.strftime("%H-%M-%S")
        time_folder = os.path.join(name_folder, current_time)
        os.makedirs(time_folder, exist_ok=True)
        self.manage.monitor_1_ui.csv_path = time_folder

        file_name = self.data.get("name", "") + "_data.csv"
        file_path = os.path.join(time_folder, file_name)

        counter = 1
        while os.path.exists(file_path):
            file_name = self.data.get("name", "") + f"_data({counter}).csv"
            file_path = os.path.join(time_folder, file_name)
            counter += 1

        self.data_file_path = file_path
        self.frame_file_path = os.path.join(time_folder, "frames")
        os.makedirs(self.frame_file_path, exist_ok=True)
        # self.manage.save_frame_thread.img_base_path = self.frame_file_path

        # Initialize the CSV file with headers
        self.init_csv()

        print(f"CSV file created at: {self.data_file_path}")
        self.path_signal.emit()

    def init_csv(self):
        # Create the CSV file and write initial headers and data
        with open(self.data_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Write initial information in separate rows
            writer.writerow(["NAME",self.data.get('name', '')])
            writer.writerow(["AGE",self.data.get('age', '')])
            writer.writerow(["SEX",self.data.get('sex', '')])
            writer.writerow(["MAJOR",self.data.get('major', '')])
            writer.writerow(["DATE",self.data.get('date', '')])
            # Write headers for the data entries
            writer.writerow(['CATEGORY', 'FRAME_NO', 'STIMULI_NO', 'DIAMETER_1_EYE0', 'DIAMETER_2_EYE0', 'X_AXIS_EYE0', 'Y_AXIS_EYE0', 'D_RATIO_EYE0', '', 'DIAMETER_1_EYE1', 'DIAMETER_2_EYE1', 'X_AXIS_EYE1', 'Y_AXIS_EYE1', 'D_RATIO_EYE1'])

        print(f"Initial data written to CSV at: {self.data_file_path}")

    def save_data_slot(self):
        """Write one row immediately.

        The previous implementation buffered rows and only flushed when
        manage.IsCapture became False, which often meant nothing was saved.
        """
        if not self.manage.IsCapture:
            return
        if not self.data_file_path:
            return

        row = [
            self.category,
            self.frame_no,
            self.stimuli_no,
            # eye0
            self.diameter_1,
            self.diameter_2,
            self.x_axis,
            self.y_axis,
            self.d_ratio,
            # gap (11 cols)
            "", 
            # eye1
            self.diameter_1_eye1,
            self.diameter_2_eye1,
            self.x_axis_eye1,
            self.y_axis_eye1,
            self.d_ratio_eye1,
        ]

        try:
            with open(self.data_file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(row)
        except Exception as e:
            print(f"[save_data] Failed to append row: {e}")

    def append_data_to_csv(self):
        if self.data_entries:
            # Append data to the existing CSV file
            with open(self.data_file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                # Write data entries
                writer.writerows(self.data_entries)
            self.data_entries = []  # Clear the list after saving
            print(f"Data appended to CSV at: {self.data_file_path}")

    def infomation_slot(self):
        # Common meta
        self.category = self.manage.current_phase
        self.frame_no = self.manage.current_frame_no
        self.stimuli_no = self.manage.stimuli_no

        # ---- eye0 (kept as the primary columns for backward compatibility) ----
        self.diameter_1 = self.manage.capture_thread.frame_diameter[1]
        self.diameter_2 = self.manage.capture_thread.frame_diameter[0]
        self.x_axis = self.manage.capture_thread.frame_axis[0]
        self.y_axis = self.manage.capture_thread.frame_axis[1]

        # ---- eye1 ----
        self.diameter_1_eye1 = self.manage.capture_thread.frame_diameter_1[1]
        self.diameter_2_eye1 = self.manage.capture_thread.frame_diameter_1[0]
        self.x_axis_eye1 = self.manage.capture_thread.frame_axis_1[0]
        self.y_axis_eye1 = self.manage.capture_thread.frame_axis_1[1]

        # ---- calibration uses average of (eye0, eye1) ----
        # if one eye is missing (0), fall back to the other
        def _avg_or_fallback(a, b):
            a_ok = (a is not None) and (a != 0)
            b_ok = (b is not None) and (b != 0)
            if a_ok and b_ok:
                return (a + b) / 2.0
            if a_ok:
                return float(a)
            if b_ok:
                return float(b)
            return 0.0

        self.diameter_1_avg = _avg_or_fallback(self.diameter_1, self.diameter_1_eye1)
        self.x_axis_avg = _avg_or_fallback(self.x_axis, self.x_axis_eye1)
        self.y_axis_avg = _avg_or_fallback(self.y_axis, self.y_axis_eye1)

        test = self.manage.monitor_2_ui.index
        if test in [3, 4, 6]:
            i = test // 2 - 1
            # avg (used by UI/table calibration)
            self.diameters[i].append([self.diameter_1_avg, self.x_axis_avg, self.y_axis_avg])
            # per-eye (for separate tables)
            self.diameters_eye0[i].append([self.diameter_1, self.x_axis, self.y_axis])
            self.diameters_eye1[i].append([self.diameter_1_eye1, self.x_axis_eye1, self.y_axis_eye1])

        # D-Ratio based on BASE_AVG (avg of both eyes)
        if self.base_min_max_mean[2] != -1 and self.base_min_max_mean[2] != 0:
            self.d_ratio = (float(self.diameter_1) / float(self.base_min_max_mean[2])) * 100.0
            self.d_ratio_eye1 = (float(self.diameter_1_eye1) / float(self.base_min_max_mean[2])) * 100.0

        self.save_data_slot()
        