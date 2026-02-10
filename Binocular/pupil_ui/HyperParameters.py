import os

class HyperParameters:
    def __init__(self):
        self.fps = 30     # 110 이하로 설정
        self.stddev = 2
        self.base_path = os.path.dirname(os.path.abspath(__file__)) + os.sep
        # NOTE: base_path is resolved relative to this file, so running from any CWD works.
        self.Trial = 25  # 25가 디폴트

        # Timers (ms)
        self.Start_time = 10000  # 10초
        self.Ready_time = 5000   # 5초. 실험 시작하자마자 뜨는 화면 (page 8)
        self.Rest_time = 4000    # 4초
        self.Calibration_time = 6000  # 6초

        # Image base paths
        # NOTE: NEG/POS are split:
        #   1~15  -> Image/<NEG|POS>/high/
        #   16~30 -> Image/<NEG|POS>/low/
        # monitor_2.py will resolve high/low automatically from the filename index.
        self.NEG_Image_Base_Path = os.path.join(self.base_path, 'Image', 'NEG')
        self.NEU_Image_Base_Path = os.path.join(self.base_path, 'Image', 'NEU')
        self.POS_Image_Base_Path = os.path.join(self.base_path, 'Image', 'POS')

        # Optional explicit paths (not required, but handy)
        self.NEG_Image_High_Path = os.path.join(self.base_path, 'Image', 'NEG', 'high')
        self.NEG_Image_Low_Path = os.path.join(self.base_path, 'Image', 'NEG', 'low')
        self.POS_Image_High_Path = os.path.join(self.base_path, 'Image', 'POS', 'high')
        self.POS_Image_Low_Path = os.path.join(self.base_path, 'Image', 'POS', 'low')

        self.NEG_Images = [
            'NEG1.jpg', 'NEG2.jpg', 'NEG3.jpg', 'NEG4.jpg', 'NEG5.jpg', 'NEG6.jpg', 'NEG7.jpg', 'NEG8.jpg', 'NEG9.jpg', 'NEG10.jpg',
            'NEG11.jpg', 'NEG12.jpg', 'NEG13.jpg', 'NEG14.jpg', 'NEG15.jpg', 'NEG16.jpg', 'NEG17.jpg', 'NEG18.jpg', 'NEG19.jpg', 'NEG20.jpg',
            'NEG21.jpg', 'NEG22.jpg', 'NEG23.jpg', 'NEG24.jpg', 'NEG25.jpg', 'NEG26.jpg', 'NEG27.jpg', 'NEG28.jpg', 'NEG29.jpg', 'NEG30.jpg'
        ]
        self.NEU_Images = [
            'NEU1.jpg', 'NEU2.jpg', 'NEU3.jpg', 'NEU4.jpg', 'NEU5.jpg', 'NEU6.jpg', 'NEU7.jpg', 'NEU8.jpg', 'NEU9.jpg', 'NEU10.jpg',
            'NEU11.jpg', 'NEU12.jpg', 'NEU13.jpg', 'NEU14.jpg', 'NEU15.jpg', 'NEU16.jpg', 'NEU17.jpg', 'NEU18.jpg', 'NEU19.jpg', 'NEU20.jpg',
            'NEU21.jpg', 'NEU22.jpg', 'NEU23.jpg', 'NEU24.jpg', 'NEU25.jpg', 'NEU26.jpg', 'NEU27.jpg', 'NEU28.jpg', 'NEU29.jpg', 'NEU30.jpg'
        ]
        self.POS_Images = [
            'POS1.jpg', 'POS2.jpg', 'POS3.jpg', 'POS4.jpg', 'POS5.jpg', 'POS6.jpg', 'POS7.jpg', 'POS8.jpg', 'POS9.jpg', 'POS10.jpg',
            'POS11.jpg', 'POS12.jpg', 'POS13.jpg', 'POS14.jpg', 'POS15.jpg', 'POS16.jpg', 'POS17.jpg', 'POS18.jpg', 'POS19.jpg', 'POS20.jpg',
            'POS21.jpg', 'POS22.jpg', 'POS23.jpg', 'POS24.jpg', 'POS25.jpg', 'POS26.jpg', 'POS27.jpg', 'POS28.jpg', 'POS29.jpg', 'POS30.jpg'
        ]
