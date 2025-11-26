"""
Logic xử lý tìm kiếm và kiểm tra xung đột thời khóa biểu
"""

from .models import ThoiGianHoc, LichBan, LopHoc


def kiem_tra_xung_dot_gio(gio_A, gio_B):
    """Kiểm tra xem hai khung giờ có xung đột không"""
    if not gio_A or not gio_B or gio_A.thu != gio_B.thu:
        return False
    return not (gio_A.tiet_ket_thuc < gio_B.tiet_bat_dau or 
                gio_A.tiet_bat_dau > gio_B.tiet_ket_thuc)


def check_trung_lich(lop_A, lop_B_or_lich_ban):
    """Kiểm tra xem lớp A có trùng lịch với lớp B hoặc lịch bận không"""
    cac_khung_gio_B = []
    if isinstance(lop_B_or_lich_ban, LopHoc):
        cac_khung_gio_B = lop_B_or_lich_ban.cac_khung_gio
    elif isinstance(lop_B_or_lich_ban, LichBan):
        gio_ban_converted = lop_B_or_lich_ban.to_thoi_gian_hoc()
        if gio_ban_converted:
            cac_khung_gio_B = [gio_ban_converted]
    
    for gio_A in lop_A.cac_khung_gio:
        for gio_B in cac_khung_gio_B:
            if kiem_tra_xung_dot_gio(gio_A, gio_B):
                return True
    return False


def _kiem_tra_trung_voi_lich(lop_moi, lich_hien_tai, danh_sach_gio_ban):
    """Kiểm tra xem lớp mới có trùng với lịch hiện tại hoặc giờ bận không"""
    for lop_da_chon in lich_hien_tai:
        if check_trung_lich(lop_moi, lop_da_chon):
            return True
    for gio_ban in danh_sach_gio_ban:
        if check_trung_lich(lop_moi, gio_ban):
            return True
    return False


def _tim_kiem_de_quy(danh_sach_mon_hoc, mon_hoc_index, lich_hien_tai, ket_qua, danh_sach_gio_ban):
    """Hàm đệ quy để tìm tất cả các thời khóa biểu hợp lệ"""
    if mon_hoc_index == len(danh_sach_mon_hoc):
        ket_qua.append(list(lich_hien_tai))
        return
    
    mon_hien_tai = danh_sach_mon_hoc[mon_hoc_index]
    if not mon_hien_tai.cac_lop_hoc:
        _tim_kiem_de_quy(danh_sach_mon_hoc, mon_hoc_index + 1, lich_hien_tai, ket_qua, danh_sach_gio_ban)
        return
    
    for lop_hoc in mon_hien_tai.cac_lop_hoc:
        if not _kiem_tra_trung_voi_lich(lop_hoc, lich_hien_tai, danh_sach_gio_ban):
            lich_hien_tai.append(lop_hoc)
            _tim_kiem_de_quy(danh_sach_mon_hoc, mon_hoc_index + 1, lich_hien_tai, ket_qua, danh_sach_gio_ban)
            lich_hien_tai.pop()


def tim_thoi_khoa_bieu(danh_sach_mon_hoc, danh_sach_gio_ban, mon_bat_buoc):
    """
    Tìm tất cả các thời khóa biểu hợp lệ từ danh sách môn học
    
    Args:
        danh_sach_mon_hoc: Danh sách các môn học cần sắp xếp
        danh_sach_gio_ban: Danh sách các giờ bận (LichBan)
        mon_bat_buoc: Danh sách mã môn bắt buộc phải có trong TKB
    
    Returns:
        Tuple (ket_qua, error_msg): 
        - ket_qua: Danh sách các TKB hợp lệ (mỗi TKB là list các LopHoc)
        - error_msg: Thông báo lỗi nếu có (None nếu không có lỗi)
    """
    # Kiểm tra môn tiên quyết
    ma_mon_da_chon = {mon.ma_mon for mon in danh_sach_mon_hoc}
    for mon in danh_sach_mon_hoc:
        for mon_tien_quyet in mon.tien_quyet:
            if mon_tien_quyet not in ma_mon_da_chon:
                error_msg = (f"Lỗi: Môn '{mon.ten_mon} ({mon.ma_mon})' yêu cầu "
                           f"phải học môn tiên quyết '{mon_tien_quyet}' trước.")
                return [], error_msg
    
    # Tìm tất cả các TKB hợp lệ
    ket_qua_thuan = []
    _tim_kiem_de_quy(danh_sach_mon_hoc, 0, [], ket_qua_thuan, danh_sach_gio_ban)
    
    # Nếu không có môn bắt buộc, trả về tất cả kết quả
    if not mon_bat_buoc:
        return ket_qua_thuan, None
    
    # Lọc các TKB có chứa tất cả môn bắt buộc
    ket_qua_da_loc = []
    ma_mon_bat_buoc = set(mon_bat_buoc)
    for tkb in ket_qua_thuan:
        ma_mon_trong_tkb = {lop.ma_mon for lop in tkb}
        if ma_mon_bat_buoc.issubset(ma_mon_trong_tkb):
            ket_qua_da_loc.append(tkb)
    
    return ket_qua_da_loc, None

