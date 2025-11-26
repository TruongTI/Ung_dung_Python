# TKB Planner Pro

Công cụ sắp xếp thời khóa biểu (TKB) tự động với giao diện đồ họa PyQt6.

## Mô tả

TKB Planner Pro là ứng dụng giúp sinh viên tìm kiếm và sắp xếp thời khóa biểu học tập một cách tự động. Ứng dụng có thể:

- Quản lý danh sách môn học và các lớp học
- Xác định các giờ bận (không thể học)
- Tìm tất cả các thời khóa biểu hợp lệ không bị trùng lịch
- Hỗ trợ môn tiên quyết và môn bắt buộc
- Hiển thị thời khóa biểu dạng lưới trực quan
- Lưu và tải dữ liệu từ file JSON

## Cấu trúc dự án

```
py-t4/
├── tkb_planner/          # Package chính
│   ├── __init__.py       # Khởi tạo package
│   ├── constants.py      # Các hằng số (tên thứ, tên file)
│   ├── models.py         # Các class model (ThoiGianHoc, LichBan, LopHoc, MonHoc)
│   ├── scheduler.py      # Logic tìm kiếm và kiểm tra xung đột TKB
│   ├── data_handler.py   # Xử lý lưu/tải dữ liệu JSON
│   └── ui/               # Giao diện người dùng
│       ├── __init__.py
│       ├── main_window.py      # Cửa sổ chính
│       ├── schedule_widget.py  # Widget hiển thị lịch
│       ├── dialogs.py          # Các dialog nhập liệu
│       └── theme.py            # Quản lý theme (sáng/tối)
├── main.py               # Entry point
├── requirements.txt      # Dependencies
└── README.md            # File này
```

## Yêu cầu hệ thống

- Python 3.7 trở lên
- PyQt6

## Cài đặt

### 1. Cài đặt Python

Đảm bảo bạn đã cài đặt Python 3.7 trở lên. Kiểm tra bằng lệnh:

```bash
python --version
```

hoặc

```bash
python3 --version
```

### 2. Tạo Virtual Environment (Khuyến nghị)

Virtual environment giúp tránh xung đột với các package khác và giải quyết vấn đề đường dẫn dài trên Windows:

**Trên Windows:**
```bash
cd py-t4
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Trên Linux/Mac:**
```bash
cd py-t4
python3 -m venv venv
source venv/bin/activate
```

### 3. Cài đặt dependencies

Sau khi kích hoạt virtual environment, cài đặt các thư viện cần thiết:

```bash
pip install -r requirements.txt
```

hoặc cài đặt PyQt6 trực tiếp:

```bash
pip install PyQt6
```

**Lưu ý:** Nếu gặp lỗi đường dẫn dài trên Windows khi cài đặt trực tiếp (không dùng venv), hãy sử dụng virtual environment như hướng dẫn trên.

## Cách chạy

**Quan trọng:** Đảm bảo bạn đã kích hoạt virtual environment trước khi chạy ứng dụng.

### Trên Windows

```bash
# Kích hoạt virtual environment (nếu chưa kích hoạt)
.\venv\Scripts\Activate.ps1

# Chạy ứng dụng
python main.py
```

### Trên Linux/Mac

```bash
# Kích hoạt virtual environment (nếu chưa kích hoạt)
source venv/bin/activate

# Chạy ứng dụng
python3 main.py
```

**Lưu ý:** Nếu bạn không sử dụng virtual environment, có thể chạy trực tiếp `python main.py` hoặc `python3 main.py`, nhưng cần đảm bảo PyQt6 đã được cài đặt trong môi trường Python của bạn.

## Hướng dẫn sử dụng

### 1. Thêm môn học

- Click nút **"Thêm Môn"** hoặc vào menu **Edit > Thêm Môn học**
- Nhập mã môn, tên môn và các môn tiên quyết (nếu có)
- Click **OK**

### 2. Thêm lớp học

- Click nút **"Thêm Môn"** (nếu chưa có môn) trước
- Click vào menu **Edit > Thêm Lớp học** hoặc click vào ô trống trên lịch
- Chọn môn học, nhập mã lớp, tên giáo viên, thứ và tiết học
- Click **OK**

### 3. Thêm giờ bận

- Chọn ngày, giờ bắt đầu, giờ kết thúc và lý do
- Click nút **"Thêm"** trong phần "Giờ bận"

### 4. Tìm thời khóa biểu

- Chọn các môn học muốn học (tick vào checkbox)
- Đánh dấu môn bắt buộc nếu cần (tick vào "Bắt buộc")
- Click nút **"Tìm TKB hợp lệ"**
- Sử dụng nút **"< TKB Trước"** và **"TKB Tiếp >"** để xem các kết quả

### 5. Lưu thời khóa biểu

- Sau khi tìm được TKB, click nút **"Lưu TKB"** để lưu ra file text

### 6. Lưu dữ liệu môn học

- Vào menu **File > Lưu dữ liệu môn học** để lưu tất cả môn học và lớp học vào file JSON

### 7. Chuyển đổi chế độ sáng/tối

- Vào menu **View > Chế độ tối** (hoặc **Chế độ sáng**) để chuyển đổi giữa hai chế độ
- Ứng dụng sẽ tự động lưu lựa chọn của bạn và áp dụng lại khi khởi động lần sau

## Dữ liệu mẫu

Khi chạy lần đầu, ứng dụng sẽ tự động tạo file `data_TKB_pro.json` với dữ liệu mẫu gồm:
- Môn Giải tích 1 (MI1111) với 2 lớp
- Môn Tin học đại cương (IT1110) với 2 lớp và yêu cầu môn tiên quyết MI1111

## Tính năng

- ✅ Quản lý môn học và lớp học
- ✅ Kiểm tra xung đột lịch học
- ✅ Hỗ trợ môn tiên quyết
- ✅ Hỗ trợ môn bắt buộc
- ✅ Quản lý giờ bận
- ✅ Tìm kiếm tất cả TKB hợp lệ
- ✅ Hiển thị lịch dạng lưới với ngày tháng
- ✅ Lưu/tải dữ liệu JSON
- ✅ Lưu TKB ra file text
- ✅ Tìm kiếm và lọc môn học
- ✅ Sửa/xóa môn học
- ✅ Chế độ sáng/tối (Dark/Light mode) với lưu cài đặt tự động

## Lưu ý

- File dữ liệu `data_TKB_pro.json` sẽ được tạo tự động trong thư mục chạy ứng dụng
- Ứng dụng hỗ trợ 7 ngày trong tuần (Thứ 2 đến Chủ Nhật)
- Mỗi ngày có 12 tiết học (từ 7h-11h và 13h-17h)
- Môn tiên quyết phải được thêm vào danh sách môn học trước

## Phát triển

Dự án được tổ chức theo cấu trúc module rõ ràng:
- `models.py`: Định nghĩa các class dữ liệu
- `scheduler.py`: Logic xử lý tìm kiếm TKB
- `data_handler.py`: Xử lý I/O dữ liệu
- `ui/`: Tất cả các component giao diện

## Giấy phép

Dự án này được phát triển cho mục đích giáo dục.

## Phiên bản

Version 3.0.0

