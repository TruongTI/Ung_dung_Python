"""
Các class model đại diện cho dữ liệu trong hệ thống
"""


class ThoiGianHoc:
    """Đại diện cho một khung giờ học (thứ, tiết bắt đầu, tiết kết thúc)"""
    
    def __init__(self, thu, tiet_bat_dau, tiet_ket_thuc):
        self.thu = int(thu)
        self.tiet_bat_dau = int(tiet_bat_dau)
        self.tiet_ket_thuc = int(tiet_ket_thuc)
    
    def __str__(self):
        return f"[Thứ {self.thu}, Tiết {self.tiet_bat_dau}-{self.tiet_ket_thuc}]"
    
    def to_dict(self):
        return {
            'thu': self.thu, 
            'tiet_bat_dau': self.tiet_bat_dau, 
            'tiet_ket_thuc': self.tiet_ket_thuc
        }


class LichBan:
    """Đại diện cho một khoảng thời gian bận (không thể học)"""
    
    def __init__(self, thu, gio_bat_dau, gio_ket_thuc, ly_do, id):
        self.thu = int(thu)
        self.gio_bat_dau = gio_bat_dau 
        self.gio_ket_thuc = gio_ket_thuc
        self.ly_do = ly_do
        self.id = id
    
    @staticmethod
    def time_to_tiet(qtime):
        """
        Chuyển đổi QTime sang số tiết (1-13) dựa vào lịch thực tế
        Lịch tiết:
        - Tiết 1: 07h00 - 07h50
        - Tiết 2: 07h55 - 08h45
        - Tiết 3: 08h50 - 09h40
        - Tiết 4: 09h50 - 10h40
        - Tiết 5: 10h45 - 11h35
        - Tiết 6: 11h40 - 12h30
        - Tiết 7: 13h30 - 14h20
        - Tiết 8: 14h25 - 15h15
        - Tiết 9: 15h20 - 16h10
        - Tiết 10: 16h20 - 17h10
        - Tiết 11: 17h15 - 18h05
        - Tiết 12: 18h20 - 19h10
        - Tiết 13: 19h15 - 20h05
        """
        hour = qtime.hour()
        minute = qtime.minute()
        total_minutes = hour * 60 + minute
        
        # Ca Sáng
        if 420 <= total_minutes < 430:  # 07:00 - 07:50
            return 1
        if 475 <= total_minutes < 525:  # 07:55 - 08:45
            return 2
        if 530 <= total_minutes < 580:  # 08:50 - 09:40
            return 3
        if 590 <= total_minutes < 640:  # 09:50 - 10:40
            return 4
        if 645 <= total_minutes < 695:  # 10:45 - 11:35
            return 5
        if 700 <= total_minutes < 750:  # 11:40 - 12:30
            return 6
        
        # Ca Chiều
        if 810 <= total_minutes < 860:  # 13:30 - 14:20
            return 7
        if 865 <= total_minutes < 915:  # 14:25 - 15:15
            return 8
        if 920 <= total_minutes < 970:  # 15:20 - 16:10
            return 9
        if 980 <= total_minutes < 1030:  # 16:20 - 17:10
            return 10
        if 1035 <= total_minutes < 1085:  # 17:15 - 18:05
            return 11
        
        # Ca Tối
        if 1100 <= total_minutes < 1150:  # 18:20 - 19:10
            return 12
        if 1155 <= total_minutes < 1205:  # 19:15 - 20:05
            return 13
        
        return -1
    
    @staticmethod
    def _find_nearest_tiet(qtime):
        """
        Tìm tiết gần nhất với thời gian cho trước
        Nếu giờ không khớp chính xác, tìm tiết gần nhất và chiếm hết tiết đó
        """
        hour = qtime.hour()
        minute = qtime.minute()
        total_minutes = hour * 60 + minute
        
        # Danh sách thời gian bắt đầu của các tiết (tính bằng phút từ 00:00)
        tiet_times = [
            (420, 1),   # 07:00 - Tiết 1
            (475, 2),   # 07:55 - Tiết 2
            (530, 3),   # 08:50 - Tiết 3
            (590, 4),   # 09:50 - Tiết 4
            (645, 5),   # 10:45 - Tiết 5
            (700, 6),   # 11:40 - Tiết 6
            (810, 7),   # 13:30 - Tiết 7
            (865, 8),   # 14:25 - Tiết 8
            (920, 9),   # 15:20 - Tiết 9
            (980, 10),  # 16:20 - Tiết 10
            (1035, 11), # 17:15 - Tiết 11
            (1100, 12), # 18:20 - Tiết 12
            (1155, 13), # 19:15 - Tiết 13
        ]
        
        # Tìm tiết gần nhất
        min_diff = float('inf')
        nearest_tiet = -1
        
        for tiet_time, tiet_num in tiet_times:
            diff = abs(total_minutes - tiet_time)
            if diff < min_diff:
                min_diff = diff
                nearest_tiet = tiet_num
        
        return nearest_tiet

    def to_thoi_gian_hoc(self):
        """Chuyển đổi LichBan sang ThoiGianHoc"""
        tiet_bd = self.time_to_tiet(self.gio_bat_dau)
        tiet_kt = self.time_to_tiet(self.gio_ket_thuc)
        if tiet_bd != -1 and tiet_kt != -1:
            return ThoiGianHoc(self.thu, tiet_bd, tiet_kt)
        return None
        
    def __str__(self):
        return f"Thứ {self.thu} ({self.gio_bat_dau.toString('HH:mm')}-{self.gio_ket_thuc.toString('HH:mm')}) - {self.ly_do}"


class LopHoc:
    """Đại diện cho một lớp học cụ thể"""
    
    def __init__(self, ma_lop, ten_giao_vien, ma_mon, ten_mon, color_hex=None, loai_lop="Lớp"):
        self.ma_lop = ma_lop
        self.ten_giao_vien = ten_giao_vien
        self.ma_mon = ma_mon
        self.ten_mon = ten_mon
        self.cac_khung_gio = []
        self.color_hex = color_hex or "#ADD8E6"
        self.loai_lop = loai_lop  # "Lý thuyết", "Bài tập", hoặc "Lớp"
    
    def them_khung_gio(self, thu, tiet_bat_dau, tiet_ket_thuc):
        """Thêm một khung giờ học vào lớp"""
        self.cac_khung_gio.append(ThoiGianHoc(thu, tiet_bat_dau, tiet_ket_thuc))
    
    def __str__(self):
        gio_str = ", ".join(str(gio) for gio in self.cac_khung_gio)
        return f"({self.ma_lop}) {self.ten_giao_vien} - {gio_str}"
    
    def get_id(self):
        """Trả về ID duy nhất của lớp (ma_mon-ma_lop)"""
        return f"{self.ma_mon}-{self.ma_lop}"
    
    def to_dict(self):
        return {
            'ma_lop': self.ma_lop, 
            'ten_giao_vien': self.ten_giao_vien,
            'ma_mon': self.ma_mon, 
            'ten_mon': self.ten_mon,
            'cac_khung_gio': [gio.to_dict() for gio in self.cac_khung_gio],
            'color_hex': self.color_hex,
            'loai_lop': self.loai_lop
        }


class MonHoc:
    """Đại diện cho một môn học với các lớp học của nó"""
    
    def __init__(self, ma_mon, ten_mon, tien_quyet=None, color_hex=None):
        self.ma_mon = ma_mon
        self.ten_mon = ten_mon
        self.cac_lop_hoc = []
        self.cac_lop_hoc_dict = {}
        self.tien_quyet = tien_quyet or [] 
        self.color_hex = color_hex
    
    def them_lop_hoc(self, lop_hoc):
        """Thêm một lớp học vào môn học"""
        if lop_hoc.get_id() not in self.cac_lop_hoc_dict:
            if self.color_hex and not lop_hoc.color_hex:
                lop_hoc.color_hex = self.color_hex
            self.cac_lop_hoc.append(lop_hoc)
            self.cac_lop_hoc_dict[lop_hoc.get_id()] = lop_hoc
    
    def to_dict(self):
        return {
            'ma_mon': self.ma_mon, 
            'ten_mon': self.ten_mon,
            'cac_lop_hoc': [lop.to_dict() for lop in self.cac_lop_hoc],
            'tien_quyet': self.tien_quyet,
            'color_hex': self.color_hex
        }

