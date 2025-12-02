"""
Widget hiển thị thời khóa biểu dạng lưới
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QRect
from PyQt6.QtGui import QFont, QPainter, QColor, QBrush, QPen, QFontMetrics
from PyQt6.QtWidgets import QSizePolicy

from ..constants import TEN_THU_TRONG_TUAN


class ScheduleWidget(QWidget):
    """Widget hiển thị thời khóa biểu dạng lưới với khả năng click vào ô"""
    
    cellClicked = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(800, 600)
        self.current_schedule = []
        self.busy_times = []  # Danh sách giờ bận
        self.CELL_WIDTH = 120
        self.CELL_HEIGHT = 50
        self.HEADER_HEIGHT = 60
        self.TIME_COL_WIDTH = 60
        self.MAX_TIET = 12
        self.schedule_colors = {}
        self.constrained_classes = set()  # Set các lớp ràng buộc (dùng id() để so sánh)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMouseTracking(True)

        # Tính ngày Thứ 2 của tuần này
        today = QDate.currentDate()
        self.start_of_week = today.addDays(-(today.dayOfWeek() - 1))  # 1 = Monday

    def mousePressEvent(self, event):
        """Xử lý sự kiện click chuột vào ô lịch"""
        if event.button() == Qt.MouseButton.LeftButton:
            x, y = event.pos().x(), event.pos().y()
            # Kiểm tra click vào vùng hợp lệ (không phải header hoặc cột tiết)
            if x < self.TIME_COL_WIDTH or y < self.HEADER_HEIGHT:
                return
            
            # Tính toán chỉ số thứ và tiết
            thu_index = int((x - self.TIME_COL_WIDTH) / self.CELL_WIDTH)
            tiet = int((y - self.HEADER_HEIGHT) / self.CELL_HEIGHT) + 1
            
            # Kiểm tra bounds đầy đủ để tránh crash
            if thu_index < 0 or thu_index >= len(TEN_THU_TRONG_TUAN):
                return
            if tiet < 1 or tiet > self.MAX_TIET:
                return
            
            # Lấy thứ tương ứng
            thu = list(TEN_THU_TRONG_TUAN.keys())[thu_index]
            
            # Cho phép click vào ô để thêm tiết học (không chặn nếu đã có lớp)
            # Người dùng có thể thêm lớp mới hoặc lớp khác vào cùng ô
            self.cellClicked.emit(thu, tiet)

    def paintEvent(self, event):
        """Vẽ lưới thời khóa biểu"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Tính toán lại kích thước dựa trên kích thước widget
        self.CELL_WIDTH = (self.width() - self.TIME_COL_WIDTH) / len(TEN_THU_TRONG_TUAN)
        self.CELL_HEIGHT = (self.height() - self.HEADER_HEIGHT) / self.MAX_TIET
        self._draw_grid(painter)
        self._draw_busy_times(painter)  # Vẽ giờ bận trước (lớp nền)
        self._draw_schedule(painter)  # Vẽ lớp học lên trên
        painter.end()

    def _is_dark_mode(self):
        """Kiểm tra xem ứng dụng đang ở chế độ tối không"""
        # Lấy style sheet từ parent window
        parent = self.parent()
        while parent:
            if hasattr(parent, 'dark_mode'):
                return parent.dark_mode
            parent = parent.parent()
        return False

    def _draw_grid(self, painter):
        """Vẽ lưới và header"""
        is_dark = self._is_dark_mode()
        header_color = QColor("#C00000")
        text_color = QColor("#ffffff") if is_dark else QColor("#ffffff")
        grid_color = QColor("#666666") if is_dark else QColor("#d0d0d0")
        bg_color = QColor("#1e1e1e") if is_dark else QColor("#ffffff")

        
        
        # Vẽ nền
        painter.fillRect(0, 0, self.width(), self.height(), bg_color)
        
        painter.setPen(text_color)
        painter.fillRect(0, 0, self.TIME_COL_WIDTH, self.HEADER_HEIGHT, header_color)
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.drawText(0, 0, self.TIME_COL_WIDTH, self.HEADER_HEIGHT, 
                        Qt.AlignmentFlag.AlignCenter, "Tiết")
        
        for i, thu_text in enumerate(TEN_THU_TRONG_TUAN.values()):
            x = self.TIME_COL_WIDTH + i * self.CELL_WIDTH
            painter.fillRect(int(x), 0, int(self.CELL_WIDTH), self.HEADER_HEIGHT, header_color)
            
            # Vẽ Thứ và Ngày
            current_day = self.start_of_week.addDays(i)
            date_str = current_day.toString("dd/MM")
            
            # Vẽ "Thứ" ở trên
            painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            painter.setPen(text_color)
            painter.drawText(int(x), 0, int(self.CELL_WIDTH), int(self.HEADER_HEIGHT / 2), 
                           Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom, thu_text)
            # Vẽ "Ngày" ở dưới
            painter.setFont(QFont("Segoe UI", 9))
            painter.drawText(int(x), int(self.HEADER_HEIGHT / 2), int(self.CELL_WIDTH), 
                           int(self.HEADER_HEIGHT / 2), 
                           Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop, date_str)

        painter.setPen(grid_color)
        text_color_grid = QColor("#e0e0e0") if is_dark else QColor("#000000")
        painter.setPen(text_color_grid)
        painter.setFont(QFont("Segoe UI", 9))
        for tiet in range(1, self.MAX_TIET + 1):
            y = self.HEADER_HEIGHT + (tiet - 1) * self.CELL_HEIGHT
            painter.drawText(0, int(y), self.TIME_COL_WIDTH, int(self.CELL_HEIGHT), 
                           Qt.AlignmentFlag.AlignCenter, str(tiet))
            painter.setPen(grid_color)
            painter.drawLine(0, int(y + self.CELL_HEIGHT), self.width(), int(y + self.CELL_HEIGHT))
        for i in range(len(TEN_THU_TRONG_TUAN) + 1):
            x = self.TIME_COL_WIDTH + i * self.CELL_WIDTH
            painter.drawLine(int(x), 0, int(x), self.height())
            
    def _draw_busy_times(self, painter):
        """Vẽ các giờ bận lên lưới với màu và font khác với môn học"""
        if not self.busy_times:
            return
        
        is_dark = self._is_dark_mode()
        # Màu xám nhạt cho giờ bận (khác với môn học)
        busy_color = QColor("#f0f0f0") if not is_dark else QColor("#3a3a3a")
        border_color = QColor("#cccccc") if not is_dark else QColor("#666666")
        text_color = QColor("#666666") if not is_dark else QColor("#aaaaaa")  # Text màu xám
        
        for busy_time in self.busy_times:
            # Chuyển đổi giờ sang tiết
            tiet_bd = busy_time.time_to_tiet(busy_time.gio_bat_dau)
            tiet_kt = busy_time.time_to_tiet(busy_time.gio_ket_thuc)
            
            # Nếu không tìm được tiết chính xác, tìm tiết gần nhất
            from ..models import LichBan
            if tiet_bd == -1:
                tiet_bd = LichBan._find_nearest_tiet(busy_time.gio_bat_dau)
            if tiet_kt == -1:
                tiet_kt = LichBan._find_nearest_tiet(busy_time.gio_ket_thuc)
            
            if tiet_bd == -1 or tiet_kt == -1:
                continue  # Bỏ qua nếu không chuyển đổi được
            
            # Đảm bảo tiet_bd <= tiet_kt
            if tiet_bd > tiet_kt:
                tiet_bd, tiet_kt = tiet_kt, tiet_bd
            
            thu_index = busy_time.thu - 2  # 2 (Thứ 2) -> index 0
            if 0 <= thu_index < len(TEN_THU_TRONG_TUAN):
                x = self.TIME_COL_WIDTH + thu_index * self.CELL_WIDTH
                y = self.HEADER_HEIGHT + (tiet_bd - 1) * self.CELL_HEIGHT
                rect_width = self.CELL_WIDTH
                rect_height = (tiet_kt - tiet_bd + 1) * self.CELL_HEIGHT
                
                # Vẽ vùng giờ bận với màu xám nhạt
                painter.setBrush(QBrush(busy_color))
                painter.setPen(QPen(border_color, 1))
                painter.drawRoundedRect(int(x)+2, int(y)+2, int(rect_width)-4, 
                                      int(rect_height)-4, 5, 5)
                
                # Vẽ text với font nhỏ hơn và màu khác
                painter.setPen(text_color)
                painter.setFont(QFont("Segoe UI", 9))  # Font nhỏ hơn (9 thay vì 12)
                text_rect = int(x)+5, int(y)+5, int(rect_width)-10, int(rect_height)-10
                text_flags = Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap
                
                # Format text hiển thị thông tin giờ bận và lý do (ngắn gọn hơn)
                gio_bd_str = busy_time.gio_bat_dau.toString("HH:mm")
                gio_kt_str = busy_time.gio_ket_thuc.toString("HH:mm")
                ten_thu = TEN_THU_TRONG_TUAN.get(busy_time.thu, f"Thứ {busy_time.thu}")
                # Rút gọn text để tránh vỡ chữ
                ly_do_short = busy_time.ly_do[:15] + "..." if len(busy_time.ly_do) > 15 else busy_time.ly_do
                text_content = f"BẬN\n{ten_thu}\n{gio_bd_str}-{gio_kt_str}\n{ly_do_short}"
                
                painter.drawText(text_rect[0], text_rect[1], text_rect[2], text_rect[3], 
                               text_flags, text_content)
    
    def _draw_schedule(self, painter):
        """Vẽ các lớp học lên lưới"""
        is_dark = self._is_dark_mode()
        border_color = QColor("#888888") if is_dark else QColor("#666666")
        text_color = QColor("#000000") if is_dark else QColor("#000000")
        
        for lop_hoc in self.current_schedule:
            for khung_gio in lop_hoc.cac_khung_gio:
                thu_index = khung_gio.thu - 2  # 2 (Thứ 2) -> index 0
                if 0 <= thu_index < len(TEN_THU_TRONG_TUAN):
                    x = self.TIME_COL_WIDTH + thu_index * self.CELL_WIDTH
                    y = self.HEADER_HEIGHT + (khung_gio.tiet_bat_dau - 1) * self.CELL_HEIGHT
                    rect_width = self.CELL_WIDTH
                    rect_height = (khung_gio.tiet_ket_thuc - khung_gio.tiet_bat_dau + 1) * self.CELL_HEIGHT
                    color = QColor(self.schedule_colors.get(lop_hoc.ma_mon, "#ffffff"))
                    painter.setBrush(QBrush(color))
                    
                    # Kiểm tra xem lớp này có ràng buộc không
                    is_constrained = id(lop_hoc) in self.constrained_classes
                    if is_constrained:
                        # Lớp ràng buộc: dùng border dày hơn và màu đặc biệt
                        constraint_border_color = QColor("#FF6600")  # Màu cam
                        painter.setPen(QPen(constraint_border_color, 3))  # Border dày hơn
                    else:
                        painter.setPen(QPen(border_color, 1))
                    
                    painter.drawRoundedRect(int(x)+2, int(y)+2, int(rect_width)-4, 
                                          int(rect_height)-4, 5, 5)
                    text_rect = int(x)+5, int(y)+5, int(rect_width)-10, int(rect_height)-10
                    text_rect_x, text_rect_y, text_rect_w, text_rect_h = text_rect
                    
                    # Tính tổng chiều cao của tất cả các phần text trước để căn giữa
                    # Lấy loại lớp (nếu có)
                    loai_lop = getattr(lop_hoc, 'loai_lop', 'Lớp')
                    
                    painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
                    # Hiển thị loại lớp nếu là Lý thuyết hoặc Bài tập
                    if loai_lop in ["Lý thuyết", "Bài tập"]:
                        ma_lop_text = f"[{loai_lop}] {lop_hoc.ma_lop}"
                    else:
                        ma_lop_text = f"Lớp: {lop_hoc.ma_lop}"
                    font_metrics = painter.fontMetrics()
                    ma_lop_rect = font_metrics.boundingRect(
                        text_rect_x, text_rect_y, text_rect_w, 0,
                        Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, ma_lop_text
                    )
                    ma_lop_height = ma_lop_rect.height()
                    
                    painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
                    ten_mon_font_metrics = painter.fontMetrics()
                    ten_mon_rect = ten_mon_font_metrics.boundingRect(
                        text_rect_x, text_rect_y, text_rect_w, 0,
                        Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, lop_hoc.ten_mon
                    )
                    ten_mon_height = ten_mon_rect.height()
                    
                    painter.setFont(QFont("Segoe UI", 9))
                    normal_font_metrics = painter.fontMetrics()
                    ma_mon_text = f"({lop_hoc.ma_mon})"
                    ma_mon_rect = normal_font_metrics.boundingRect(
                        text_rect_x, text_rect_y, text_rect_w, 0,
                        Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, ma_mon_text
                    )
                    ma_mon_height = ma_mon_rect.height()
                    
                    gv_text = f"GV: {lop_hoc.ten_giao_vien}"
                    gv_rect = normal_font_metrics.boundingRect(
                        text_rect_x, text_rect_y, text_rect_w, 0,
                        Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, gv_text
                    )
                    gv_height = gv_rect.height()
                    
                    # Tính tổng chiều cao (bao gồm khoảng cách giữa các dòng)
                    spacing = 2
                    total_text_height = ma_lop_height + spacing + ten_mon_height + spacing + ma_mon_height + spacing + gv_height
                    
                    # Tính offset để căn giữa theo chiều dọc (chuyển sang int)
                    vertical_offset = int((text_rect_h - total_text_height) / 2)
                    current_y = text_rect_y + vertical_offset
                    
                    # Vẽ mã lớp to hơn, đậm và màu khác
                    painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
                    ma_lop_color = QColor("#0066CC") 
                    painter.setPen(ma_lop_color)
                    painter.drawText(text_rect_x, current_y, text_rect_w, ma_lop_height,
                                   Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, ma_lop_text)
                    current_y += ma_lop_height + spacing
                    
                    # Vẽ tên môn với word wrap, màu riêng, cỡ chữ lớn hơn và in đậm
                    ten_mon_color = QColor("#DC143C")
                    painter.setPen(ten_mon_color)
                    painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
                    painter.drawText(text_rect_x, current_y, text_rect_w, ten_mon_height,
                                   Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, lop_hoc.ten_mon)
                    painter.setFont(QFont("Segoe UI", 9))
                    painter.setPen(text_color)
                    current_y += ten_mon_height + spacing
                    
                    # Vẽ mã môn với word wrap
                    painter.drawText(text_rect_x, current_y, text_rect_w, ma_mon_height,
                                   Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, ma_mon_text)
                    current_y += ma_mon_height + spacing
                    
                    # Vẽ giáo viên với word wrap
                    painter.drawText(text_rect_x, current_y, text_rect_w, gv_height,
                                   Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, gv_text)

    def display_schedule(self, tkb, all_courses, busy_times=None):
        """Hiển thị một thời khóa biểu lên widget"""
        self.current_schedule = tkb
        self.busy_times = busy_times or []
        self.schedule_colors.clear()
        # Tạo set các lớp ràng buộc để hiển thị đặc biệt (dùng object reference)
        from ..scheduler import _find_lop_by_id_helper
        self.constrained_classes = set()
        for lop in tkb:
            if lop.lop_rang_buoc:
                # Thêm lớp này vào set (có ràng buộc)
                self.constrained_classes.add(id(lop))
                # Thêm các lớp ràng buộc vào set (sử dụng helper để tìm chính xác)
                for rang_buoc_id in lop.lop_rang_buoc:
                    # Tìm lớp ràng buộc bằng helper (hỗ trợ cả format cũ và mới)
                    lop_rang_buoc = _find_lop_by_id_helper(rang_buoc_id, all_courses)
                    if lop_rang_buoc:
                        # Tìm lớp này trong TKB (so sánh bằng object reference)
                        for lop_khac in tkb:
                            if lop_khac is lop_rang_buoc:
                                self.constrained_classes.add(id(lop_khac))
                                break
        for ma_mon, mon_hoc in all_courses.items():
            if mon_hoc.color_hex:
                self.schedule_colors[ma_mon] = mon_hoc.color_hex
        self.update()

    def display_schedule_partial(self, tkb, all_courses, busy_times=None, dirty_rects=None):
        """
        Cập nhật TKB và/hoặc giờ bận nhưng chỉ repaint các vùng cần thiết.
        dirty_rects: danh sách QRect (tọa độ theo widget) cần update.
        """
        self.current_schedule = tkb
        self.busy_times = busy_times or []
        self.schedule_colors.clear()

        from ..scheduler import _find_lop_by_id_helper
        self.constrained_classes = set()
        for lop in tkb:
            if lop.lop_rang_buoc:
                self.constrained_classes.add(id(lop))
                for rang_buoc_id in lop.lop_rang_buoc:
                    lop_rang_buoc = _find_lop_by_id_helper(rang_buoc_id, all_courses)
                    if lop_rang_buoc:
                        for lop_khac in tkb:
                            if lop_khac is lop_rang_buoc:
                                self.constrained_classes.add(id(lop_khac))
                                break

        for ma_mon, mon_hoc in all_courses.items():
            if mon_hoc.color_hex:
                self.schedule_colors[ma_mon] = mon_hoc.color_hex

        if dirty_rects:
            for rect in dirty_rects:
                self.update(rect)
        else:
            # Fallback: repaint toàn bộ nếu không cung cấp vùng cụ thể
            self.update()

