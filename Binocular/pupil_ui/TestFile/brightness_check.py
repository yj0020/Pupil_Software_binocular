import cv2
import numpy as np
import os

def check_brightness_in_folder(folder_path):
    # 폴더 내 모든 파일 순회
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # 이미지 파일만 처리
        if os.path.isfile(file_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            # 이미지 읽기
            image = cv2.imread(file_path)
            
            if image is None:
                print(f"Could not read image {filename}")
                continue

            # 그레이스케일로 변환
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # 이미지 밝기 계산
            average_brightness = np.mean(gray_image)

            print(f"{filename}: Average brightness = {average_brightness}")

            # 밝기 확인
            if average_brightness == 128:
                print(f"{filename} has the correct brightness of 128.")
            else:
                print(f"{filename} does not have the correct brightness. It is {average_brightness}.")

# 사용 예시
folder_path = 'C:/Users/melon/OneDrive/Desktop/Pupil_Tracking/pupil_labs/Pupil_Software/pupil_ui/Datas/2024-08-27/1/20-40-45/frames/original'  # 여기서 폴더 경로를 지정
check_brightness_in_folder(folder_path)
