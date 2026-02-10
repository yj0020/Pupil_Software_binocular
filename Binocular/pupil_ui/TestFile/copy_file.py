import os
import shutil

def copy_with_new_name(folder_path):
    # 폴더 내 모든 파일 순회
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # 이미지 파일만 처리
        if os.path.isfile(file_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            # 파일 이름을 _로 구분하여 분리
            parts = filename.split('_')

            # 분리된 파일 이름의 두 번째 부분을 새로운 파일 이름으로 사용
            if len(parts) > 1:
                new_filename = f"{parts[1]}{os.path.splitext(filename)[1]}"
                new_file_path = os.path.join(folder_path, new_filename)

                # 파일 복사
                shutil.copy(file_path, new_file_path)
                print(f"Copied {filename} to {new_file_path}")

# 사용 예시
folder_path = 'C:/Users/melon/OneDrive/Desktop/Pupil_Tracking/pupil_labs/Pupil_Software/pupil_ui/Image/POS'  # 여기서 폴더 경로를 지정
copy_with_new_name(folder_path)
