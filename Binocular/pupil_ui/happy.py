import os
import cv2
from PyQt5.QtCore import QThread


class HappyThread(QThread):
    def __init__(self, manage):
        super().__init__()
        self.manage = manage

    def save_image(self):
        """
        Save original images for both eyes into:
          <original_path>/eye0/<frame_name>.png
          <original_path>/eye1/<frame_name>.png
        """
        base = self.manage.capture_thread.original_path
        frame_name = self.manage.capture_thread.frame_name

        eye0 = self.manage.capture_thread.recent_eye0_original
        eye1 = self.manage.capture_thread.recent_eye1_original

        if base is None or frame_name is None or frame_name == "":
            return

        eye0_dir = os.path.join(base, "eye0")
        eye1_dir = os.path.join(base, "eye1")
        os.makedirs(eye0_dir, exist_ok=True)
        os.makedirs(eye1_dir, exist_ok=True)

        if eye0 is not None:
            cv2.imwrite(os.path.join(eye0_dir, f"{frame_name}.png"), eye0)
        if eye1 is not None:
            cv2.imwrite(os.path.join(eye1_dir, f"{frame_name}.png"), eye1)
