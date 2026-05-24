from pathlib import Path
import os

# Định nghĩa đường dẫn gốc tới thư mục testcases
base_dir = Path("scripts/testcases")

def print_testcase_files():
    if not base_dir.exists():
        print(f"Thư mục {base_dir} không tồn tại.")
        return

    with open("path.txt", "w", encoding='utf-8') as f:
    # Duyệt qua các thư mục con và sắp xếp theo thứ tự tc01 -> tc17
        for tc_dir in sorted(base_dir.iterdir()):
            # Lọc các thư mục có tên bắt đầu bằng 'tc' (từ tc01 đến tc17)
            if tc_dir.is_dir() and tc_dir.name.startswith("tc"):
                for filename in ["edges.txt", "users.csv"]:
                    file_path = tc_dir / filename
                    
                    # Kiểm tra nếu file thực sự tồn tại thì mới in đường dẫn
                    if file_path.exists():
                        # as_posix() giúp chuyển dấu gạch chéo ngược '\' thành '/' nếu chạy trên Windows
                        f.write(f"./{file_path.as_posix()}\n")

if __name__ == "__main__":
    print_testcase_files()
