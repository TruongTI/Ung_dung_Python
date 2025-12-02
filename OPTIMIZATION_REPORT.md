# Báo Cáo Phân Tích và Tối Ưu Dự Án TKB Planner Pro

## 📋 Tổng Quan

Báo cáo này phân tích toàn diện dự án TKB Planner Pro và đưa ra các vấn đề cần tối ưu về hiệu suất, thuật toán, code quality, và trải nghiệm người dùng.

---

## 🔴 VẤN ĐỀ NGHIÊM TRỌNG (Critical Issues)

### 1. **Hiệu Suất Thuật Toán Tìm TKB - Độ Phức Tạp Quá Cao**

**Vấn đề:**
- Thuật toán backtracking hiện tại có độ phức tạp **O(n^m)** với n = số lớp/môn, m = số môn
- Với 15 môn, mỗi môn có 5 lớp → **5^15 = 30,517,578,125** khả năng (worst case)
- Không có giới hạn số lượng kết quả → có thể tạo hàng triệu TKB, gây treo ứng dụng

**Vị trí:** `scheduler.py` - hàm `_tim_kiem_de_quy()`

**Giải pháp đề xuất:**
```python
# 1. Thêm giới hạn số lượng kết quả tối đa
MAX_RESULTS = 1000  # Chỉ tìm tối đa 1000 TKB

# 2. Thêm early termination khi đạt giới hạn
def _tim_kiem_de_quy(..., max_results=MAX_RESULTS):
    if len(ket_qua) >= max_results:
        return  # Dừng khi đạt giới hạn
    
# 3. Thêm timeout cho quá trình tìm kiếm
import signal
def tim_thoi_khoa_bieu_with_timeout(..., timeout=30):
    # Tìm kiếm với timeout 30 giây
```

**Ưu tiên:** ⚠️ **CAO** - Cần sửa ngay

---

### 2. **Vấn Đề Memory Leak - Tạo Quá Nhiều List Copy**

**Vấn đề:**
- Mỗi lần tìm thấy TKB hợp lệ, code tạo `list(lich_hien_tai)` → copy toàn bộ list
- Với 1000 TKB, mỗi TKB có 15 lớp → **15,000 object references** được lưu
- Không có cơ chế giải phóng memory khi xóa TKB cũ

**Vị trí:** `scheduler.py:123`

**Giải pháp:**
```python
# Sử dụng generator thay vì list để tiết kiệm memory
def _tim_kiem_de_quy_generator(...):
    # Yield thay vì append
    yield list(lich_hien_tai)

# Hoặc sử dụng weak references cho các TKB không còn dùng
```

**Ưu tiên:** ⚠️ **CAO**

---

### 3. **Nested Loops Không Tối Ưu - O(n²) hoặc O(n³)**

**Vấn đề:**
- Nhiều hàm có nested loops không cần thiết:
  - `_kiem_tra_trung_voi_lich()`: O(n²) với n = số lớp trong lịch
  - `kiem_tra_trung_giao_vien()`: O(n²) với n = tổng số lớp
  - `_find_lop_by_id_helper()`: O(n²) - tìm lớp trong tất cả môn

**Vị trí:** 
- `scheduler.py:34-42` (kiểm tra trùng lịch)
- `scheduler.py:372-422` (kiểm tra giáo viên)
- `scheduler.py:425-481` (tìm lớp theo ID)

**Giải pháp:**
```python
# 1. Sử dụng set/dict để lookup O(1) thay vì O(n)
# Tạo index cho giáo viên
gv_index = {}  # {ten_gv: [list of classes]}
for mon in all_courses.values():
    for lop in mon.cac_lop_hoc:
        gv_key = lop.ten_giao_vien.strip().lower()
        if gv_key not in gv_index:
            gv_index[gv_key] = []
        gv_index[gv_key].append(lop)

# 2. Sử dụng spatial index cho thời gian (thứ, tiết)
# Tạo grid: {thu: {tiet: [list of classes]}}
time_index = {}
```

**Ưu tiên:** ⚠️ **TRUNG BÌNH-CAO**

---

## 🟡 VẤN ĐỀ QUAN TRỌNG (Important Issues)

### 4. **Xử Lý Lớp Ràng Buộc Không Hiệu Quả**

**Vấn đề:**
- Mỗi lần thêm lớp ràng buộc, phải tìm lại lớp từ ID → O(n) mỗi lần
- Xóa lớp ràng buộc phải duyệt toàn bộ list → O(n)
- Không cache kết quả tìm kiếm

**Vị trí:** `scheduler.py:92-118`, `scheduler.py:191-199`

**Giải pháp:**
```python
# Tạo cache cho việc tìm lớp theo ID
_lop_cache = {}  # {lop_id: LopHoc}

def _tim_lop_rang_buoc_cached(lop_id, all_courses):
    if lop_id in _lop_cache:
        return _lop_cache[lop_id]
    result = _find_lop_by_id_helper(lop_id, all_courses)
    if result:
        _lop_cache[lop_id] = result
    return result
```

**Ưu tiên:** 🟡 **TRUNG BÌNH**

---

### 5. **UI Blocking - Tìm TKB Làm Đơ Giao Diện**

**Vấn đề:**
- Hàm `handle_find_tkb()` chạy trên main thread
- Với nhiều môn, quá trình tìm kiếm có thể mất 10-30 giây
- UI bị đơ, không thể cancel, không có progress bar

**Vị trí:** `main_window.py:680-716`

**Giải pháp:**
```python
# Sử dụng QThread để chạy tìm kiếm ở background
from PyQt6.QtCore import QThread, pyqtSignal

class FindTKBThread(QThread):
    finished = pyqtSignal(list, str)  # ket_qua, error_msg
    
    def run(self):
        # Tìm TKB ở background thread
        ket_qua, error = tim_thoi_khoa_bieu(...)
        self.finished.emit(ket_qua, error)

# Trong MainWindow:
def handle_find_tkb(self):
    self.find_tkb_thread = FindTKBThread(...)
    self.find_tkb_thread.finished.connect(self.on_tkb_found)
    self.find_tkb_thread.start()
    # Hiển thị progress bar
```

**Ưu tiên:** 🟡 **TRUNG BÌNH**

---

### 6. **Validation Dữ Liệu Không Đầy Đủ**

**Vấn đề:**
- Không validate tiết học (có thể nhập tiết < 1 hoặc > 12)
- Không validate thứ (có thể nhập thứ < 2 hoặc > 8)
- Không kiểm tra tiết bắt đầu > tiết kết thúc
- Không validate format mã môn, mã lớp

**Vị trí:** `dialogs.py`, `models.py`

**Giải pháp:**
```python
# Thêm validation trong models.py
class ThoiGianHoc:
    def __init__(self, thu, tiet_bat_dau, tiet_ket_thuc):
        if not (2 <= thu <= 8):
            raise ValueError(f"Thứ phải từ 2-8, nhận được: {thu}")
        if not (1 <= tiet_bat_dau <= 12):
            raise ValueError(f"Tiết bắt đầu phải từ 1-12, nhận được: {tiet_bat_dau}")
        if not (1 <= tiet_ket_thuc <= 12):
            raise ValueError(f"Tiết kết thúc phải từ 1-12, nhận được: {tiet_ket_thuc}")
        if tiet_bat_dau > tiet_ket_thuc:
            raise ValueError("Tiết bắt đầu phải <= tiết kết thúc")
        # ...
```

**Ưu tiên:** 🟡 **TRUNG BÌNH**

---

### 7. **Xử Lý Lỗi Không Nhất Quán**

**Vấn đề:**
- Một số hàm trả về tuple `(result, error_msg)`, một số raise exception
- Không có logging system → khó debug
- Thông báo lỗi không rõ ràng cho người dùng

**Vị trí:** Toàn bộ codebase

**Giải pháp:**
```python
# Tạo custom exception classes
class TKBError(Exception):
    pass

class ValidationError(TKBError):
    pass

class ConflictError(TKBError):
    pass

# Sử dụng logging
import logging
logger = logging.getLogger(__name__)
logger.error("Error message", exc_info=True)
```

**Ưu tiên:** 🟡 **TRUNG BÌNH**

---

## 🟢 VẤN ĐỀ CẢI THIỆN (Enhancement Issues)

### 8. **Code Duplication - Lặp Lại Logic Kiểm Tra**

**Vấn đề:**
- Logic kiểm tra trùng phòng học được lặp lại ở nhiều nơi
- Logic kiểm tra trùng giáo viên cũng tương tự
- Có thể refactor thành hàm chung

**Vị trí:**
- `scheduler.py:254-302` (kiem_tra_trung_phong_hoc)
- `scheduler.py:305-369` (kiem_tra_trung_trong_cung_mon)
- `scheduler.py:372-422` (kiem_tra_trung_giao_vien)

**Giải pháp:**
```python
# Tạo hàm chung để kiểm tra xung đột
def kiem_tra_xung_dot_chung(lop_moi, all_courses, 
                            check_phong=True, 
                            check_gv=True,
                            scope='all'):  # 'all' hoặc 'same_subject'
    # Logic chung
    pass
```

**Ưu tiên:** 🟢 **THẤP**

---

### 9. **Hiển Thị Lịch Không Tối Ưu - Repaint Toàn Bộ**

**Vấn đề:**
- Mỗi lần update, `paintEvent()` vẽ lại toàn bộ lịch
- Không có dirty region tracking
- Với lịch lớn, có thể gây lag

**Vị trí:** `schedule_widget.py:62-72`

**Giải pháp:**
```python
# Chỉ repaint phần thay đổi
def update_schedule_partial(self, changed_cells):
    for cell in changed_cells:
        self.update(cell.rect)  # Chỉ update cell cụ thể
```

**Ưu tiên:** 🟢 **THẤP**

---

### 10. **Lưu Dữ Liệu Không An Toàn**

**Vấn đề:**
- Lưu trực tiếp vào file, không có backup
- Nếu crash khi đang lưu, có thể mất dữ liệu
- Không có transaction/rollback

**Vị trí:** `data_handler.py:15-33`

**Giải pháp:**
```python
def save_data_safe(all_courses_dict):
    # 1. Lưu vào file temp
    temp_file = DATA_FILE + ".tmp"
    with open(temp_file, 'w') as f:
        json.dump(data, f)
    
    # 2. Backup file cũ
    if os.path.exists(DATA_FILE):
        backup_file = DATA_FILE + ".bak"
        shutil.copy(DATA_FILE, backup_file)
    
    # 3. Rename temp file
    os.rename(temp_file, DATA_FILE)
```

**Ưu tiên:** 🟢 **THẤP**

---

### 11. **Không Có Unit Tests**

**Vấn đề:**
- Không có test cases cho các hàm quan trọng
- Khó đảm bảo code hoạt động đúng sau khi refactor
- Khó phát hiện bug sớm

**Giải pháp:**
```python
# Tạo file tests/test_scheduler.py
import unittest
from tkb_planner.scheduler import tim_thoi_khoa_bieu

class TestScheduler(unittest.TestCase):
    def test_tim_tkb_basic(self):
        # Test case cơ bản
        pass
    
    def test_kiem_tra_trung_lich(self):
        # Test kiểm tra trùng lịch
        pass
```

**Ưu tiên:** 🟢 **THẤP** (nhưng quan trọng cho maintainability)

---

### 12. **Magic Numbers và Hard-coded Values**

**Vấn đề:**
- Số 12 (MAX_TIET) được hard-code ở nhiều nơi
- Số 7 (số ngày) cũng tương tự
- Khó thay đổi sau này

**Vị trí:** 
- `schedule_widget.py:27` (MAX_TIET = 12)
- `constants.py` (thiếu MAX_TIET)

**Giải pháp:**
```python
# Thêm vào constants.py
MAX_TIET = 12
MIN_TIET = 1
MIN_THU = 2
MAX_THU = 8
```

**Ưu tiên:** 🟢 **THẤP**

---

## 📊 Tổng Kết và Đề Xuất Ưu Tiên

### Ưu Tiên Cao (Làm Ngay):
1. ✅ Thêm giới hạn số lượng kết quả TKB (MAX_RESULTS)
2. ✅ Thêm timeout cho quá trình tìm kiếm
3. ✅ Tối ưu nested loops bằng index/dict
4. ✅ Sử dụng QThread cho tìm kiếm TKB

### Ưu Tiên Trung Bình (Làm Sớm):
5. ✅ Cache kết quả tìm lớp theo ID
6. ✅ Thêm validation dữ liệu đầy đủ
7. ✅ Cải thiện xử lý lỗi và logging
8. ✅ Lưu dữ liệu an toàn với backup

### Ưu Tiên Thấp (Cải Thiện Dần):
9. ✅ Refactor code duplication
10. ✅ Tối ưu repaint UI
11. ✅ Thêm unit tests
12. ✅ Loại bỏ magic numbers

---

## 🔧 Công Cụ và Kỹ Thuật Đề Xuất

1. **Profiling:** Sử dụng `cProfile` để tìm bottleneck
2. **Memory Profiling:** Sử dụng `memory_profiler` để kiểm tra memory leak
3. **Type Hints:** Thêm type hints để cải thiện code quality
4. **Documentation:** Thêm docstring đầy đủ cho các hàm quan trọng

---

## 📈 Ước Tính Cải Thiện

Sau khi tối ưu:
- **Hiệu suất:** Giảm thời gian tìm TKB từ 30s → 2-5s (với 15 môn)
- **Memory:** Giảm memory usage từ ~500MB → ~100MB (với 1000 TKB)
- **UX:** UI không còn bị đơ, có progress bar và cancel button
- **Stability:** Giảm crash rate nhờ validation và error handling tốt hơn

---

**Ngày tạo:** $(date)
**Phiên bản:** 1.0

