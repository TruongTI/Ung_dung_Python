"""
Xử lý lưu và tải dữ liệu từ file JSON
"""

import json
import os
from PyQt6.QtWidgets import QMessageBox

from .constants import DATA_FILE, COMPLETED_COURSES_FILE
from .models import MonHoc, LopHoc, ThoiGianHoc


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
                    lop_data.get('color_hex')
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
    """Tạo dữ liệu mẫu nếu file dữ liệu chưa tồn tại"""
    if os.path.exists(DATA_FILE):
        return
    
    all_courses = {}
    
    # Tạo môn Giải tích 1
    mon_giai_tich = MonHoc("MI1111", "Giải tích 1", color_hex="#ADD8E6")
    lop_GT_L05 = LopHoc("L05", "GV. Lê Văn C", "MI1111", "Giải tích 1")
    lop_GT_L05.them_khung_gio(2, 3, 5)
    lop_GT_L06 = LopHoc("L06", "GV. Phạm Dũng", "MI1111", "Giải tích 1")
    lop_GT_L06.them_khung_gio(3, 1, 3)
    mon_giai_tich.them_lop_hoc(lop_GT_L05)
    mon_giai_tich.them_lop_hoc(lop_GT_L06)
    all_courses["MI1111"] = mon_giai_tich
    
    # Tạo môn Tin học đại cương
    mon_tin_hoc = MonHoc("IT1110", "Tin học đại cương", tien_quyet=["MI1111"], color_hex="#90EE90")
    lop_L01 = LopHoc("L01", "GV. Nguyễn Văn A", "IT1110", "Tin học đại cương")
    lop_L01.them_khung_gio(2, 1, 3)
    lop_L01.them_khung_gio(4, 1, 2)
    lop_L02 = LopHoc("L02", "GV. Trần Thị B", "IT1110", "Tin học đại cương")
    lop_L02.them_khung_gio(3, 7, 9)
    lop_L02.them_khung_gio(5, 7, 8)
    mon_tin_hoc.them_lop_hoc(lop_L01)
    mon_tin_hoc.them_lop_hoc(lop_L02)
    all_courses["IT1110"] = mon_tin_hoc
    
    save_data(all_courses)
    QMessageBox.information(
        None, 
        "Tạo dữ liệu", 
        f"Chưa có file dữ liệu. Đã tạo file mẫu tại {DATA_FILE}"
    )


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

