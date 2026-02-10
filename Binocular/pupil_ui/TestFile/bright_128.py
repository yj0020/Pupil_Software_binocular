import cv2
import numpy as np
import os

def adjust_brightness_to_128(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    average_brightness = np.mean(gray_image)

    # 밝기 조정을 위해 차이를 계산
    brightness_difference = 128 - average_brightness

    # 모든 채널에 brightness_difference를 더해 밝기 조정
    adjusted_image = cv2.add(image, np.array([brightness_difference], dtype=np.uint8))

    return adjusted_image

def adjust_brightness_in_folder(folder_path):
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

            # 밝기를 128로 조정
            adjusted_image = adjust_brightness_to_128(image)

            # 수정된 이미지 저장
            save_path = os.path.join(folder_path, f"adjusted_{filename}")
            cv2.imwrite(save_path, adjusted_image)

            print(f"Adjusted and saved {filename} with brightness 128 as {save_path}")

# 사용 예시
folder_path = 'C:/Users/melon/OneDrive/Desktop/Pupil_Tracking/pupil_labs/Pupil_Software/pupil_ui/Image/NEU'  # 여기서 폴더 경로를 지정
adjust_brightness_in_folder(folder_path)
