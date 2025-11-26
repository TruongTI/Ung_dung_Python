"""
Widget hiển thị thời khóa biểu dạng lưới
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QColor, QBrush, QPen
from PyQt6.QtWidgets import QSizePolicy

from ..constants import TEN_THU_TRONG_TUAN


class ScheduleWidget(QWidget):
    """Widget hiển thị thời khóa biểu dạng lưới với khả năng click vào ô"""
    
    cellClicked = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(800, 600)
        self.current_schedule = []
        self.CELL_WIDTH = 120
        self.CELL_HEIGHT = 50
        self.HEADER_HEIGHT = 60
        self.TIME_COL_WIDTH = 60
        self.MAX_TIET = 12
        self.schedule_colors = {}
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
        self._draw_schedule(painter)
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
            
    def _draw_schedule(self, painter):
        """Vẽ các lớp học lên lưới"""
        is_dark = self._is_dark_mode()
        border_color = QColor("#888888") if is_dark else QColor("#666666")
        text_color = QColor("#ffffff") if is_dark else QColor("#000000")
        
        for lop_hoc in self.current_schedule:
            for khung_gio in lop_hoc.cac_khung_gio:
                thu_index = khung_gio.thu - 2  # 2 (Thứ 2) -> index 0
                if 0 <= thu_index < len(TEN_THU_TRONG_TUAN):
                    x = self.TIME_COL_WIDTH + thu_index * self.CELL_WIDTH
                    y = self.HEADER_HEIGHT + (khung_gio.tiet_bat_dau - 1) * self.CELL_HEIGHT
                    rect_width = self.CELL_WIDTH
                    rect_height = (khung_gio.tiet_ket_thuc - khung_gio.tiet_bat_dau + 1) * self.CELL_HEIGHT
                    color = QColor(self.schedule_colors.get(lop_hoc.ma_mon, "#ADD8E6"))
                    painter.setBrush(QBrush(color))
                    painter.setPen(QPen(border_color, 1))
                    painter.drawRoundedRect(int(x)+2, int(y)+2, int(rect_width)-4, 
                                          int(rect_height)-4, 5, 5)
                    painter.setPen(text_color)
                    text_rect = int(x)+5, int(y)+5, int(rect_width)-10, int(rect_height)-10
                    text_flags = Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap
                    text_content = (f"{lop_hoc.ten_mon}\n({lop_hoc.ma_mon})\n"
                                  f"Lớp: {lop_hoc.ma_lop}\nGV: {lop_hoc.ten_giao_vien}")
                    painter.drawText(text_rect[0], text_rect[1], text_rect[2], text_rect[3], 
                                   text_flags, text_content)

    def display_schedule(self, tkb, all_courses):
        """Hiển thị một thời khóa biểu lên widget"""
        self.current_schedule = tkb
        self.schedule_colors.clear()
        for ma_mon, mon_hoc in all_courses.items():
            if mon_hoc.color_hex:
                self.schedule_colors[ma_mon] = mon_hoc.color_hex
        self.update()

