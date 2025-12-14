# TKB Planner Pro

Ứng dụng desktop quản lý và sắp xếp thời khóa biểu (TKB) tự động với giao diện đồ họa PyQt6, giúp sinh viên tìm kiếm và quản lý thời khóa biểu học tập tối ưu.

## 📋 Mục lục

- [Giới thiệu](#giới-thiệu)
- [Tính năng chính](#tính-năng-chính)
- [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
- [Cài đặt](#cài-đặt)
- [Hướng dẫn sử dụng](#hướng-dẫn-sử-dụng)
- [Cấu trúc dự án](#cấu-trúc-dự-án)
- [Phát triển](#phát-triển)
- [Xử lý sự cố](#xử-lý-sự-cố)
- [Phiên bản](#phiên-bản)

## Giới thiệu

**TKB Planner Pro** là công cụ hỗ trợ sinh viên quản lý và tìm kiếm thời khóa biểu học tập một cách tự động và thông minh. Ứng dụng sử dụng thuật toán backtracking để tìm tất cả các thời khóa biểu hợp lệ, tự động kiểm tra xung đột lịch học, phòng học, và giáo viên.

### Đối tượng sử dụng

- Sinh viên cần sắp xếp thời khóa biểu học tập
- Người dùng cần quản lý nhiều lớp học và môn học
- Người dùng muốn tìm kiếm thời khóa biểu tối ưu không bị trùng lịch

## Tính năng chính

### 📚 Quản lý dữ liệu

- **Quản lý môn học**: Thêm, sửa, xóa môn học với mã môn, tên môn, và môn tiên quyết
- **Quản lý lớp học**: Quản lý nhiều lớp học cho mỗi môn với thông tin giáo viên, phòng học, thời gian
- **Phân loại lớp**: Hỗ trợ 3 loại lớp: Lý thuyết, Bài tập, và Lớp
- **Tìm kiếm môn học**: Tìm kiếm và lọc môn học theo mã hoặc tên
- **Chuẩn hóa tự động**: Tự động chuẩn hóa mã lớp và tên giáo viên
- **Quản lý môn đã học**: Đánh dấu môn đã học để kiểm tra môn tiên quyết
- **Quản lý giờ bận**: Thêm các khung giờ không thể học (giờ làm việc, giờ họp, v.v.)

### 🔍 Tìm kiếm thời khóa biểu

- **Thuật toán thông minh**: Sử dụng backtracking để tìm tất cả TKB hợp lệ
- **Kiểm tra xung đột tự động**:
  - Xung đột lịch học giữa các môn
  - Trùng giáo viên (một giáo viên không thể dạy nhiều lớp cùng lúc)
  - Trùng phòng học trong cùng môn
  - Xung đột với giờ bận
  - Kiểm tra môn tiên quyết
- **Môn bắt buộc**: Đánh dấu môn bắt buộc phải có trong TKB
- **Giới hạn tìm kiếm**: Tối đa 15 môn và 1000 TKB để đảm bảo hiệu suất
- **Timeout**: Tự động dừng sau 30 giây nếu tìm kiếm quá lâu

### 🎨 Giao diện người dùng

- **Hiển thị lịch trực quan**: Lưới 7 ngày × 12 tiết với màu sắc phân biệt môn học
- **Chế độ sáng/tối**: Hỗ trợ dark mode và light mode với lưu cài đặt tự động
- **Điều hướng TKB**: Duyệt qua các TKB tìm được với nút "Trước" và "Tiếp"
- **Thông tin chi tiết**: Hiển thị thông tin lớp học khi hover chuột
- **Click để thêm nhanh**: Click vào ô lịch để thêm lớp học nhanh chóng
- **Quản lý lớp theo môn**: Click vào tên môn để quản lý tất cả lớp học của môn đó

### 💾 Lưu trữ và Import/Export

- **Lưu tự động**: Tự động lưu dữ liệu môn học, lớp học, giờ bận, và môn đã học
- **Lưu TKB**: Lưu thời khóa biểu đã chọn ra file text
- **Import TKB**: Import thời khóa biểu từ file đã lưu
- **Backup tự động**: Tự động backup file dữ liệu khi lưu

## Yêu cầu hệ thống

- **Python**: 3.7 trở lên
- **PyQt6**: >= 6.0.0
- **Hệ điều hành**: Windows, Linux, hoặc macOS
- **Dung lượng**: ~50MB (bao gồm virtual environment)

## Cài đặt

### Bước 1: Kiểm tra Python

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

### Bước 2: Clone hoặc tải dự án

Nếu bạn đã có thư mục dự án, chuyển vào thư mục đó:

```bash
cd PYTHON_T5
```

### Bước 3: Tạo Virtual Environment (Khuyến nghị)

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

### Bước 4: Cài đặt dependencies

Sau khi kích hoạt virtual environment, cài đặt các thư viện cần thiết:

```bash
pip install -r requirements.txt
```

Hoặc cài đặt trực tiếp:

```bash
pip install PyQt6>=6.0.0 watchdog>=6.0.0
```

**Lưu ý:** 
- Nếu gặp lỗi đường dẫn dài trên Windows, hãy sử dụng virtual environment
- Nếu gặp lỗi quyền truy cập, thử thêm `--user` vào cuối lệnh pip

### Bước 5: Chạy ứng dụng

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

## Hướng dẫn sử dụng

### Quick Start

1. **Khởi động ứng dụng**: Chạy `python main.py` (hoặc `python3 main.py`)
2. **Thêm môn học**: Click nút "Thêm Môn" hoặc menu `Edit > Thêm Môn học`
3. **Thêm lớp học**: Click menu `Edit > Thêm Lớp học` hoặc click vào ô trống trên lịch
4. **Chọn môn học**: Tick vào checkbox bên cạnh tên môn
5. **Tìm TKB**: Click nút "Tìm TKB hợp lệ"
6. **Xem kết quả**: Sử dụng nút "< TKB Trước" và "TKB Tiếp >" để xem các TKB tìm được

### Chi tiết các chức năng

#### 1. Thêm môn học

**Cách 1:** Click nút **"Thêm Môn"** ở bên trái giao diện  
**Cách 2:** Vào menu **Edit > Thêm Môn học**

Nhập thông tin:
- **Mã môn**: Mã định danh của môn (ví dụ: `CS101`)
- **Tên môn**: Tên đầy đủ của môn học
- **Môn tiên quyết**: Danh sách mã môn tiên quyết, cách nhau bởi dấu phẩy (ví dụ: `CS100, MATH101`)

Click **OK** để lưu.

#### 2. Thêm lớp học

**Cách 1:** Vào menu **Edit > Thêm Lớp học**  
**Cách 2:** Click vào ô trống trên lịch (schedule widget) - sẽ tự động điền thứ và tiết

Nhập thông tin:
- **Môn học**: Chọn môn từ danh sách
- **Mã lớp**: Mã lớp học (ví dụ: `A704`, `B102`)
- **Tên giáo viên**: Tên giáo viên phụ trách
- **Loại lớp**: Chọn từ Lý thuyết, Bài tập, hoặc Lớp
- **Thứ**: Chọn thứ trong tuần (2-8, với 8 là Chủ Nhật)
- **Tiết bắt đầu/Kết thúc**: Chọn tiết học (1-12)

**Lưu ý:** Hệ thống tự động chuẩn hóa:
- Mã lớp: Chữ đầu viết hoa (ví dụ: `a704` → `A704`)
- Tên giáo viên: Chữ cái đầu mỗi từ viết hoa (ví dụ: `nguyễn văn a` → `Nguyễn Văn A`)

#### 3. Quản lý lớp học của môn

- **Click vào tên môn học** trong danh sách (phần checkbox) để mở dialog quản lý lớp học
- Trong dialog, bạn có thể:
  - Xem tất cả lớp học của môn
  - Thêm lớp học mới
  - Sửa thông tin lớp học
  - Xóa lớp học
- Các lớp được phân loại và hiển thị theo: Lý thuyết, Bài tập, Lớp

#### 4. Thêm giờ bận

Giờ bận là các khung giờ bạn không thể học (ví dụ: giờ làm việc, giờ họp).

1. Trong phần **"Giờ bận"** bên trái:
   - Chọn **Thứ** trong tuần
   - Chọn **Giờ bắt đầu** và **Giờ kết thúc**
   - Nhập **Lý do** (tùy chọn)
2. Click nút **"Thêm"**
3. Giờ bận sẽ:
   - Hiển thị trên lịch với màu xám nhạt
   - Có checkbox để bật/tắt hiển thị
   - Tự động được loại trừ khi tìm TKB

#### 5. Quản lý môn đã học

Môn đã học được dùng để kiểm tra môn tiên quyết.

- **Thêm môn đã học**: Menu **TKB > Nhập môn đã học**
  - Nhập danh sách mã môn, cách nhau bởi dấu phẩy
- **Xem/Xóa môn đã học**: Menu **TKB > Xem danh sách môn đã học**
  - Xem danh sách môn đã học
  - Xóa môn khỏi danh sách

**Lưu ý:** 
- Môn đã học sẽ bị disable (không thể chọn) trong danh sách môn học
- Môn tiên quyết phải có trong danh sách môn đã học

#### 6. Tìm kiếm và lọc môn học

- Sử dụng ô **"Nhập môn:"** ở đầu danh sách môn học
- Nhập mã môn hoặc tên môn để lọc
- Danh sách sẽ tự động cập nhật khi bạn nhập

#### 7. Tìm thời khóa biểu

1. **Chọn môn học**: Tick vào checkbox bên cạnh tên môn
2. **Đánh dấu môn bắt buộc** (tùy chọn): Tick vào checkbox "Bắt buộc"
   - Môn bắt buộc phải có trong mọi TKB tìm được
3. Click nút **"Tìm TKB hợp lệ"**
4. Hệ thống sẽ:
   - Tìm tất cả các TKB hợp lệ không bị trùng lịch
   - Kiểm tra xung đột giữa các môn
   - Kiểm tra trùng giáo viên
   - Loại trừ giờ bận
   - Kiểm tra môn tiên quyết
5. **Xem kết quả**:
   - Sử dụng nút **"< TKB Trước"** và **"TKB Tiếp >"** để điều hướng
   - Label ở giữa hiển thị "TKB X/Y" (X là TKB hiện tại, Y là tổng số TKB)
   - TKB được hiển thị trên lịch với màu sắc khác nhau cho mỗi môn

#### 8. Lưu thời khóa biểu

- Sau khi tìm được TKB, click nút **"Lưu TKB"**
- Chọn vị trí lưu file
- File text sẽ chứa:
  - Thông tin đầy đủ về TKB
  - Danh sách môn học và lớp học
  - Thời gian học của từng lớp

#### 9. Import thời khóa biểu

- Vào menu **File > Import thời khóa biểu**
- Chọn file TKB đã lưu trước đó (.txt)
- Hệ thống sẽ:
  - Đọc file và tìm các lớp học tương ứng
  - Hiển thị TKB lên lịch
  - Hiển thị thông báo nếu có lớp không tìm thấy

**Lưu ý:** Các lớp học trong file TKB phải đã tồn tại trong hệ thống.

#### 10. Chuyển đổi chế độ sáng/tối

- Vào menu **View > Chế độ tối** (hoặc **Chế độ sáng**)
- Ứng dụng sẽ:
  - Chuyển đổi theme ngay lập tức
  - Tự động lưu lựa chọn
  - Áp dụng lại khi khởi động lần sau

#### 11. Sửa/Xóa môn học và lớp học

- **Sửa môn học**: Menu **Edit > Sửa môn học**
  - Mở dialog với danh sách tất cả môn học
  - Click "Sửa" để chỉnh sửa
  - Click "Xóa" để xóa môn (sẽ xóa tất cả lớp học của môn đó)
  
- **Sửa lớp học**: Menu **Edit > Sửa lớp học**
  - Mở dialog với danh sách tất cả lớp học
  - Click "Sửa" để chỉnh sửa
  - Click "Xóa" để xóa lớp

- **Xóa trực tiếp**: Click nút "Xóa" bên cạnh môn học trong danh sách

### Menu và Chức năng

#### Menu File
- **Lưu dữ liệu môn học**: Lưu tất cả môn học và lớp học vào file JSON (`data_TKB_pro.json`)
- **Import thời khóa biểu**: Import TKB từ file text đã lưu trước đó
- **Thoát**: Đóng ứng dụng

#### Menu Edit
- **Thêm Môn học**: Thêm môn học mới vào hệ thống
- **Thêm Lớp học**: Thêm lớp học mới cho một môn
- **Sửa môn học**: Mở dialog để sửa/xóa tất cả môn học
- **Sửa lớp học**: Mở dialog để sửa/xóa tất cả lớp học

#### Menu View
- **Chọn tất cả các môn**: Chọn tất cả môn học trong danh sách
- **Bỏ chọn tất cả**: Bỏ chọn tất cả môn học
- **Xóa toàn bộ dữ liệu**: Xóa tất cả môn học và lớp học (có xác nhận)
- **Chế độ tối/Sáng**: Chuyển đổi giữa chế độ sáng và tối

#### Menu TKB
- **Tìm TKB hợp lệ**: Tìm tất cả thời khóa biểu hợp lệ
- **TKB Trước/Tiếp**: Điều hướng giữa các TKB đã tìm được
- **Xóa TKB**: Xóa TKB hiện tại khỏi lịch
- **Nhập môn đã học**: Thêm môn vào danh sách môn đã học
- **Xem danh sách môn đã học**: Xem và quản lý môn đã học

#### Menu Help
- **Giới thiệu**: Hiển thị thông tin về ứng dụng

## Cấu trúc dự án

```
PYTHON_T5/
├── tkb_planner/                    # Package chính
│   ├── __init__.py                 # Khởi tạo package
│   ├── constants.py                # Các hằng số (tên thứ, tên file, giới hạn)
│   ├── models.py                   # Các class model và hàm chuẩn hóa
│   │   ├── ThoiGianHoc            # Khung giờ học (thứ, tiết)
│   │   ├── LichBan                # Giờ bận
│   │   ├── LopHoc                 # Lớp học
│   │   ├── MonHoc                 # Môn học
│   │   ├── chuan_hoa_ma_lop()     # Chuẩn hóa mã lớp
│   │   └── chuan_hoa_ten_giao_vien() # Chuẩn hóa tên giáo viên
│   ├── scheduler.py                # Logic tìm kiếm và kiểm tra xung đột
│   │   ├── tim_thoi_khoa_bieu()   # Tìm tất cả TKB hợp lệ (backtracking)
│   │   ├── kiem_tra_trung_phong_hoc() # Kiểm tra trùng phòng học
│   │   ├── kiem_tra_trung_giao_vien() # Kiểm tra trùng giáo viên
│   │   └── kiem_tra_trung_trong_cung_mon() # Kiểm tra trong cùng môn
│   ├── data_handler.py             # Xử lý lưu/tải dữ liệu JSON
│   │   ├── save_data()            # Lưu môn học và lớp học
│   │   ├── load_data()            # Tải môn học và lớp học
│   │   ├── save_completed_courses() # Lưu môn đã học
│   │   ├── load_completed_courses() # Tải môn đã học
│   │   ├── save_busy_times()      # Lưu giờ bận
│   │   ├── load_busy_times()      # Tải giờ bận
│   │   └── create_sample_data_if_not_exists() # Tạo dữ liệu mẫu
│   ├── errors.py                   # Các exception tùy chỉnh
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
├── .gitignore                     # Git ignore file
└── README.md                      # File này
```

## Phát triển

### Công nghệ sử dụng

- **Python 3.7+**: Ngôn ngữ lập trình chính
- **PyQt6**: Framework giao diện đồ họa
- **JSON**: Định dạng lưu trữ dữ liệu
- **Thuật toán Backtracking**: Tìm kiếm TKB hợp lệ

### Cấu trúc module

#### Core Modules

- **`models.py`**: 
  - Định nghĩa các class dữ liệu: `MonHoc`, `LopHoc`, `ThoiGianHoc`, `LichBan`
  - Hàm chuẩn hóa: `chuan_hoa_ma_lop()`, `chuan_hoa_ten_giao_vien()`
  - Validation dữ liệu với `ValidationError`
  
- **`scheduler.py`**: 
  - Logic tìm kiếm TKB: `tim_thoi_khoa_bieu()` (thuật toán đệ quy với backtracking)
  - Kiểm tra xung đột: `kiem_tra_trung_phong_hoc()`, `kiem_tra_trung_giao_vien()`, `kiem_tra_trung_trong_cung_mon()`
  - Xử lý ràng buộc: `update_bidirectional_constraints()`
  - Tối ưu hiệu suất với index và cache
  
- **`data_handler.py`**: 
  - Lưu/tải dữ liệu JSON: `save_data()`, `load_data()`
  - Quản lý môn đã học: `save_completed_courses()`, `load_completed_courses()`
  - Quản lý giờ bận: `save_busy_times()`, `load_busy_times()`
  - Tạo dữ liệu mẫu: `create_sample_data_if_not_exists()`
  - Atomic write với backup tự động
  
- **`constants.py`**: 
  - Các hằng số: tên thứ trong tuần, tên file dữ liệu
  - Giới hạn: `MAX_COURSES`, `MAX_RESULTS`, `SEARCH_TIMEOUT`
  - Validation: `MIN_THU`, `MAX_THU`, `MIN_TIET`, `MAX_TIET`

#### UI Modules (`ui/`)

- **`main_window.py`**: 
  - Cửa sổ chính và logic điều khiển toàn bộ ứng dụng
  - Quản lý menu, toolbar, và các widget chính
  - Xử lý sự kiện và tương tác người dùng
  - Thread tìm kiếm TKB để tránh block UI
  
- **`schedule_widget.py`**: 
  - Widget hiển thị lịch dạng lưới với ngày tháng
  - Hiển thị môn học và giờ bận với màu sắc khác biệt
  - Hỗ trợ click vào ô để thêm lớp học nhanh
  - Tooltip hiển thị thông tin chi tiết
  
- **`dialogs.py`**: 
  - Các dialog nhập liệu: `SubjectDialog`, `ClassDialog`
  - Dialog quản lý: `CompletedCoursesDialog`, `ViewCompletedCoursesDialog`
  - Dialog chỉnh sửa: `EditAllSubjectsDialog`, `EditAllClassesDialog`
  
- **`course_classes_dialog.py`**: 
  - Dialog quản lý lớp học của một môn cụ thể
  - Hiển thị và phân loại lớp học theo loại
  
- **`custom_checkbox.py`**: 
  - Checkbox tùy chỉnh với khả năng click vào text
  - Hỗ trợ tooltip và các tùy chọn hiển thị
  
- **`theme.py`**: 
  - Quản lý theme sáng/tối
  - Định nghĩa màu sắc và style cho từng theme

### Entry Point

- **`main.py`**: Khởi tạo QApplication và MainWindow, chạy ứng dụng

### Chạy với auto-reload (Dành cho phát triển)

Để tự động reload khi có thay đổi code:

```bash
# Cài đặt watchdog (nếu chưa có)
pip install watchdog

# Chạy với auto-reload
watchmedo auto-restart --patterns="*.py" --recursive -- python main.py
```

## Xử lý sự cố

### Lỗi khi cài đặt

**Lỗi: "pip is not recognized"**
- Đảm bảo Python đã được cài đặt và thêm vào PATH
- Thử dùng `python -m pip` thay vì `pip`

**Lỗi: "No module named 'PyQt6'"**
- Đảm bảo đã kích hoạt virtual environment
- Chạy lại: `pip install -r requirements.txt`

**Lỗi đường dẫn dài trên Windows**
- Sử dụng virtual environment (venv)
- Hoặc di chuyển dự án vào thư mục có đường dẫn ngắn hơn

**Lỗi quyền truy cập khi cài đặt**
- Thử thêm `--user`: `pip install --user PyQt6`
- Hoặc chạy terminal với quyền Administrator

### Lỗi khi chạy ứng dụng

**Ứng dụng không khởi động**
- Kiểm tra Python version: `python --version` (cần >= 3.7)
- Kiểm tra PyQt6 đã được cài đặt: `pip list | grep PyQt6`
- Xem lỗi chi tiết trong terminal/command prompt

**Giao diện bị lỗi hoặc không hiển thị**
- Thử chạy lại ứng dụng
- Kiểm tra file dữ liệu JSON có bị hỏng không
- Xóa các file JSON và để ứng dụng tạo lại file mẫu

**Không tìm thấy TKB hợp lệ**
- Kiểm tra xem có môn học nào được chọn không
- Kiểm tra xem các môn học có lớp học không
- Kiểm tra xem có quá nhiều giờ bận không
- Kiểm tra môn tiên quyết đã được thêm vào danh sách môn đã học chưa
- Kiểm tra xem có quá nhiều môn bắt buộc không (có thể không có TKB thỏa mãn)

**Import TKB không hoạt động**
- Đảm bảo file TKB là file text (.txt) đã được lưu từ ứng dụng
- Kiểm tra các lớp học trong file TKB đã tồn tại trong hệ thống chưa
- Kiểm tra định dạng file có đúng không

### Vấn đề về dữ liệu

**Mất dữ liệu**
- Kiểm tra các file JSON trong thư mục chạy ứng dụng
- Kiểm tra file backup (`.bak`) nếu có
- Nếu file bị hỏng, có thể xóa và để ứng dụng tạo lại file mẫu
- Nên backup các file JSON thường xuyên

**Dữ liệu không được lưu**
- Kiểm tra quyền ghi file trong thư mục chạy ứng dụng
- Đảm bảo không có chương trình khác đang mở file JSON
- Thử lưu thủ công từ menu File > Lưu dữ liệu môn học

### Lưu ý quan trọng

#### Về dữ liệu

- **File dữ liệu**: Tất cả file dữ liệu được lưu trong thư mục chạy ứng dụng
  - `data_TKB_pro.json`: Lưu môn học và lớp học
  - `completed_courses.json`: Lưu danh sách môn đã học
  - `busy_times.json`: Lưu danh sách giờ bận
- **Tự động lưu**: Dữ liệu được lưu tự động khi thêm/sửa/xóa
- **Backup tự động**: File được backup thành `.bak` trước khi ghi mới

#### Về thời gian

- **Ngày trong tuần**: Hỗ trợ 7 ngày (Thứ 2 = 2, Thứ 3 = 3, ..., Chủ Nhật = 8)
- **Tiết học**: Mỗi ngày có 12 tiết:
  - Tiết 1-5: 7h-11h (sáng)
  - Tiết 6-12: 13h-17h (chiều)
- **Giờ bận**: Được chuyển đổi tự động sang tiết học khi thêm

#### Về logic kiểm tra

**Khi thêm lớp học:**
- Chỉ kiểm tra xung đột **trong cùng một môn**:
  - Trùng phòng học (nếu cùng thời gian)
  - Trùng giáo viên (nếu cùng thời gian)
  - Trùng lịch học (nếu cùng thời gian)

**Khi tìm TKB:**
- Kiểm tra xung đột **giữa tất cả các môn đã chọn**:
  - Trùng lịch học giữa các môn khác nhau
  - Trùng giáo viên (một giáo viên không thể dạy nhiều lớp cùng lúc)
  - Trùng với giờ bận
  - Môn tiên quyết phải có trong danh sách môn đã học
  - Tất cả môn bắt buộc phải có trong TKB

**Quy tắc chung:**
- **Phòng học**: Có thể được sử dụng bởi nhiều lớp nếu không trùng giờ (giữa các môn khác nhau)
- **Giáo viên**: Không thể dạy nhiều lớp cùng lúc (giữa các môn)
- **Môn tiên quyết**: Phải có trong danh sách môn đã học
- **Môn đã học**: Không thể chọn trong danh sách môn học

## Phiên bản

**Version 3.0.0** - Phiên bản hiện tại

### Các tính năng chính trong phiên bản này:

#### Tính năng mới
- ✅ Import TKB từ file text
- ✅ Chuẩn hóa tự động định dạng mã lớp và tên giáo viên
- ✅ Quản lý môn đã học với giao diện riêng
- ✅ Chế độ sáng/tối với lưu cài đặt tự động
- ✅ Thread tìm kiếm TKB để tránh block UI
- ✅ Atomic write với backup tự động

#### Cải thiện
- ✅ Kiểm tra trùng phòng học và giáo viên chính xác hơn
- ✅ Cải thiện hiển thị giờ bận trên lịch
- ✅ Tối ưu logic kiểm tra xung đột với index và cache
- ✅ Cải thiện giao diện và trải nghiệm người dùng
- ✅ Thêm menu và shortcuts tiện lợi
- ✅ Giới hạn tìm kiếm để đảm bảo hiệu suất

#### Sửa lỗi
- ✅ Sửa các lỗi liên quan đến xử lý dữ liệu
- ✅ Cải thiện xử lý lỗi và thông báo
- ✅ Sửa lỗi validation và kiểm tra xung đột
