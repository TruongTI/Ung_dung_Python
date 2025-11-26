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
        """Chuyển đổi QTime sang số tiết (1-12)"""
        hour = qtime.hour()
        if 7 <= hour <= 11:
            return hour - 6
        if 13 <= hour <= 17:
            return hour - 12 + 6
        return -1

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
    
    def __init__(self, ma_lop, ten_giao_vien, ma_mon, ten_mon, color_hex=None):
        self.ma_lop = ma_lop
        self.ten_giao_vien = ten_giao_vien
        self.ma_mon = ma_mon
        self.ten_mon = ten_mon
        self.cac_khung_gio = []
        self.color_hex = color_hex or "#ADD8E6"
    
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
            'color_hex': self.color_hex
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

