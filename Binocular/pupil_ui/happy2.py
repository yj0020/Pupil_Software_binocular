import cv2
from PyQt5.QtCore import *

class Happy2Thread(QThread):

    def __init__(self, manage):
        super().__init__()
        self.manage = manage
    
    def save_image(self):
        cv2.imwrite(self.manage.capture_thread.original_path+"\\"+self.manage.capture_thread.frame_name+".png", self.manage.capture_thread.recent_eye0_original)