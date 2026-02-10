from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtCore import pyqtSignal, Qt, QMutex
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QLabel
import numpy as np
import csv
import os


class WidgetScreen(QLabel):
    def __init__(self, parent=None):
        super(WidgetScreen, self).__init__(parent)
        self.image = None
        self.eyes = None
        self.circles = None
        self.screen_width = 640
        self.screen_height = 480
        self.mutex = QMutex()

    def setScreen(self, np_array):
        if np_array is None:
            return
        self.mutex.lock()
        try:
            height, width, n = np_array.shape
            bytes_per_line, _, _ = np_array.strides
            self.image = QImage(
                np_array.data.tobytes(),
                width,
                height,
                bytes_per_line,
                QtGui.QImage.Format_BGR888
            )
            self.image.scaledToWidth(self.width())
            self.update()
        finally:
            self.mutex.unlock()

    def setEyes(self, w, h, eye_list):
        self.eyes = eye_list
        self.screen_width = w
        self.screen_height = h
        self.update()

    def setCircles(self, w, h, circles):
        self.circles = circles
        self.screen_width = w
        self.screen_height = h
        self.update()

    def resetEyes(self):
        self.eyes = None
        self.update()

    def paintEvent(self, event):
        self.mutex.lock()
        try:
            painter = QPainter(self)
            ratio_width = float(self.width()) / float(self.screen_width)
            ratio_height = float(self.height()) / float(self.screen_height)

            if self.image is not None:
                painter.drawImage(0, 0, self.image)
                pen = QtGui.QPen(QtCore.Qt.white)
                painter.setPen(pen)

                if self.eyes is not None:
                    for eye in self.eyes:
                        x = int(eye[0] * ratio_width)
                        y = int(eye[1] * ratio_height)
                        w = int(eye[2] * ratio_width)
                        h = int(eye[3] * ratio_height)
                        painter.drawRect(x, y, w, h)

                if self.circles is not None:
                    red_pen = QtGui.QPen(QtCore.Qt.red)
                    painter.setPen(red_pen)
                    for circle in self.circles:
                        x = int(circle[0] * ratio_width)
                        y = int(circle[1] * ratio_height)
                        r1 = int(circle[2] * ratio_width)
                        r2 = int(circle[3] * ratio_height)
                        painter.drawEllipse(x - r1, y - r2, r1 * 2, r2 * 2)
                    painter.setPen(pen)
            else:
                super(WidgetScreen, self).paintEvent(event)
        finally:
            self.mutex.unlock()


class Monitor_1_ui(QtWidgets.QWidget):
    abort_signal = pyqtSignal()

    def __init__(self, manage):
        super().__init__()
        self.manage = manage
        self.setupUi()
        self.show()
        self.screen_width = 1920
        self.screen_height = 1080
        self.stddev = self.manage.hyperparameters.stddev
        self.csv_path = None
        
        self.Frame_No.hide()
        self.Frame_No_output.hide()
        self.Diameter.hide()
        self.Diameter_output.hide()

    def setupUi(self):
        self.setGeometry(100, 100, 1920, 1080)
        self.setStyleSheet("QWidget { background-color: #FFFFFF; }")
        


        # Two-row camera view: eye0 (top) + eye1 (bottom)
        top_y = 40
        gap = 20
        self.Camera_view0 = WidgetScreen(self)
        self.Camera_view0.setGeometry(QtCore.QRect(199, top_y, 640, 480))
        self.Camera_view0.setAlignment(QtCore.Qt.AlignCenter)
        self.Camera_view0.setObjectName("Camera_view0")

        self.Camera_view1 = WidgetScreen(self)
        self.Camera_view1.setGeometry(QtCore.QRect(199, top_y + 480 + gap, 640, 480))
        self.Camera_view1.setAlignment(QtCore.Qt.AlignCenter)
        self.Camera_view1.setObjectName("Camera_view1")

        # Labels
        self.Name = QtWidgets.QLabel(self)
        self.Name.setGeometry(QtCore.QRect(1120, 160, 60, 40))
        self.Name.setAlignment(QtCore.Qt.AlignCenter)
        self.Name.setText("Name")
        self.Name.raise_()

        self.Age = QtWidgets.QLabel(self)
        self.Age.setGeometry(QtCore.QRect(1120, 260, 60, 40))
        self.Age.setAlignment(QtCore.Qt.AlignCenter)
        self.Age.setText("Age")
        self.Age.raise_()

        self.Sex = QtWidgets.QLabel(self)
        self.Sex.setGeometry(QtCore.QRect(1120, 360, 60, 40))
        self.Sex.setAlignment(QtCore.Qt.AlignCenter)
        self.Sex.setText("Sex")
        self.Sex.raise_()

        self.Major = QtWidgets.QLabel(self)
        self.Major.setGeometry(QtCore.QRect(1120, 460, 60, 40))
        self.Major.setAlignment(QtCore.Qt.AlignCenter)
        self.Major.setText("Major")
        self.Major.raise_()

        self.Date = QtWidgets.QLabel(self)
        self.Date.setGeometry(QtCore.QRect(1120, 560, 60, 40))
        self.Date.setAlignment(QtCore.Qt.AlignCenter)
        self.Date.setText("Date")
        self.Date.raise_()

        self.Frame_No = QtWidgets.QLabel(self)
        self.Frame_No.setGeometry(QtCore.QRect(200, 870, 280, 70))
        self.Frame_No.setAlignment(QtCore.Qt.AlignCenter)
        self.Frame_No.setText("Frame_No")
        self.Frame_No.raise_()

        self.Frame_No_output = QtWidgets.QLabel(self)
        self.Frame_No_output.setGeometry(QtCore.QRect(480, 870, 280, 70))
        self.Frame_No_output.setAlignment(QtCore.Qt.AlignCenter)
        self.Frame_No_output.setText("No Capture")
        self.Frame_No_output.raise_()

        self.Diameter = QtWidgets.QLabel(self)
        self.Diameter.setGeometry(QtCore.QRect(200, 940, 280, 70))
        self.Diameter.setAlignment(QtCore.Qt.AlignCenter)
        self.Diameter.setText("Diameter (eye0)")
        self.Diameter.raise_()

        self.Diameter_output = QtWidgets.QLabel(self)
        self.Diameter_output.setGeometry(QtCore.QRect(480, 940, 280, 70))
        self.Diameter_output.setAlignment(QtCore.Qt.AlignCenter)
        self.Diameter_output.setText("Diameter_output")
        self.Diameter_output.raise_()

        # Inputs
        self.Name_Input = QtWidgets.QLabel(self)
        self.Name_Input.setGeometry(QtCore.QRect(1217, 140, 284, 73))
        self.Name_Input.setStyleSheet("QLabel { background-color: #D9D9D9; }")
        self.Name_Input.setAlignment(QtCore.Qt.AlignCenter)
        self.Name_Input.raise_()

        self.Age_Input = QtWidgets.QLabel(self)
        self.Age_Input.setGeometry(QtCore.QRect(1217, 243, 284, 73))
        self.Age_Input.setStyleSheet("QLabel { background-color: #D9D9D9; }")
        self.Age_Input.setAlignment(QtCore.Qt.AlignCenter)
        self.Age_Input.raise_()

        self.Sex_Input = QtWidgets.QLabel(self)
        self.Sex_Input.setGeometry(QtCore.QRect(1217, 346, 284, 73))
        self.Sex_Input.setStyleSheet("QLabel { background-color: #D9D9D9; }")
        self.Sex_Input.setAlignment(QtCore.Qt.AlignCenter)
        self.Sex_Input.raise_()

        self.Major_Input = QtWidgets.QLabel(self)
        self.Major_Input.setGeometry(QtCore.QRect(1217, 449, 284, 73))
        self.Major_Input.setStyleSheet("QLabel { background-color: #D9D9D9; }")
        self.Major_Input.setAlignment(QtCore.Qt.AlignCenter)
        self.Major_Input.raise_()

        self.Date_Input = QtWidgets.QLabel(self)
        self.Date_Input.setGeometry(QtCore.QRect(1217, 552, 284, 73))
        self.Date_Input.setStyleSheet("QLabel { background-color: #D9D9D9; }")
        self.Date_Input.setAlignment(QtCore.Qt.AlignCenter)
        self.Date_Input.raise_()

        # ABORT button
        self.Abort_Button = QtWidgets.QPushButton(self)
        self.Abort_Button.setGeometry(QtCore.QRect(1690, 915, 170, 125))
        self.Abort_Button.setStyleSheet(
            "QPushButton { background-color: #FF0000; color: #FFFFFF; border: none; padding: 10px 20px; "
            "font-family: Pretendard; font-size: 32px; font-weight: 900; line-height: 38.19px; }"
        )
        self.Abort_Button.setText("ABORT")
        self.Abort_Button.clicked.connect(self.abort_operation)
        self.Abort_Button.raise_()

        # Table (unchanged)
        self.table = QTableWidget(self)
        self.table.setGeometry(QtCore.QRect(1000, 750, 600, 300))
        self.table.setRowCount(9)
        self.table.setColumnCount(3)
        table_data = [
            ["BASE_CALIBRATION", "BASE_MIN", ""],
            ["", "BASE_MAX", ""],
            ["", "BASE_AVERAGE", ""],
            ["MIN_CALIBRATION", "MIN_MIN", ""],
            ["", "MIN_MAX", ""],
            ["", "MIN_AVERAGE", ""],
            ["MAX_CALIBRATION", "MAX_MIN", ""],
            ["", "MAX_MAX", ""],
            ["", "MAX_AVERAGE", ""]
        ]
        self.table.setSpan(0, 0, 3, 1)
        self.table.setSpan(3, 0, 3, 1)
        self.table.setSpan(6, 0, 3, 1)

        total_width = self.table.width()
        col_width = total_width // 5
        self.table.setColumnWidth(0, int(col_width * 1.5))
        self.table.setColumnWidth(1, int(col_width))
        self.table.setColumnWidth(2, int(col_width * 2.5))
        for row in range(9):
            self.table.setRowHeight(row, self.table.height() // 9)

        for row in range(9):
            for col in range(3):
                item = QTableWidgetItem(table_data[row][col])
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, col, item)

        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setStretchLastSection(True)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.show()
        self.table.raise_()

        for row in range(9):
            for col in range(3):
                if self.table.item(row, col):
                    self.table.item(row, col).setTextAlignment(Qt.AlignCenter)

    def abort_operation(self):
        self.manage.person_info_q.queue.clear()
        self.abort_signal.emit()
        self.manage.capture_thread.frame_count = 0
        self.manage.current_phase = None
        self.Camera_view0.eyes = None
        self.Camera_view0.circles = None
        self.Camera_view1.eyes = None
        self.Camera_view1.circles = None
        self.reset_data()
        print("end")

    def reset_data(self):
        self.Name_Input.setText("")
        self.Age_Input.setText("")
        self.Sex_Input.setText("")
        self.Major_Input.setText("")
        self.Date_Input.setText("")
        self.Frame_No_output.setText("No Capture")
        self.Diameter_output.setText("Diameter_output")
        for i in range(9):
            item = QTableWidgetItem("")
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 2, item)

    def table_print(self):
        """
        Compute calibration stats for eye0 and eye1 separately, then display/write the average.
        CSV format: phase, stat, eye0, eye1, avg
        """
        # BASE
        base0 = self._get_base_min_max_mean_eye(eye=0)
        base1 = self._get_base_min_max_mean_eye(eye=1)

        # MIN / MAX phases are stored in diameters[idx]
        min0 = self.min_max_mean_eye(idx=1, eye=0)
        min1 = self.min_max_mean_eye(idx=1, eye=1)

        max0 = self.min_max_mean_eye(idx=2, eye=0)
        max1 = self.min_max_mean_eye(idx=2, eye=1)

        def avg_triplet(a, b):
            return ( (a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0, (a[2] + b[2]) / 2.0 )

        base_avg = avg_triplet(base0, base1)
        min_avg  = avg_triplet(min0,  min1)
        max_avg  = avg_triplet(max0,  max1)

        # UI shows average only
        arr_avg = [base_avg, min_avg, max_avg]
        for i in range(3):
            for row in range(3):
                item = QTableWidgetItem("{:.1f}".format(arr_avg[i][row]))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row + 3 * i, 2, item)
                self.table.item(row + 3 * i, 2).setTextAlignment(Qt.AlignCenter)

        # Write CSV with both eyes + avg
        self.csv_path = os.path.join(self.csv_path, "table.csv")
        with open(self.csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["phase", "stat", "eye0", "eye1", "avg"])
            writer.writerow(["BASE", "min", f"{base0[0]}", f"{base1[0]}", f"{base_avg[0]}"])
            writer.writerow(["",     "max", f"{base0[1]}", f"{base1[1]}", f"{base_avg[1]}"])
            writer.writerow(["",     "avg", f"{base0[2]}", f"{base1[2]}", f"{base_avg[2]}"])

            writer.writerow(["MIN",  "min", f"{min0[0]}",  f"{min1[0]}",  f"{min_avg[0]}"])
            writer.writerow(["",     "max", f"{min0[1]}",  f"{min1[1]}",  f"{min_avg[1]}"])
            writer.writerow(["",     "avg", f"{min0[2]}",  f"{min1[2]}",  f"{min_avg[2]}"])

            writer.writerow(["MAX",  "min", f"{max0[0]}",  f"{max1[0]}",  f"{max_avg[0]}"])
            writer.writerow(["",     "max", f"{max0[1]}",  f"{max1[1]}",  f"{max_avg[1]}"])
            writer.writerow(["",     "avg", f"{max0[2]}",  f"{max1[2]}",  f"{max_avg[2]}"])

        print(f"Table data written to CSV at: {self.csv_path}")

    def set_text(self):
        self.Frame_No_output.setText(self.manage.capture_thread.frame_name)

    def _get_eye_samples(self, raw, eye: int) -> np.ndarray:
        """
        Normalize raw diameter samples into a (N, C) numeric numpy array for the requested eye.

        Supported raw formats:
          1) list/np.ndarray of shape (N, 3): [diameter, x, y]  (single eye)
          2) list/np.ndarray of shape (N, 6+): either
                a) [d0, x0, y0, d1, x1, y1, ...]  (interleaved per-eye triplets)
                b) [d0, d1, x0, y0, x1, y1, ...]  (diameters first, then positions)
             -> auto-detected with heuristics
          3) dict-like:
                {'eye0': samples0, 'eye1': samples1} or {0: samples0, 1: samples1}
          4) list/tuple of two per-eye sample lists: [samples0, samples1]
        """
        # dict-like
        if isinstance(raw, dict):
            for k in (f"eye{eye}", f"eye_{eye}", eye, str(eye)):
                if k in raw:
                    return np.asarray(raw[k])
            # common alternative keys
            if eye == 0:
                for k in ("left", "eye_left", "eyeL"):
                    if k in raw:
                        return np.asarray(raw[k])
            if eye == 1:
                for k in ("right", "eye_right", "eyeR"):
                    if k in raw:
                        return np.asarray(raw[k])
            return np.asarray([])

        # list/tuple with two per-eye lists
        if isinstance(raw, (list, tuple)) and len(raw) == 2 and not isinstance(raw[0], (int, float)):
            # Heuristic: raw[0] and raw[1] are themselves sequences of samples
            try:
                a0 = np.asarray(raw[0])
                a1 = np.asarray(raw[1])
                if a0.ndim >= 1 and a1.ndim >= 1:
                    return a0 if eye == 0 else a1
            except Exception:
                pass

        return np.asarray(raw)

    def _extract_eye_arrays(self, diameters_np: np.ndarray, eye: int):
        """
        Extract (diameter, x, y) arrays for eye0/eye1 from a 2D numeric array.

        Expected shapes:
          - (N, 3): [diameter, x, y]  -> treated as single-eye (eye0 == eye1)
          - (N, 6+):
              Pattern A (interleaved): [d0, x0, y0, d1, x1, y1, ...]
              Pattern B (diameters first): [d0, d1, x0, y0, x1, y1, ...]
            -> auto-detected by checking plausible ranges of x/y (non-negative, not all zeros)
        Returns: (diameter_arr, x_arr, y_arr)
        """
        if diameters_np.ndim != 2 or diameters_np.shape[0] == 0:
            return np.array([]), np.array([]), np.array([])

        cols = diameters_np.shape[1]
        if cols >= 6:
            # Candidate mappings
            # A: [d0,x0,y0,d1,x1,y1]
            candA = {
                0: (0, 1, 2),
                1: (3, 4, 5),
            }
            # B: [d0,d1,x0,y0,x1,y1]
            candB = {
                0: (0, 2, 3),
                1: (1, 4, 5),
            }

            def score(mapping):
                d_i, x_i, y_i = mapping[eye]
                x = diameters_np[:, x_i]
                y = diameters_np[:, y_i]
                # prefer mappings where x/y are not all zeros and are mostly non-negative
                nonzero = float(np.mean((x != 0) | (y != 0)))
                nonneg = float(np.mean((x >= 0) & (y >= 0)))
                finite = float(np.mean(np.isfinite(x) & np.isfinite(y)))
                return 2.0 * nonzero + 1.0 * nonneg + 1.0 * finite

            mapping = candA if score(candA) >= score(candB) else candB
            d_i, x_i, y_i = mapping[eye]
            d, x, y = diameters_np[:, d_i], diameters_np[:, x_i], diameters_np[:, y_i]
        else:
            # fallback: treat as single eye
            d, x, y = diameters_np[:, 0], diameters_np[:, 1], diameters_np[:, 2]

        return np.array(d, dtype=float), np.array(x, dtype=float), np.array(y, dtype=float)

    def _robust_min_max_mean(self, d_arr, x_arr, y_arr):
        """Apply outlier filtering (stddev-based) and return (min, max, mean)."""
        # remove zeros
        mask1 = (d_arr != 0)
        d2 = d_arr[mask1]
        x2 = x_arr[mask1]
        y2 = y_arr[mask1]

        if d2.size == 0:
            return (0.0, 0.0, 0.0)

        d_mean, d_std = np.mean(d2), np.std(d2)
        x_mean, x_std = np.mean(x2), np.std(x2)
        y_mean, y_std = np.mean(y2), np.std(y2)

        # if std is 0, broaden mask
        d_std = d_std if d_std > 1e-9 else 1e-9
        x_std = x_std if x_std > 1e-9 else 1e-9
        y_std = y_std if y_std > 1e-9 else 1e-9

        mask2 = (
            (d2 > d_mean - self.stddev * d_std) & (d2 < d_mean + self.stddev * d_std) &
            (x2 > x_mean - self.stddev * x_std) & (x2 < x_mean + self.stddev * x_std) &
            (y2 > y_mean - self.stddev * y_std) & (y2 < y_mean + self.stddev * y_std)
        )
        filtered = d2[mask2]
        if filtered.size == 0:
            filtered = d2

        return (float(np.min(filtered)), float(np.max(filtered)), float(np.mean(filtered)))

    def _get_base_min_max_mean_eye(self, eye: int):
        """
        Try to obtain BASE calibration per-eye from save_data_thread.
        Priority:
          1) save_data_thread.base_min_max_mean_eye0/eye1 (or *_0/*_1)
          2) save_data_thread.base_diameters (compute)
          3) save_data_thread.base_min_max_mean (fallback for both eyes)
        """
        sdt = self.manage.save_data_thread

        # 1) explicit per-eye fields
        for attr0, attr1 in [
            ("base_min_max_mean_eye0", "base_min_max_mean_eye1"),
            ("base_min_max_mean_0", "base_min_max_mean_1"),
            ("base_min_max_mean_left", "base_min_max_mean_right"),
        ]:
            if hasattr(sdt, attr0) and hasattr(sdt, attr1):
                return tuple(getattr(sdt, attr0 if eye == 0 else attr1))

        # 2) compute from base_diameters if present
        if hasattr(sdt, "base_diameters"):
            base_np = np.array(getattr(sdt, "base_diameters"))
            d, x, y = self._extract_eye_arrays(base_np, eye=eye)
            return self._robust_min_max_mean(d, x, y)

        # 3) fallback: same for both eyes
        if hasattr(sdt, "base_min_max_mean"):
            return tuple(getattr(sdt, "base_min_max_mean"))

        return (0.0, 0.0, 0.0)

    def min_max_mean_eye(self, idx: int, eye: int):
        """Compute (min, max, mean) for a given calibration phase idx and eye (0/1)."""
        sdt = self.manage.save_data_thread

        # Prefer per-eye buffers when available.
        # In binocular mode, sdt.diameters[idx] stores the *average* (eye0/eye1) samples,
        # while sdt.diameters_eye0[idx] / sdt.diameters_eye1[idx] store the actual per-eye samples.
        raw = None
        if hasattr(sdt, "diameters_eye0") and hasattr(sdt, "diameters_eye1"):
            try:
                raw = (sdt.diameters_eye0 if eye == 0 else sdt.diameters_eye1)[idx]
            except Exception:
                raw = None
        if raw is None:
            raw = sdt.diameters[idx]
        arr = self._get_eye_samples(raw, eye=eye)
        arr = np.asarray(arr)

        # If arr is 1D (e.g., empty or malformed), return zeros safely
        if arr.ndim == 1:
            return (0.0, 0.0, 0.0)

        d, x, y = self._extract_eye_arrays(arr, eye=eye)
        return self._robust_min_max_mean(d, x, y)

    # Backward compatibility (single-eye callers)
    def min_max_mean(self, idx):
        return self.min_max_mean_eye(idx=idx, eye=0)
