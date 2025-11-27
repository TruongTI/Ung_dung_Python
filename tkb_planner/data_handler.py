"""
Xử lý lưu và tải dữ liệu từ file JSON
"""

import json
import os
from PyQt6.QtWidgets import QMessageBox

from PyQt6.QtCore import QTime

from .constants import DATA_FILE, COMPLETED_COURSES_FILE, BUSY_TIMES_FILE
from .models import MonHoc, LopHoc, ThoiGianHoc, LichBan


def save_data(all_courses_dict):
    """
    Lưu dữ liệu môn học vào file JSON
    
    Args:
        all_courses_dict: Dictionary chứa các môn học (key: ma_mon, value: MonHoc)
    
    Returns:
        True nếu lưu thành công, False nếu có lỗi
    """
    try:
        data_to_save = {ma_mon: mon_hoc.to_dict() 
                       for ma_mon, mon_hoc in all_courses_dict.items()}
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        QMessageBox.critical(None, "Lỗi Lưu", f"Không thể lưu dữ liệu: {e}")
        return False


def load_data():
    """
    Tải dữ liệu môn học từ file JSON
    
    Returns:
        Dictionary chứa các môn học (key: ma_mon, value: MonHoc)
    """
    if not os.path.exists(DATA_FILE):
        return {}
    
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        loaded_courses = {}
        for ma_mon, mon_data in data.items():
            mon_hoc = MonHoc(
                mon_data['ma_mon'], 
                mon_data['ten_mon'], 
                mon_data.get('tien_quyet', []), 
                mon_data.get('color_hex')
            )
            for lop_data in mon_data.get('cac_lop_hoc', []):
                lop_hoc = LopHoc(
                    lop_data['ma_lop'], 
                    lop_data['ten_giao_vien'], 
                    lop_data['ma_mon'], 
                    lop_data['ten_mon'], 
                    lop_data.get('color_hex'),
                    lop_data.get('loai_lop', 'Lớp')  # Mặc định là "Lớp" nếu không có
                )
                for gio_data in lop_data.get('cac_khung_gio', []):
                    lop_hoc.them_khung_gio(
                        gio_data['thu'], 
                        gio_data['tiet_bat_dau'], 
                        gio_data['tiet_ket_thuc']
                    )
                mon_hoc.them_lop_hoc(lop_hoc)
            loaded_courses[ma_mon] = mon_hoc
        return loaded_courses
    except Exception as e:
        QMessageBox.critical(None, "Lỗi Tải", f"Không thể đọc file dữ liệu: {e}")
        return {}


def create_sample_data_if_not_exists():
    """Tạo file JSON trống nếu file dữ liệu chưa tồn tại"""
    if os.path.exists(DATA_FILE):
        return
    
    # Tạo file JSON trống với cấu trúc rỗng
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=4)
    except Exception as e:
        QMessageBox.critical(None, "Lỗi Tạo File", f"Không thể tạo file dữ liệu: {e}")


def save_completed_courses(completed_courses_list):
    """
    Lưu danh sách môn đã học vào file JSON
    
    Args:
        completed_courses_list: List các mã môn đã học
    
    Returns:
        True nếu lưu thành công, False nếu có lỗi
    """
    try:
        with open(COMPLETED_COURSES_FILE, 'w', encoding='utf-8') as f:
            json.dump(completed_courses_list, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        QMessageBox.critical(None, "Lỗi Lưu", f"Không thể lưu danh sách môn đã học: {e}")
        return False


def load_completed_courses():
    """
    Tải danh sách môn đã học từ file JSON
    
    Returns:
        List các mã môn đã học
    """
    if not os.path.exists(COMPLETED_COURSES_FILE):
        return []
    
    try:
        with open(COMPLETED_COURSES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Đảm bảo trả về list
        if isinstance(data, list):
            return data
        return []
    except Exception as e:
        QMessageBox.critical(None, "Lỗi Tải", f"Không thể đọc file môn đã học: {e}")
        return []


def save_busy_times(busy_times_list):
    """
    Lưu danh sách giờ bận vào file JSON
    
    Args:
        busy_times_list: List các đối tượng LichBan
    
    Returns:
        True nếu lưu thành công, False nếu có lỗi
    """
    try:
        data_to_save = []
        for busy_time in busy_times_list:
            data_to_save.append({
                'thu': busy_time.thu,
                'gio_bat_dau': busy_time.gio_bat_dau.toString('HH:mm'),
                'gio_ket_thuc': busy_time.gio_ket_thuc.toString('HH:mm'),
                'ly_do': busy_time.ly_do,
                'id': busy_time.id
            })
        with open(BUSY_TIMES_FILE, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        QMessageBox.critical(None, "Lỗi Lưu", f"Không thể lưu danh sách giờ bận: {e}")
        return False


def load_busy_times():
    """
    Tải danh sách giờ bận từ file JSON
    
    Returns:
        List các đối tượng LichBan
    """
    if not os.path.exists(BUSY_TIMES_FILE):
        return []
    
    try:
        with open(BUSY_TIMES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        busy_times = []
        for item in data:
            # Parse thời gian từ string "HH:mm"
            gio_bd_parts = item['gio_bat_dau'].split(':')
            gio_kt_parts = item['gio_ket_thuc'].split(':')
            gio_bat_dau = QTime(int(gio_bd_parts[0]), int(gio_bd_parts[1]))
            gio_ket_thuc = QTime(int(gio_kt_parts[0]), int(gio_kt_parts[1]))
            
            busy_time = LichBan(
                item['thu'],
                gio_bat_dau,
                gio_ket_thuc,
                item['ly_do'],
                item['id']
            )
            busy_times.append(busy_time)
        return busy_times
    except Exception as e:
        QMessageBox.critical(None, "Lỗi Tải", f"Không thể đọc file giờ bận: {e}")
        return []

