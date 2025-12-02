"""
Logic xử lý tìm kiếm và kiểm tra xung đột thời khóa biểu
"""

from .models import ThoiGianHoc, LichBan, LopHoc
from .constants import TEN_THU_TRONG_TUAN


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


def _tim_lop_rang_buoc(lop_id, all_courses, lop_hien_tai=None):
    """Tìm lớp học từ ID (ma_mon-ma_lop)
    
    Nếu có nhiều lớp cùng ID, ưu tiên lớp không trùng giờ với lop_hien_tai (nếu có)
    """
    if not all_courses:
        return None
    
    cac_lop_cung_id = []
    for ma_mon, mon_hoc in all_courses.items():
        for lop in mon_hoc.cac_lop_hoc:
            if lop.get_id() == lop_id:
                cac_lop_cung_id.append(lop)
    
    if not cac_lop_cung_id:
        return None
    
    # Nếu chỉ có 1 lớp, trả về lớp đó
    if len(cac_lop_cung_id) == 1:
        return cac_lop_cung_id[0]
    
    # Nếu có nhiều lớp cùng ID, ưu tiên lớp không trùng giờ với lop_hien_tai
    if lop_hien_tai:
        for lop in cac_lop_cung_id:
            if not check_trung_lich(lop_hien_tai, lop):
                return lop  # Trả về lớp không trùng giờ
    
    # Nếu không có lớp nào không trùng giờ, hoặc không có lop_hien_tai, trả về lớp đầu tiên
    return cac_lop_cung_id[0]

def _them_lop_rang_buoc(lop_hoc, lich_hien_tai, danh_sach_gio_ban, all_courses):
    """Thêm các lớp ràng buộc vào lịch hiện tại nếu có"""
    if not lop_hoc.lop_rang_buoc or not all_courses:
        return True  # Không có ràng buộc, OK
    
    # Kiểm tra và thêm các lớp ràng buộc
    for rang_buoc_id in lop_hoc.lop_rang_buoc:
        # Tìm lớp ràng buộc (truyền lop_hoc để ưu tiên lớp không trùng giờ)
        lop_rang_buoc = _tim_lop_rang_buoc(rang_buoc_id, all_courses, lop_hien_tai=lop_hoc)
        if not lop_rang_buoc:
            continue  # Lớp ràng buộc không tồn tại, bỏ qua
        
        # Kiểm tra xem lớp ràng buộc đã có trong lịch chưa (so sánh bằng object reference)
        lop_da_co = False
        for lop_trong_lich in lich_hien_tai:
            if lop_trong_lich is lop_rang_buoc:
                lop_da_co = True
                break
        
        # Nếu chưa có, kiểm tra xung đột và thêm vào
        if not lop_da_co:
            # Kiểm tra xung đột với lịch hiện tại
            if _kiem_tra_trung_voi_lich(lop_rang_buoc, lich_hien_tai, danh_sach_gio_ban):
                return False  # Có xung đột, không thể thêm lớp ràng buộc
            lich_hien_tai.append(lop_rang_buoc)
    
    return True  # Đã thêm tất cả lớp ràng buộc thành công

def _tim_kiem_de_quy(danh_sach_mon_hoc, mon_hoc_index, lich_hien_tai, ket_qua, danh_sach_gio_ban, all_courses=None):
    """Hàm đệ quy để tìm tất cả các thời khóa biểu hợp lệ"""
    if mon_hoc_index == len(danh_sach_mon_hoc):
        ket_qua.append(list(lich_hien_tai))
        return
    
    mon_hien_tai = danh_sach_mon_hoc[mon_hoc_index]
    if not mon_hien_tai.cac_lop_hoc:
        _tim_kiem_de_quy(danh_sach_mon_hoc, mon_hoc_index + 1, lich_hien_tai, ket_qua, danh_sach_gio_ban, all_courses)
        return
    
    # Kiểm tra xem môn học này đã có lớp nào trong lịch chưa (do được thêm như một lớp ràng buộc)
    # Nếu có rồi, bỏ qua môn học này và tiếp tục với môn tiếp theo
    mon_da_co_lop_trong_lich = False
    for lop_trong_lich in lich_hien_tai:
        if lop_trong_lich.ma_mon == mon_hien_tai.ma_mon:
            mon_da_co_lop_trong_lich = True
            break
    
    # Nếu môn học đã có lớp trong lịch, bỏ qua và tiếp tục với môn tiếp theo
    if mon_da_co_lop_trong_lich:
        _tim_kiem_de_quy(danh_sach_mon_hoc, mon_hoc_index + 1, lich_hien_tai, ket_qua, danh_sach_gio_ban, all_courses)
        return
    
    for lop_hoc in mon_hien_tai.cac_lop_hoc:
        if not _kiem_tra_trung_voi_lich(lop_hoc, lich_hien_tai, danh_sach_gio_ban):
            # Thêm lớp học vào lịch
            lich_hien_tai.append(lop_hoc)
            
            # Thêm các lớp ràng buộc nếu có
            lop_rang_buoc_da_them = []
            if _them_lop_rang_buoc(lop_hoc, lich_hien_tai, danh_sach_gio_ban, all_courses):
                # Đã thêm thành công các lớp ràng buộc, tiếp tục đệ quy
                _tim_kiem_de_quy(danh_sach_mon_hoc, mon_hoc_index + 1, lich_hien_tai, ket_qua, danh_sach_gio_ban, all_courses)
            else:
                # Không thể thêm lớp ràng buộc do xung đột, bỏ qua lớp này
                pass
            
            # Xóa lớp học và các lớp ràng buộc đã thêm
            lich_hien_tai.pop()  # Xóa lớp chính
            # Xóa các lớp ràng buộc đã thêm (so sánh bằng object reference)
            if lop_hoc.lop_rang_buoc and all_courses:
                for rang_buoc_id in lop_hoc.lop_rang_buoc:
                    lop_rang_buoc = _tim_lop_rang_buoc(rang_buoc_id, all_courses)
                    if lop_rang_buoc:
                        # Tìm và xóa bằng object reference
                        for i in range(len(lich_hien_tai) - 1, -1, -1):
                            if lich_hien_tai[i] is lop_rang_buoc:
                                lich_hien_tai.pop(i)
                                break


def tim_thoi_khoa_bieu(danh_sach_mon_hoc, danh_sach_gio_ban, mon_bat_buoc, completed_courses=None, all_courses=None):
    """
    Tìm tất cả các thời khóa biểu hợp lệ từ danh sách môn học
    
    Args:
        danh_sach_mon_hoc: Danh sách các môn học cần sắp xếp
        danh_sach_gio_ban: Danh sách các giờ bận (LichBan)
        mon_bat_buoc: Danh sách mã môn bắt buộc phải có trong TKB
        completed_courses: Danh sách mã môn đã học (môn tiên quyết)
        all_courses: Dictionary chứa tất cả các môn học (để tìm lớp ràng buộc)
    
    Returns:
        Tuple (ket_qua, error_msg): 
        - ket_qua: Danh sách các TKB hợp lệ (mỗi TKB là list các LopHoc)
        - error_msg: Thông báo lỗi nếu có (None nếu không có lỗi)
    """
    # Kiểm tra môn tiên quyết - môn tiên quyết phải có trong danh sách môn đã học
    completed_courses_set = set(completed_courses) if completed_courses else set()
    for mon in danh_sach_mon_hoc:
        for mon_tien_quyet in mon.tien_quyet:
            if mon_tien_quyet not in completed_courses_set:
                error_msg = (f"Lỗi: Môn '{mon.ten_mon} ({mon.ma_mon})' yêu cầu "
                           f"phải học môn tiên quyết '{mon_tien_quyet}' trước. "
                           f"Vui lòng thêm môn '{mon_tien_quyet}' vào danh sách môn đã học.")
                return [], error_msg
    
    # Tìm tất cả các TKB hợp lệ (truyền all_courses để xử lý ràng buộc)
    ket_qua_thuan = []
    _tim_kiem_de_quy(danh_sach_mon_hoc, 0, [], ket_qua_thuan, danh_sach_gio_ban, all_courses)
    
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


def kiem_tra_trung_phong_hoc(lop_moi, all_courses, exclude_lop_id=None):
    """
    Kiểm tra xem lớp mới có trùng phòng học và trùng giờ với lớp khác không
    
    Args:
        lop_moi: Lớp học mới cần kiểm tra
        all_courses: Dictionary chứa tất cả các môn học (key: ma_mon, value: MonHoc)
        exclude_lop_id: ID của lớp cần loại trừ khỏi kiểm tra (khi sửa lớp)
    
    Returns:
        Tuple (is_valid, error_msg):
        - is_valid: True nếu không trùng, False nếu trùng
        - error_msg: Thông báo lỗi nếu trùng (None nếu không trùng)
    """
    # Tìm tất cả các lớp có cùng phòng học (ma_lop)
    cac_lop_cung_phong = []
    for mon_hoc in all_courses.values():
        for lop in mon_hoc.cac_lop_hoc:
            # Bỏ qua lớp hiện tại nếu đang sửa
            if exclude_lop_id and lop.get_id() == exclude_lop_id:
                continue
            if lop.ma_lop == lop_moi.ma_lop:
                cac_lop_cung_phong.append(lop)
    
    # Nếu không có lớp nào cùng phòng, cho phép thêm
    if not cac_lop_cung_phong:
        return True, None
    
    # Kiểm tra xem có trùng giờ trong cùng 1 ngày không
    cac_thu_trung = []
    for lop_cung_phong in cac_lop_cung_phong:
        for gio_moi in lop_moi.cac_khung_gio:
            for gio_cu in lop_cung_phong.cac_khung_gio:
                # Nếu cùng thứ và trùng giờ
                if gio_moi.thu == gio_cu.thu:
                    if kiem_tra_xung_dot_gio(gio_moi, gio_cu):
                        ten_thu = TEN_THU_TRONG_TUAN.get(gio_moi.thu, f"Thứ {gio_moi.thu}")
                        if ten_thu not in cac_thu_trung:
                            cac_thu_trung.append(ten_thu)
    
    # Nếu có trùng giờ, báo lỗi
    if cac_thu_trung:
        error_msg = (f"Lỗi: Phòng học '{lop_moi.ma_lop}' đã được sử dụng vào "
                    f"{', '.join(cac_thu_trung)}. "
                    f"Vui lòng chọn phòng khác hoặc thay đổi thời gian học.")
        return False, error_msg
    
    # Không trùng giờ, cho phép thêm
    return True, None


def kiem_tra_trung_trong_cung_mon(lop_moi, mon_hoc, exclude_lop_id=None):
    """
    Kiểm tra xem lớp mới có trùng phòng học, giáo viên và trùng giờ với lớp khác trong cùng môn không
    (Chỉ kiểm tra trong cùng một môn - dùng khi thêm lớp trong area lớp học)
    
    Args:
        lop_moi: Lớp học mới cần kiểm tra
        mon_hoc: Môn học chứa lớp mới
        exclude_lop_id: ID của lớp cần loại trừ khỏi kiểm tra (khi sửa lớp)
    
    Returns:
        Tuple (is_valid, error_msg):
        - is_valid: True nếu không trùng, False nếu trùng
        - error_msg: Thông báo lỗi nếu trùng (None nếu không trùng)
    """
    # Kiểm tra trùng phòng học trong cùng môn
    cac_lop_cung_phong = []
    cac_lop_cung_gv = []
    
    for lop in mon_hoc.cac_lop_hoc:
        # Bỏ qua lớp hiện tại nếu đang sửa
        if exclude_lop_id and lop.get_id() == exclude_lop_id:
            continue
        
        if lop.ma_lop == lop_moi.ma_lop:
            cac_lop_cung_phong.append(lop)
        
        if lop.ten_giao_vien.strip().lower() == lop_moi.ten_giao_vien.strip().lower():
            cac_lop_cung_gv.append(lop)
    
    # Kiểm tra trùng phòng học và trùng giờ
    cac_thu_trung_phong = []
    for lop_cung_phong in cac_lop_cung_phong:
        for gio_moi in lop_moi.cac_khung_gio:
            for gio_cu in lop_cung_phong.cac_khung_gio:
                if gio_moi.thu == gio_cu.thu:
                    if kiem_tra_xung_dot_gio(gio_moi, gio_cu):
                        ten_thu = TEN_THU_TRONG_TUAN.get(gio_moi.thu, f"Thứ {gio_moi.thu}")
                        if ten_thu not in cac_thu_trung_phong:
                            cac_thu_trung_phong.append(ten_thu)
    
    if cac_thu_trung_phong:
        error_msg = (f"Lỗi: Phòng học '{lop_moi.ma_lop}' đã được sử dụng trong môn này vào "
                    f"{', '.join(cac_thu_trung_phong)}. "
                    f"Vui lòng chọn phòng khác hoặc thay đổi thời gian học.")
        return False, error_msg
    
    # Kiểm tra trùng giáo viên và trùng giờ
    cac_thu_trung_gv = []
    for lop_cung_gv in cac_lop_cung_gv:
        for gio_moi in lop_moi.cac_khung_gio:
            for gio_cu in lop_cung_gv.cac_khung_gio:
                if gio_moi.thu == gio_cu.thu:
                    if kiem_tra_xung_dot_gio(gio_moi, gio_cu):
                        ten_thu = TEN_THU_TRONG_TUAN.get(gio_moi.thu, f"Thứ {gio_moi.thu}")
                        if ten_thu not in cac_thu_trung_gv:
                            cac_thu_trung_gv.append(ten_thu)
    
    if cac_thu_trung_gv:
        error_msg = (f"Lỗi: Giáo viên '{lop_moi.ten_giao_vien}' đã có lớp khác trong môn này vào "
                    f"{', '.join(cac_thu_trung_gv)}. "
                    f"Một giáo viên không thể dạy nhiều lớp cùng lúc.")
        return False, error_msg
    
    return True, None


def kiem_tra_trung_giao_vien(lop_moi, all_courses, exclude_lop_id=None):
    """
    Kiểm tra xem giáo viên của lớp mới có trùng giờ với lớp khác không
    (Một giáo viên không thể dạy nhiều lớp cùng lúc)
    
    Args:
        lop_moi: Lớp học mới cần kiểm tra
        all_courses: Dictionary chứa tất cả các môn học (key: ma_mon, value: MonHoc)
        exclude_lop_id: ID của lớp cần loại trừ khỏi kiểm tra (khi sửa lớp)
    
    Returns:
        Tuple (is_valid, error_msg):
        - is_valid: True nếu không trùng, False nếu trùng
        - error_msg: Thông báo lỗi nếu trùng (None nếu không trùng)
    """
    # Tìm tất cả các lớp có cùng giáo viên
    cac_lop_cung_gv = []
    for mon_hoc in all_courses.values():
        for lop in mon_hoc.cac_lop_hoc:
            # Bỏ qua lớp hiện tại nếu đang sửa
            if exclude_lop_id and lop.get_id() == exclude_lop_id:
                continue
            # So sánh tên giáo viên (không phân biệt hoa thường)
            if lop.ten_giao_vien.strip().lower() == lop_moi.ten_giao_vien.strip().lower():
                cac_lop_cung_gv.append(lop)
    
    # Nếu không có lớp nào cùng giáo viên, cho phép thêm
    if not cac_lop_cung_gv:
        return True, None
    
    # Kiểm tra xem có trùng giờ trong cùng 1 ngày không
    cac_thu_trung = []
    for lop_cung_gv in cac_lop_cung_gv:
        for gio_moi in lop_moi.cac_khung_gio:
            for gio_cu in lop_cung_gv.cac_khung_gio:
                # Nếu cùng thứ và trùng giờ
                if gio_moi.thu == gio_cu.thu:
                    if kiem_tra_xung_dot_gio(gio_moi, gio_cu):
                        ten_thu = TEN_THU_TRONG_TUAN.get(gio_moi.thu, f"Thứ {gio_moi.thu}")
                        if ten_thu not in cac_thu_trung:
                            cac_thu_trung.append(ten_thu)
    
    # Nếu có trùng giờ, báo lỗi
    if cac_thu_trung:
        error_msg = (f"Lỗi: Giáo viên '{lop_moi.ten_giao_vien}' đã có lớp khác vào "
                    f"{', '.join(cac_thu_trung)}. "
                    f"Một giáo viên không thể dạy nhiều lớp cùng lúc.")
        return False, error_msg
    
    # Không trùng giờ, cho phép thêm
    return True, None

