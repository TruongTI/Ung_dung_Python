"""
Logic xử lý tìm kiếm và kiểm tra xung đột thời khóa biểu
"""

import time
from collections import defaultdict
from .models import ThoiGianHoc, LichBan, LopHoc
from .constants import TEN_THU_TRONG_TUAN, MAX_COURSES, MAX_RESULTS, SEARCH_TIMEOUT


def kiem_tra_xung_dot_gio(gio_A, gio_B):
    """Kiểm tra xem hai khung giờ có xung đột không"""
    if not gio_A or not gio_B or gio_A.thu != gio_B.thu:
        return False
    return not (gio_A.tiet_ket_thuc < gio_B.tiet_bat_dau or 
                gio_A.tiet_bat_dau > gio_B.tiet_ket_thuc)


def _build_time_index(lop_list):
    """
    Tạo index cho thời gian học để lookup nhanh O(1)
    
    Args:
        lop_list: Danh sách các lớp học hoặc lịch bận
    
    Returns:
        Dict: {thu: {tiet: [list of objects]}} - Index theo thứ và tiết
    """
    time_index = defaultdict(lambda: defaultdict(list))
    for item in lop_list:
        if isinstance(item, LopHoc):
            for gio in item.cac_khung_gio:
                for tiet in range(gio.tiet_bat_dau, gio.tiet_ket_thuc + 1):
                    time_index[gio.thu][tiet].append(item)
        elif isinstance(item, LichBan):
            gio_ban = item.to_thoi_gian_hoc()
            if gio_ban:
                for tiet in range(gio_ban.tiet_bat_dau, gio_ban.tiet_ket_thuc + 1):
                    time_index[gio_ban.thu][tiet].append(item)
    return time_index


def _build_gv_index(all_courses, exclude_lop_id=None):
    """
    Tạo index cho giáo viên để lookup nhanh O(1)
    
    Args:
        all_courses: Dictionary chứa tất cả các môn học
        exclude_lop_id: ID của lớp cần loại trừ
    
    Returns:
        Dict: {ten_gv_normalized: [list of LopHoc]}
    """
    gv_index = defaultdict(list)
    for mon_hoc in all_courses.values():
        for lop in mon_hoc.cac_lop_hoc:
            if exclude_lop_id and lop.get_id() == exclude_lop_id:
                continue
            gv_key = lop.ten_giao_vien.strip().lower()
            gv_index[gv_key].append(lop)
    return gv_index


def _build_lop_id_index(all_courses):
    """
    Tạo index cho lớp học theo ID để lookup nhanh O(1)
    
    Args:
        all_courses: Dictionary chứa tất cả các môn học
    
    Returns:
        Dict: {lop_id: LopHoc} - Index theo ID
    """
    lop_id_index = {}
    for mon_hoc in all_courses.values():
        for lop in mon_hoc.cac_lop_hoc:
            lop_id = lop.get_id()
            # Nếu có nhiều lớp cùng ID, lưu lớp đầu tiên (hoặc có thể lưu list)
            if lop_id not in lop_id_index:
                lop_id_index[lop_id] = lop
    return lop_id_index


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
    """
    Kiểm tra xem lớp mới có trùng với lịch hiện tại hoặc giờ bận không
    Tối ưu: Sử dụng time index để giảm độ phức tạp từ O(n²) xuống O(n)
    """
    # Tạo index cho lịch hiện tại và giờ bận
    all_items = list(lich_hien_tai) + list(danh_sach_gio_ban)
    time_index = _build_time_index(all_items)
    
    # Kiểm tra xung đột bằng cách lookup trong index
    for gio_moi in lop_moi.cac_khung_gio:
        thu = gio_moi.thu
        if thu in time_index:
            # Kiểm tra các tiết trong khung giờ mới
            for tiet in range(gio_moi.tiet_bat_dau, gio_moi.tiet_ket_thuc + 1):
                if tiet in time_index[thu]:
                    # Có lớp/giờ bận ở cùng thứ và tiết, kiểm tra xung đột chi tiết
                    for item in time_index[thu][tiet]:
                        if check_trung_lich(lop_moi, item):
                            return True
    return False


def _tim_lop_rang_buoc(lop_id, all_courses, lop_hien_tai=None):
    """Tìm lớp học từ ID
    
    Args:
        lop_id: ID của lớp (format mới hoặc cũ)
        all_courses: Dictionary chứa tất cả các môn học
        lop_hien_tai: Lớp hiện tại (để ưu tiên lớp không trùng giờ)
    
    Returns:
        LopHoc object nếu tìm thấy, None nếu không tìm thấy
    """
    # Sử dụng helper để tìm lớp (hỗ trợ cả format cũ và mới)
    lop_tim_duoc = _find_lop_by_id_helper(lop_id, all_courses)
    
    # Nếu tìm thấy và là format mới (có nhiều phần), trả về luôn
    if lop_tim_duoc:
        parts = lop_id.split("-")
        if len(parts) >= 6:
            # Format mới: đã tìm chính xác, trả về luôn
            return lop_tim_duoc
    
    # Format cũ hoặc không tìm thấy: tìm tất cả lớp cùng ID và ưu tiên
    # Tối ưu: Tìm trực tiếp trong môn học cụ thể nếu có thể parse được ma_mon
    if not all_courses:
        return None
    
    # Thử parse ma_mon từ lop_id (format cũ: "ma_mon-ma_lop")
    parts = lop_id.split("-")
    if len(parts) >= 2:
        ma_mon = parts[0]
        if ma_mon in all_courses:
            # Tìm trong môn học cụ thể
            mon_hoc = all_courses[ma_mon]
            cac_lop_cung_id = [lop for lop in mon_hoc.cac_lop_hoc if lop.get_id() == lop_id]
            
            if cac_lop_cung_id:
                # Nếu chỉ có 1 lớp, trả về lớp đó
                if len(cac_lop_cung_id) == 1:
                    return cac_lop_cung_id[0]
                
                # Nếu có nhiều lớp cùng ID, ưu tiên lớp không trùng giờ với lop_hien_tai
                if lop_hien_tai:
                    for lop in cac_lop_cung_id:
                        if not check_trung_lich(lop_hien_tai, lop):
                            return lop  # Trả về lớp không trùng giờ
                
                # Nếu không có lớp nào không trùng giờ, trả về lớp đầu tiên
                return cac_lop_cung_id[0]
    
    # Fallback: Duyệt tất cả (cho trường hợp format không chuẩn)
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
    """
    Thêm các lớp ràng buộc vào lịch hiện tại nếu có
    Tối ưu: Sử dụng set để kiểm tra nhanh O(1) thay vì O(n)
    """
    if not lop_hoc.lop_rang_buoc or not all_courses:
        return True  # Không có ràng buộc, OK
    
    # Tạo set các object ID đã có trong lịch để lookup nhanh O(1)
    lich_hien_tai_ids = {id(lop) for lop in lich_hien_tai}
    
    # Kiểm tra và thêm các lớp ràng buộc
    for rang_buoc_id in lop_hoc.lop_rang_buoc:
        # Tìm lớp ràng buộc (truyền lop_hoc để ưu tiên lớp không trùng giờ)
        lop_rang_buoc = _tim_lop_rang_buoc(rang_buoc_id, all_courses, lop_hien_tai=lop_hoc)
        if not lop_rang_buoc:
            continue  # Lớp ràng buộc không tồn tại, bỏ qua
        
        # Kiểm tra xem lớp ràng buộc đã có trong lịch chưa (so sánh bằng object ID) - O(1)
        if id(lop_rang_buoc) in lich_hien_tai_ids:
            continue  # Đã có trong lịch, bỏ qua
        
        # Nếu chưa có, kiểm tra xung đột và thêm vào
        # Kiểm tra xung đột với lịch hiện tại
        if _kiem_tra_trung_voi_lich(lop_rang_buoc, lich_hien_tai, danh_sach_gio_ban):
            return False  # Có xung đột, không thể thêm lớp ràng buộc
        
        lich_hien_tai.append(lop_rang_buoc)
        lich_hien_tai_ids.add(id(lop_rang_buoc))  # Cập nhật set
    
    return True  # Đã thêm tất cả lớp ràng buộc thành công

def _tim_kiem_de_quy(danh_sach_mon_hoc, mon_hoc_index, lich_hien_tai, ket_qua, danh_sach_gio_ban, all_courses=None, max_results=None, start_time=None, timeout=None):
    """
    Hàm đệ quy để tìm tất cả các thời khóa biểu hợp lệ
    
    Args:
        danh_sach_mon_hoc: Danh sách môn học
        mon_hoc_index: Chỉ số môn học hiện tại
        lich_hien_tai: Lịch hiện tại đang xây dựng
        ket_qua: Danh sách kết quả (sẽ được cập nhật)
        danh_sach_gio_ban: Danh sách giờ bận
        all_courses: Dictionary tất cả môn học
        max_results: Số lượng kết quả tối đa (None = không giới hạn)
        start_time: Thời gian bắt đầu tìm kiếm (để tính timeout)
        timeout: Timeout tính bằng giây (None = không timeout)
    """
    # Kiểm tra timeout
    if timeout and start_time:
        elapsed = time.time() - start_time
        if elapsed > timeout:
            return  # Dừng khi hết thời gian
    
    # Kiểm tra giới hạn số lượng kết quả
    if max_results and len(ket_qua) >= max_results:
        return  # Dừng khi đạt giới hạn
    
    if mon_hoc_index == len(danh_sach_mon_hoc):
        # Sử dụng tuple thay vì list để tiết kiệm memory
        # Tuple nhẹ hơn list và immutable (phù hợp vì TKB không thay đổi sau khi tìm được)
        ket_qua.append(tuple(lich_hien_tai))
        return
    
    mon_hien_tai = danh_sach_mon_hoc[mon_hoc_index]
    if not mon_hien_tai.cac_lop_hoc:
        _tim_kiem_de_quy(danh_sach_mon_hoc, mon_hoc_index + 1, lich_hien_tai, ket_qua, danh_sach_gio_ban, all_courses, max_results, start_time, timeout)
        return
    
    # Kiểm tra xem môn học này đã có lớp nào trong lịch chưa (do được thêm như một lớp ràng buộc)
    # Tối ưu: Sử dụng any() với generator expression thay vì vòng lặp thủ công
    # Nếu có rồi, bỏ qua môn học này và tiếp tục với môn tiếp theo
    mon_da_co_lop_trong_lich = any(
        lop_trong_lich.ma_mon == mon_hien_tai.ma_mon 
        for lop_trong_lich in lich_hien_tai
    )
    
    # Nếu môn học đã có lớp trong lịch, bỏ qua và tiếp tục với môn tiếp theo
    if mon_da_co_lop_trong_lich:
        _tim_kiem_de_quy(danh_sach_mon_hoc, mon_hoc_index + 1, lich_hien_tai, ket_qua, danh_sach_gio_ban, all_courses, max_results, start_time, timeout)
        return
    
    for lop_hoc in mon_hien_tai.cac_lop_hoc:
        # Kiểm tra xung đột lịch học
        if _kiem_tra_trung_voi_lich(lop_hoc, lich_hien_tai, danh_sach_gio_ban):
            continue  # Bỏ qua lớp trùng lịch
        
        # Kiểm tra logic: Nếu lớp là "Lý thuyết" hoặc "Bài tập", 
        # chỉ cho phép 1 lớp cùng loại trong cùng môn xuất hiện trong TKB (trừ khi có ràng buộc)
        loai_lop = getattr(lop_hoc, 'loai_lop', 'Lớp')
        if loai_lop in ["Lý thuyết", "Bài tập"]:
            # Tối ưu: Tìm lớp cùng loại trong cùng môn
            lop_hoc_id = lop_hoc.get_id()
            lop_rang_buoc_set = set(lop_hoc.lop_rang_buoc) if lop_hoc.lop_rang_buoc else set()
            
            # Kiểm tra xem đã có lớp cùng loại trong cùng môn chưa
            da_co_lop_cung_loai = False
            for lop_trong_lich in lich_hien_tai:
                if (lop_trong_lich.ma_mon == mon_hien_tai.ma_mon and
                    getattr(lop_trong_lich, 'loai_lop', 'Lớp') == loai_lop):
                    # Kiểm tra xem lớp trong lịch có phải là lớp ràng buộc với lớp hiện tại không
                    lop_trong_lich_id = lop_trong_lich.get_id()
                    # Kiểm tra ràng buộc 2 chiều - sử dụng set để lookup O(1) thay vì list
                    co_rang_buoc = (
                        lop_trong_lich_id in lop_rang_buoc_set or
                        (lop_trong_lich.lop_rang_buoc and lop_hoc_id in lop_trong_lich.lop_rang_buoc)
                    )
                    
                    if not co_rang_buoc:
                        # Đã có lớp cùng loại và không có ràng buộc
                        da_co_lop_cung_loai = True
                        break
            
            # Nếu đã có lớp cùng loại và không có ràng buộc, bỏ qua lớp này
            if da_co_lop_cung_loai:
                continue
        
        # Thêm lớp học vào lịch
        lich_hien_tai.append(lop_hoc)
        
        # Thêm các lớp ràng buộc nếu có
        lop_rang_buoc_da_them = []
        if _them_lop_rang_buoc(lop_hoc, lich_hien_tai, danh_sach_gio_ban, all_courses):
            # Đã thêm thành công các lớp ràng buộc, tiếp tục đệ quy
            _tim_kiem_de_quy(danh_sach_mon_hoc, mon_hoc_index + 1, lich_hien_tai, ket_qua, danh_sach_gio_ban, all_courses, max_results, start_time, timeout)
        else:
            # Không thể thêm lớp ràng buộc do xung đột, bỏ qua lớp này
            pass
        
        # Xóa lớp học và các lớp ràng buộc đã thêm
        lop_chinh = lich_hien_tai.pop()  # Xóa lớp chính
        
        # Xóa các lớp ràng buộc đã thêm (tối ưu: xóa từ cuối lên để tránh shift index)
        if lop_hoc.lop_rang_buoc and all_courses:
            # Tạo set các ID lớp ràng buộc để tìm nhanh
            rang_buoc_ids = set(lop_hoc.lop_rang_buoc)
            # Xóa từ cuối lên để tránh vấn đề với index khi xóa
            for i in range(len(lich_hien_tai) - 1, -1, -1):
                lop_trong_lich = lich_hien_tai[i]
                # Kiểm tra xem lớp này có phải là lớp ràng buộc không
                lop_id = lop_trong_lich.get_id()
                if lop_id in rang_buoc_ids:
                    lich_hien_tai.pop(i)


def tim_thoi_khoa_bieu(danh_sach_mon_hoc, danh_sach_gio_ban, mon_bat_buoc, completed_courses=None, all_courses=None, max_results=None, timeout=None):
    """
    Tìm tất cả các thời khóa biểu hợp lệ từ danh sách môn học
    
    Args:
        danh_sach_mon_hoc: Danh sách các môn học cần sắp xếp
        danh_sach_gio_ban: Danh sách các giờ bận (LichBan)
        mon_bat_buoc: Danh sách mã môn bắt buộc phải có trong TKB
        completed_courses: Danh sách mã môn đã học (môn tiên quyết)
        all_courses: Dictionary chứa tất cả các môn học (để tìm lớp ràng buộc)
        max_results: Số lượng kết quả tối đa (None = dùng MAX_RESULTS mặc định)
        timeout: Timeout tính bằng giây (None = dùng SEARCH_TIMEOUT mặc định)
    
    Returns:
        Tuple (ket_qua, error_msg, warning_msg): 
        - ket_qua: Danh sách các TKB hợp lệ (mỗi TKB là tuple các LopHoc - tối ưu memory)
        - error_msg: Thông báo lỗi nếu có (None nếu không có lỗi)
        - warning_msg: Thông báo cảnh báo (ví dụ: đạt giới hạn, timeout)
        
    Note:
        Sử dụng tuple thay vì list để tiết kiệm memory. Tuple nhẹ hơn list và immutable,
        phù hợp vì TKB không thay đổi sau khi tìm được. Tuple vẫn hỗ trợ iteration và indexing.
    """
    # Sử dụng giá trị mặc định nếu không được chỉ định
    if max_results is None:
        max_results = MAX_RESULTS
    if timeout is None:
        timeout = SEARCH_TIMEOUT
    # Kiểm tra giới hạn số môn học
    if len(danh_sach_mon_hoc) > MAX_COURSES:
        error_msg = (f"Lỗi: Chỉ được chọn tối đa {MAX_COURSES} môn học. "
                    f"Bạn đã chọn {len(danh_sach_mon_hoc)} môn. "
                    f"Vui lòng bỏ chọn một số môn.")
        return [], error_msg, None
    
    # Kiểm tra môn tiên quyết - môn tiên quyết phải có trong danh sách môn đã học
    completed_courses_set = set(completed_courses) if completed_courses else set()
    for mon in danh_sach_mon_hoc:
        for mon_tien_quyet in mon.tien_quyet:
            if mon_tien_quyet not in completed_courses_set:
                error_msg = (f"Lỗi: Môn '{mon.ten_mon} ({mon.ma_mon})' yêu cầu "
                           f"phải học môn tiên quyết '{mon_tien_quyet}' trước. "
                           f"Vui lòng thêm môn '{mon_tien_quyet}' vào danh sách môn đã học.")
                return [], error_msg, None
    
    # Tìm tất cả các TKB hợp lệ (truyền all_courses để xử lý ràng buộc)
    ket_qua_thuan = []
    start_time = time.time()
    warning_msg = None
    
    # Gọi hàm đệ quy với timeout và max_results
    _tim_kiem_de_quy(danh_sach_mon_hoc, 0, [], ket_qua_thuan, danh_sach_gio_ban, 
                     all_courses, max_results, start_time, timeout)
    
    # Kiểm tra xem có đạt giới hạn hoặc timeout không
    elapsed_time = time.time() - start_time
    if len(ket_qua_thuan) >= max_results:
        warning_msg = (f"Đã tìm được {len(ket_qua_thuan)} TKB (đạt giới hạn {max_results}). "
                      f"Có thể còn nhiều TKB khác. Thời gian: {elapsed_time:.2f}s")
    elif elapsed_time >= timeout * 0.9:  # Cảnh báo nếu gần hết thời gian
        warning_msg = (f"Đã tìm được {len(ket_qua_thuan)} TKB. "
                      f"Quá trình tìm kiếm gần hết thời gian ({elapsed_time:.2f}s/{timeout}s).")
    
    # Nếu không có môn bắt buộc, trả về tất cả kết quả
    if not mon_bat_buoc:
        return ket_qua_thuan, None, warning_msg
    
    # Lọc các TKB có chứa tất cả môn bắt buộc
    ket_qua_da_loc = []
    ma_mon_bat_buoc = set(mon_bat_buoc)
    for tkb in ket_qua_thuan:
        ma_mon_trong_tkb = {lop.ma_mon for lop in tkb}
        if ma_mon_bat_buoc.issubset(ma_mon_trong_tkb):
            ket_qua_da_loc.append(tkb)
    
    return ket_qua_da_loc, None, warning_msg


def kiem_tra_trung_phong_hoc(lop_moi, all_courses, exclude_lop_id=None):
    """
    Kiểm tra xem lớp mới có trùng phòng học và trùng giờ với lớp khác không
    Tối ưu: Sử dụng index để giảm độ phức tạp từ O(n²) xuống O(n)
    
    Args:
        lop_moi: Lớp học mới cần kiểm tra
        all_courses: Dictionary chứa tất cả các môn học (key: ma_mon, value: MonHoc)
        exclude_lop_id: ID của lớp cần loại trừ khỏi kiểm tra (khi sửa lớp)
    
    Returns:
        Tuple (is_valid, error_msg):
        - is_valid: True nếu không trùng, False nếu trùng
        - error_msg: Thông báo lỗi nếu trùng (None nếu không trùng)
    """
    # Tìm tất cả các lớp có cùng phòng học (ma_lop) - O(n)
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
    
    # Tạo time index cho các lớp cùng phòng - O(n)
    time_index = _build_time_index(cac_lop_cung_phong)
    
    # Kiểm tra xung đột bằng cách lookup trong index - O(n) thay vì O(n²)
    cac_thu_trung = set()
    for gio_moi in lop_moi.cac_khung_gio:
        thu = gio_moi.thu
        if thu in time_index:
            # Kiểm tra các tiết trong khung giờ mới
            for tiet in range(gio_moi.tiet_bat_dau, gio_moi.tiet_ket_thuc + 1):
                if tiet in time_index[thu]:
                    # Có lớp cùng phòng ở cùng thứ và tiết, kiểm tra xung đột chi tiết
                    for lop_cung_phong in time_index[thu][tiet]:
                        # Kiểm tra tất cả khung giờ của lớp cùng phòng
                        for gio_cu in lop_cung_phong.cac_khung_gio:
                            if gio_cu.thu == thu and kiem_tra_xung_dot_gio(gio_moi, gio_cu):
                                ten_thu = TEN_THU_TRONG_TUAN.get(thu, f"Thứ {thu}")
                                cac_thu_trung.add(ten_thu)
                                break  # Chỉ cần tìm một xung đột cho mỗi thứ là đủ
                        if ten_thu in cac_thu_trung:
                            break
    
    # Nếu có trùng giờ, báo lỗi
    if cac_thu_trung:
        error_msg = (f"Lỗi: Phòng học '{lop_moi.ma_lop}' đã được sử dụng vào "
                    f"{', '.join(sorted(cac_thu_trung))}. "
                    f"Vui lòng chọn phòng khác hoặc thay đổi thời gian học.")
        return False, error_msg
    
    # Không trùng giờ, cho phép thêm
    return True, None


def kiem_tra_trung_trong_cung_mon(lop_moi, mon_hoc, exclude_lop_id=None):
    """
    Kiểm tra xem lớp mới có trùng phòng học, giáo viên và trùng giờ với lớp khác trong cùng môn không
    (Chỉ kiểm tra trong cùng một môn - dùng khi thêm lớp trong area lớp học)
    Tối ưu: Sử dụng index để giảm độ phức tạp từ O(n²) xuống O(n)
    
    Args:
        lop_moi: Lớp học mới cần kiểm tra
        mon_hoc: Môn học chứa lớp mới
        exclude_lop_id: ID của lớp cần loại trừ khỏi kiểm tra (khi sửa lớp)
    
    Returns:
        Tuple (is_valid, error_msg):
        - is_valid: True nếu không trùng, False nếu trùng
        - error_msg: Thông báo lỗi nếu trùng (None nếu không trùng)
    """
    # Lọc các lớp cần kiểm tra (bỏ qua lớp đang sửa)
    cac_lop_kiem_tra = [
        lop for lop in mon_hoc.cac_lop_hoc
        if not (exclude_lop_id and lop.get_id() == exclude_lop_id)
    ]
    
    # Tạo index cho phòng học và giáo viên
    cac_lop_cung_phong = [lop for lop in cac_lop_kiem_tra if lop.ma_lop == lop_moi.ma_lop]
    gv_key = lop_moi.ten_giao_vien.strip().lower()
    cac_lop_cung_gv = [lop for lop in cac_lop_kiem_tra 
                       if lop.ten_giao_vien.strip().lower() == gv_key]
    
    # Kiểm tra trùng phòng học và trùng giờ - sử dụng time index
    if cac_lop_cung_phong:
        time_index_phong = _build_time_index(cac_lop_cung_phong)
        cac_thu_trung_phong = set()
        
        for gio_moi in lop_moi.cac_khung_gio:
            thu = gio_moi.thu
            if thu in time_index_phong:
                for tiet in range(gio_moi.tiet_bat_dau, gio_moi.tiet_ket_thuc + 1):
                    if tiet in time_index_phong[thu]:
                        # Kiểm tra xung đột chi tiết
                        for lop_cung_phong in time_index_phong[thu][tiet]:
                            for gio_cu in lop_cung_phong.cac_khung_gio:
                                if gio_cu.thu == thu and kiem_tra_xung_dot_gio(gio_moi, gio_cu):
                                    ten_thu = TEN_THU_TRONG_TUAN.get(thu, f"Thứ {thu}")
                                    cac_thu_trung_phong.add(ten_thu)
                                    break
        
        if cac_thu_trung_phong:
            error_msg = (f"Lỗi: Phòng học '{lop_moi.ma_lop}' đã được sử dụng trong môn này vào "
                        f"{', '.join(sorted(cac_thu_trung_phong))}. "
                        f"Vui lòng chọn phòng khác hoặc thay đổi thời gian học.")
            return False, error_msg
    
    # Kiểm tra trùng giáo viên và trùng giờ - sử dụng time index
    if cac_lop_cung_gv:
        time_index_gv = _build_time_index(cac_lop_cung_gv)
        cac_thu_trung_gv = set()
        
        for gio_moi in lop_moi.cac_khung_gio:
            thu = gio_moi.thu
            if thu in time_index_gv:
                for tiet in range(gio_moi.tiet_bat_dau, gio_moi.tiet_ket_thuc + 1):
                    if tiet in time_index_gv[thu]:
                        # Kiểm tra xung đột chi tiết
                        for lop_cung_gv in time_index_gv[thu][tiet]:
                            for gio_cu in lop_cung_gv.cac_khung_gio:
                                if gio_cu.thu == thu and kiem_tra_xung_dot_gio(gio_moi, gio_cu):
                                    ten_thu = TEN_THU_TRONG_TUAN.get(thu, f"Thứ {thu}")
                                    cac_thu_trung_gv.add(ten_thu)
                                    break
        
        if cac_thu_trung_gv:
            error_msg = (f"Lỗi: Giáo viên '{lop_moi.ten_giao_vien}' đã có lớp khác trong môn này vào "
                        f"{', '.join(sorted(cac_thu_trung_gv))}. "
                        f"Một giáo viên không thể dạy nhiều lớp cùng lúc.")
            return False, error_msg
    
    return True, None


def kiem_tra_trung_giao_vien(lop_moi, all_courses, exclude_lop_id=None):
    """
    Kiểm tra xem giáo viên của lớp mới có trùng giờ với lớp khác không
    (Một giáo viên không thể dạy nhiều lớp cùng lúc)
    Tối ưu: Sử dụng GV index để giảm độ phức tạp từ O(n²) xuống O(n)
    
    Args:
        lop_moi: Lớp học mới cần kiểm tra
        all_courses: Dictionary chứa tất cả các môn học (key: ma_mon, value: MonHoc)
        exclude_lop_id: ID của lớp cần loại trừ khỏi kiểm tra (khi sửa lớp)
    
    Returns:
        Tuple (is_valid, error_msg):
        - is_valid: True nếu không trùng, False nếu trùng
        - error_msg: Thông báo lỗi nếu trùng (None nếu không trùng)
    """
    # Tạo index cho giáo viên - O(n) một lần
    gv_index = _build_gv_index(all_courses, exclude_lop_id)
    
    # Lookup lớp cùng giáo viên - O(1)
    gv_key = lop_moi.ten_giao_vien.strip().lower()
    cac_lop_cung_gv = gv_index.get(gv_key, [])
    
    # Nếu không có lớp nào cùng giáo viên, cho phép thêm
    if not cac_lop_cung_gv:
        return True, None
    
    # Tạo time index cho các lớp cùng giáo viên - O(n)
    time_index = _build_time_index(cac_lop_cung_gv)
    
    # Kiểm tra xung đột bằng cách lookup trong index - O(n) thay vì O(n²)
    cac_thu_trung = set()
    for gio_moi in lop_moi.cac_khung_gio:
        thu = gio_moi.thu
        if thu in time_index:
            for tiet in range(gio_moi.tiet_bat_dau, gio_moi.tiet_ket_thuc + 1):
                if tiet in time_index[thu]:
                    # Có lớp cùng giáo viên ở cùng thứ và tiết, kiểm tra xung đột chi tiết
                    for lop_cung_gv in time_index[thu][tiet]:
                        # Kiểm tra tất cả khung giờ của lớp cùng giáo viên
                        for gio_cu in lop_cung_gv.cac_khung_gio:
                            if gio_cu.thu == thu and kiem_tra_xung_dot_gio(gio_moi, gio_cu):
                                ten_thu = TEN_THU_TRONG_TUAN.get(thu, f"Thứ {thu}")
                                cac_thu_trung.add(ten_thu)
                                break  # Chỉ cần tìm một xung đột cho mỗi thứ là đủ
                        if ten_thu in cac_thu_trung:
                            break
    
    # Nếu có trùng giờ, báo lỗi
    if cac_thu_trung:
        error_msg = (f"Lỗi: Giáo viên '{lop_moi.ten_giao_vien}' đã có lớp khác vào "
                    f"{', '.join(sorted(cac_thu_trung))}. "
                    f"Một giáo viên không thể dạy nhiều lớp cùng lúc.")
        return False, error_msg
    
    # Không trùng giờ, cho phép thêm
    return True, None


def _find_lop_by_id_helper(lop_id, all_courses):
    """
    Helper function để tìm lớp học theo ID
    Tối ưu: Tìm trực tiếp trong môn học cụ thể thay vì duyệt tất cả
    
    Args:
        lop_id: ID của lớp 
            - Format mới: "ten_giao_vien-ma_mon-ma_lop-thu-tiet_bat_dau-tiet_ket_thuc"
            - Format cũ (tương thích): "ma_mon-ma_lop"
        all_courses: Dictionary chứa tất cả các môn học
    
    Returns:
        LopHoc object nếu tìm thấy, None nếu không tìm thấy
    """
    if not all_courses:
        return None
    
    # Kiểm tra format ID: nếu có nhiều dấu "-" thì là format mới
    # Format mới: "ten_giao_vien-ma_mon-ma_lop-thu-tiet_bat_dau-tiet_ket_thuc"
    # Tên giáo viên ở đầu, dễ parse từ phải sang trái
    # Tách từ phải sang trái: 5 phần cuối là tiet_ket_thuc, tiet_bat_dau, thu, ma_lop, ma_mon
    # Phần còn lại ở đầu là ten_giao_vien
    
    parts = lop_id.split("-")
    
    if len(parts) >= 6:
        try:
            # Lấy 5 phần cuối: tiet_ket_thuc, tiet_bat_dau, thu, ma_lop, ma_mon
            tiet_ket_thuc = int(parts[-1])
            tiet_bat_dau = int(parts[-2])
            thu = int(parts[-3])
            ma_lop = parts[-4]
            ma_mon = parts[-5]
            # Phần còn lại ở đầu là ten_giao_vien
            ten_giao_vien = "-".join(parts[:-5]).replace("_", " ")  # Khôi phục khoảng trắng
            
            # Tối ưu: Tìm trực tiếp trong môn học cụ thể thay vì duyệt tất cả
            if ma_mon in all_courses:
                mon_hoc = all_courses[ma_mon]
                for lop in mon_hoc.cac_lop_hoc:
                    if (lop.ma_lop == ma_lop and
                        lop.ten_giao_vien == ten_giao_vien and
                        lop.cac_khung_gio and
                        lop.cac_khung_gio[0].thu == thu and
                        lop.cac_khung_gio[0].tiet_bat_dau == tiet_bat_dau and
                        lop.cac_khung_gio[0].tiet_ket_thuc == tiet_ket_thuc):
                        return lop
        except (ValueError, IndexError):
            # Nếu parse lỗi, fallback về format cũ
            pass
    
    # Format cũ: "ma_mon-ma_lop" (tương thích với dữ liệu cũ)
    # Tối ưu: Tìm trực tiếp trong môn học cụ thể nếu có thể parse được ma_mon
    if len(parts) >= 2:
        ma_mon = parts[0]
        if ma_mon in all_courses:
            # Tìm trong môn học cụ thể
            mon_hoc = all_courses[ma_mon]
            for lop in mon_hoc.cac_lop_hoc:
                if lop.get_id() == lop_id:
                    return lop
    
    # Fallback: Duyệt tất cả (cho trường hợp format không chuẩn)
    for mon_hoc in all_courses.values():
        for lop in mon_hoc.cac_lop_hoc:
            if lop.get_id() == lop_id:
                return lop
    
    return None


def update_bidirectional_constraints(old_lop_id, old_rang_buoc, new_lop_id, new_rang_buoc, all_courses):
    """
    Cập nhật ràng buộc 2 chiều: nếu lớp A ràng buộc với lớp B, thì lớp B cũng ràng buộc với lớp A
    
    Args:
        old_lop_id: ID của lớp cũ (khi sửa) hoặc None (khi thêm mới)
        old_rang_buoc: Danh sách ID các lớp ràng buộc cũ
        new_lop_id: ID của lớp mới (sau khi sửa hoặc thêm)
        new_rang_buoc: Danh sách ID các lớp ràng buộc mới
        all_courses: Dictionary chứa tất cả các môn học
    """
    # Tìm lớp hiện tại
    current_lop = _find_lop_by_id_helper(new_lop_id, all_courses)
    if not current_lop:
        return
    
    # Xóa ràng buộc cũ (nếu có)
    if old_lop_id:
        for old_rang_buoc_id in old_rang_buoc:
            # Tìm lớp ràng buộc cũ
            old_rang_buoc_lop = _find_lop_by_id_helper(old_rang_buoc_id, all_courses)
            if old_rang_buoc_lop and old_lop_id in (old_rang_buoc_lop.lop_rang_buoc or []):
                # Xóa ràng buộc ngược lại
                old_rang_buoc_lop.lop_rang_buoc.remove(old_lop_id)
    
    # Thêm ràng buộc mới (2 chiều)
    for new_rang_buoc_id in new_rang_buoc:
        # Tìm lớp ràng buộc mới
        new_rang_buoc_lop = _find_lop_by_id_helper(new_rang_buoc_id, all_courses)
        if new_rang_buoc_lop:
            # Đảm bảo lớp ràng buộc cũng ràng buộc với lớp hiện tại
            if not new_rang_buoc_lop.lop_rang_buoc:
                new_rang_buoc_lop.lop_rang_buoc = []
            if new_lop_id not in new_rang_buoc_lop.lop_rang_buoc:
                new_rang_buoc_lop.lop_rang_buoc.append(new_lop_id)


def remove_bidirectional_constraints(lop_id, all_courses):
    """
    Xóa ràng buộc 2 chiều khi xóa một lớp học
    
    Args:
        lop_id: ID của lớp bị xóa (format: "ma_mon-ma_lop")
        all_courses: Dictionary chứa tất cả các môn học
    """
    if not all_courses:
        return
    
    # Tìm tất cả các lớp có ràng buộc với lớp bị xóa
    for mon_hoc in all_courses.values():
        for lop in mon_hoc.cac_lop_hoc:
            if lop.lop_rang_buoc and lop_id in lop.lop_rang_buoc:
                # Xóa ràng buộc
                lop.lop_rang_buoc.remove(lop_id)