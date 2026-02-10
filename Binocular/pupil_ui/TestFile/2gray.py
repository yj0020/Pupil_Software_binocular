import cv2
import os

def is_grayscale(image):
    # 이미지가 흑백인지 확인하기 위해 BGR 채널을 분리
    b, g, r = cv2.split(image)
    
    # 모든 채널이 동일하면 흑백 이미지
    if (b == g).all() and (g == r).all():
        return True
    else:
        return False

def convert_to_grayscale(image):
    # 이미지를 흑백으로 변환
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray_image

def process_images_in_folder(folder_path):
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

            # 이미지가 흑백인지 확인
            if is_grayscale(image):
                print(f"{filename} is already grayscale.")
            else:
                print(f"{filename} is a color image. Converting to grayscale...")
                gray_image = convert_to_grayscale(image)
                
                # 흑백 이미지를 원래 파일 이름에 "_grayscale" 접미사를 붙여 저장
                save_path = os.path.join(folder_path, f"{os.path.splitext(filename)[0]}_grayscale{os.path.splitext(filename)[1]}")
                cv2.imwrite(save_path, gray_image)
                print(f"Saved grayscale image as {save_path}")

# 사용 예시
folder_path = 'C:/Users/melon/OneDrive/Desktop/Pupil_Tracking/pupil_labs/Pupil_Software/pupil_ui/Image/POS'  # 여기서 폴더 경로를 지정
process_images_in_folder(folder_path)
