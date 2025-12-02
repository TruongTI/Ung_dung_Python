# TKB Planner Pro

Công cụ sắp xếp thời khóa biểu (TKB) tự động với giao diện đồ họa PyQt6, giúp sinh viên quản lý và tìm kiếm thời khóa biểu học tập tối ưu.

## Mô tả

TKB Planner Pro là ứng dụng desktop giúp sinh viên:
- Quản lý danh sách môn học và các lớp học
- Tự động tìm kiếm tất cả các thời khóa biểu hợp lệ không bị trùng lịch
- Kiểm tra xung đột phòng học và giáo viên
- Quản lý môn đã học và môn tiên quyết
- Xác định các giờ bận (không thể học)
- Hiển thị thời khóa biểu dạng lưới trực quan với ngày tháng
- Lưu và import thời khóa biểu

## Cấu trúc dự án

```
py-t4/
├── tkb_planner/                    # Package chính
│   ├── __init__.py                 # Khởi tạo package
│   ├── constants.py                # Các hằng số (tên thứ, tên file)
│   ├── models.py                   # Các class model và hàm chuẩn hóa
│   │   ├── ThoiGianHoc            # Khung giờ học (thứ, tiết)
│   │   ├── LichBan                # Giờ bận
│   │   ├── LopHoc                 # Lớp học
│   │   ├── MonHoc                 # Môn học
│   │   ├── chuan_hoa_ma_lop()     # Chuẩn hóa mã lớp
│   │   └── chuan_hoa_ten_giao_vien() # Chuẩn hóa tên giáo viên
│   ├── scheduler.py                # Logic tìm kiếm và kiểm tra xung đột
│   │   ├── tim_thoi_khoa_bieu()   # Tìm tất cả TKB hợp lệ
│   │   ├── kiem_tra_trung_phong_hoc() # Kiểm tra trùng phòng học
│   │   ├── kiem_tra_trung_giao_vien() # Kiểm tra trùng giáo viên
│   │   └── kiem_tra_trung_trong_cung_mon() # Kiểm tra trong cùng môn
│   ├── data_handler.py             # Xử lý lưu/tải dữ liệu JSON
│   └── ui/                         # Giao diện người dùng
│       ├── __init__.py
│       ├── main_window.py          # Cửa sổ chính
│       ├── schedule_widget.py      # Widget hiển thị lịch dạng lưới
│       ├── dialogs.py              # Các dialog nhập liệu
│       ├── course_classes_dialog.py # Dialog quản lý lớp học của môn
│       ├── custom_checkbox.py      # Checkbox tùy chỉnh
│       └── theme.py                # Quản lý theme (sáng/tối)
├── main.py                         # Entry point
├── requirements.txt                # Dependencies
├── data_TKB_pro.json              # Dữ liệu môn học và lớp học
├── completed_courses.json         # Danh sách môn đã học
├── busy_times.json                # Danh sách giờ bận
└── README.md                      # File này
```

## Yêu cầu hệ thống

- Python 3.7 trở lên
- PyQt6 >= 6.0.0

## Cài đặt và Chạy ứng dụng

### Yêu cầu hệ thống

- **Python**: 3.7 trở lên
- **PyQt6**: >= 6.0.0
- **Hệ điều hành**: Windows, Linux, hoặc macOS

### Hướng dẫn cài đặt từng bước

#### Bước 1: Kiểm tra Python

Mở terminal/command prompt và kiểm tra phiên bản Python:

**Windows:**
```bash
python --version
```

**Linux/Mac:**
```bash
python3 --version
```

Nếu chưa cài đặt Python, tải về từ [python.org](https://www.python.org/downloads/)

#### Bước 2: Clone hoặc tải dự án

Nếu bạn đã có thư mục `py-t4`, chuyển vào thư mục đó:

```bash
cd py-t4
```

#### Bước 3: Tạo Virtual Environment (Khuyến nghị)

Virtual environment giúp tránh xung đột với các package khác và giải quyết vấn đề đường dẫn dài trên Windows.

**Trên Windows (PowerShell):**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Trên Windows (Command Prompt):**
```bash
python -m venv venv
venv\Scripts\activate.bat
```

**Trên Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Sau khi kích hoạt, bạn sẽ thấy `(venv)` ở đầu dòng lệnh.

#### Bước 4: Cài đặt dependencies

Sau khi kích hoạt virtual environment, cài đặt các thư viện cần thiết:

```bash
pip install -r requirements.txt
```

Hoặc cài đặt trực tiếp:

```bash
pip install PyQt6>=6.0.0
```

**Lưu ý:** 
- Nếu gặp lỗi đường dẫn dài trên Windows, hãy sử dụng virtual environment
- Nếu gặp lỗi quyền truy cập, thử thêm `--user` vào cuối lệnh pip

### Cách chạy ứng dụng

#### Chạy cơ bản

**Quan trọng:** Đảm bảo bạn đã kích hoạt virtual environment trước khi chạy.

**Trên Windows:**
```bash
# Kích hoạt virtual environment (nếu chưa kích hoạt)
.\venv\Scripts\Activate.ps1

# Chạy ứng dụng
python main.py
```

**Trên Linux/Mac:**
```bash
# Kích hoạt virtual environment (nếu chưa kích hoạt)
source venv/bin/activate

# Chạy ứng dụng
python3 main.py
```

#### Chạy không dùng Virtual Environment

Nếu không sử dụng virtual environment, đảm bảo PyQt6 đã được cài đặt:

```bash
# Windows
python main.py

# Linux/Mac
python3 main.py
```

#### Chạy với auto-reload (Dành cho phát triển)

Để tự động reload khi có thay đổi code:

```bash
# Cài đặt watchdog (nếu chưa có)
pip install watchdog

# Chạy với auto-reload
watchmedo auto-restart --patterns="*.py" --recursive -- python main.py
```

### Quick Start

1. **Khởi động ứng dụng**: Chạy `python main.py` (hoặc `python3 main.py`)
2. **Thêm môn học**: Click nút "Thêm Môn" hoặc menu `Edit > Thêm Môn học`
3. **Thêm lớp học**: Click menu `Edit > Thêm Lớp học` hoặc click vào ô trống trên lịch
4. **Chọn môn học**: Tick vào checkbox bên cạnh tên môn
5. **Tìm TKB**: Click nút "Tìm TKB hợp lệ"
6. **Xem kết quả**: Sử dụng nút "< TKB Trước" và "TKB Tiếp >" để xem các TKB tìm được

## Hướng dẫn sử dụng

### 1. Thêm môn học

- Click nút **"Thêm Môn"** hoặc vào menu **Edit > Thêm Môn học**
- Nhập mã môn, tên môn và các môn tiên quyết (nếu có)
- Click **OK**

### 2. Thêm lớp học

- Click nút **"Thêm Môn"** (nếu chưa có môn) trước
- Click vào menu **Edit > Thêm Lớp học** hoặc click vào ô trống trên lịch
- Chọn môn học, nhập mã lớp, tên giáo viên, loại lớp, thứ và tiết học
- Click **OK**
- **Lưu ý:** Hệ thống sẽ tự động chuẩn hóa định dạng:
  - Mã lớp: Chữ đầu viết hoa (ví dụ: `a704` → `A704`)
  - Tên giáo viên: Chữ cái đầu mỗi từ viết hoa (ví dụ: `nguyễn văn a` → `Nguyễn Văn A`)

### 3. Quản lý lớp học của môn

- Click vào tên môn học trong danh sách để mở dialog quản lý lớp học
- Có thể thêm, sửa, xóa lớp học
- Các lớp được phân loại theo: Lý thuyết, Bài tập, Lớp

### 4. Thêm giờ bận

- Chọn thứ, giờ bắt đầu, giờ kết thúc và lý do
- Click nút **"Thêm"** trong phần "Giờ bận"
- Giờ bận sẽ được hiển thị trên lịch với màu xám nhạt để phân biệt với môn học
- Có thể bật/tắt hiển thị giờ bận bằng checkbox

### 5. Quản lý môn đã học

- Vào menu **Edit > Nhập môn đã học** để thêm môn đã học
- Vào menu **Edit > Xem môn đã học** để xem và xóa môn đã học
- Môn tiên quyết phải có trong danh sách môn đã học

### 6. Tìm thời khóa biểu

- Chọn các môn học muốn học (tick vào checkbox)
- Đánh dấu môn bắt buộc nếu cần (tick vào "Bắt buộc")
- Click nút **"Tìm TKB hợp lệ"**
- Hệ thống sẽ tìm tất cả các TKB hợp lệ không bị trùng lịch
- Sử dụng nút **"< TKB Trước"** và **"TKB Tiếp >"** để xem các kết quả

### 7. Lưu thời khóa biểu

- Sau khi tìm được TKB, click nút **"Lưu TKB"** để lưu ra file text
- File sẽ chứa thông tin đầy đủ về TKB

### 8. Import thời khóa biểu

- Vào menu **File > Import thời khóa biểu**
- Chọn file TKB đã lưu trước đó (.txt)
- Hệ thống sẽ tự động tìm và hiển thị TKB lên lịch
- **Lưu ý:** Các lớp học trong file TKB phải đã tồn tại trong hệ thống

### 9. Lưu dữ liệu môn học

- Vào menu **File > Lưu dữ liệu môn học** để lưu tất cả môn học và lớp học vào file JSON
- Dữ liệu sẽ được lưu tự động vào `data_TKB_pro.json`

### 10. Chuyển đổi chế độ sáng/tối

- Vào menu **View > Chế độ tối** (hoặc **Chế độ sáng**) để chuyển đổi giữa hai chế độ
- Ứng dụng sẽ tự động lưu lựa chọn của bạn và áp dụng lại khi khởi động lần sau

## Tính năng

### Quản lý dữ liệu
- ✅ Quản lý môn học và lớp học
- ✅ Tự động chuẩn hóa định dạng mã lớp và tên giáo viên
- ✅ Quản lý môn đã học
- ✅ Quản lý giờ bận với bật/tắt hiển thị
- ✅ Tìm kiếm và lọc môn học
- ✅ Sửa/xóa môn học và lớp học
- ✅ Lưu/tải dữ liệu JSON tự động

### Kiểm tra xung đột
- ✅ Kiểm tra xung đột lịch học giữa các môn
- ✅ Kiểm tra trùng phòng học (chỉ trong cùng môn khi thêm lớp)
- ✅ Kiểm tra trùng giáo viên (một giáo viên không thể dạy nhiều lớp cùng lúc)
- ✅ Kiểm tra trùng với giờ bận
- ✅ Hỗ trợ môn tiên quyết (kiểm tra trong danh sách môn đã học)
- ✅ Hỗ trợ môn bắt buộc

### Tìm kiếm và hiển thị
- ✅ Tìm kiếm tất cả TKB hợp lệ (thuật toán đệ quy)
- ✅ Hiển thị lịch dạng lưới với ngày tháng
- ✅ Hiển thị giờ bận với màu và font khác biệt
- ✅ Điều hướng giữa các TKB tìm được
- ✅ Lưu TKB ra file text
- ✅ Import TKB từ file đã lưu

### Giao diện
- ✅ Chế độ sáng/tối (Dark/Light mode) với lưu cài đặt tự động
- ✅ Giao diện trực quan, dễ sử dụng
- ✅ Click vào ô lịch để thêm lớp học nhanh
- ✅ Hiển thị thông báo và log hoạt động

## Lưu ý

### Về dữ liệu
- File dữ liệu `data_TKB_pro.json` sẽ được tạo tự động trong thư mục chạy ứng dụng
- File `completed_courses.json` lưu danh sách môn đã học
- File `busy_times.json` lưu danh sách giờ bận
- Dữ liệu được lưu tự động khi thêm/sửa/xóa

### Về thời gian
- Ứng dụng hỗ trợ 7 ngày trong tuần (Thứ 2 đến Chủ Nhật)
- Mỗi ngày có 12 tiết học (từ 7h-11h và 13h-17h)
- Giờ bận được chuyển đổi tự động sang tiết học

### Về logic kiểm tra
- **Khi thêm lớp trong area lớp học:** Chỉ kiểm tra xung đột trong cùng một môn (phòng học, giáo viên)
- **Khi tìm TKB:** Kiểm tra xung đột giữa tất cả các môn đã chọn
- Môn tiên quyết phải có trong danh sách môn đã học
- Một giáo viên không thể dạy nhiều lớp cùng lúc
- Phòng học có thể được sử dụng bởi nhiều lớp nếu không trùng giờ

## Phát triển

Dự án được tổ chức theo cấu trúc module rõ ràng:

- **`models.py`**: Định nghĩa các class dữ liệu và hàm chuẩn hóa
- **`scheduler.py`**: Logic xử lý tìm kiếm TKB và kiểm tra xung đột
- **`data_handler.py`**: Xử lý I/O dữ liệu JSON
- **`ui/`**: Tất cả các component giao diện
  - `main_window.py`: Cửa sổ chính và logic điều khiển
  - `schedule_widget.py`: Widget hiển thị lịch dạng lưới
  - `dialogs.py`: Các dialog nhập liệu
  - `course_classes_dialog.py`: Dialog quản lý lớp học
  - `custom_checkbox.py`: Checkbox tùy chỉnh
  - `theme.py`: Quản lý theme

## Phiên bản

**Version 3.0.0**

### Các cập nhật chính:
- Thêm tính năng import TKB từ file
- Chuẩn hóa tự động định dạng mã lớp và tên giáo viên
- Kiểm tra trùng phòng học và giáo viên
- Quản lý môn đã học
- Cải thiện hiển thị giờ bận
- Tối ưu logic kiểm tra xung đột

## Giấy phép

Dự án này được phát triển cho mục đích giáo dục.
