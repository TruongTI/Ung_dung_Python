"""
Custom Checkbox với nền xanh lá cây và checkmark màu trắng
"""

from PyQt6.QtWidgets import QCheckBox, QStyleOptionButton
from PyQt6.QtCore import Qt, QRect, QSize, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QMouseEvent


class CustomCheckBox(QCheckBox):
    """Checkbox tùy chỉnh với nền xanh lá cây và checkmark màu trắng"""
    
    # Signal khi click vào text (không toggle checkbox)
    textClicked = pyqtSignal()
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        # Đảm bảo checkbox có kích thước tối thiểu phù hợp
        self.setMinimumHeight(22)
        # Bật mouse tracking để phát hiện hover
        self.setMouseTracking(True)
        self._is_hovered = False
        self._allow_text_click = False  # Flag để cho phép click vào text
    
    def enterEvent(self, event):
        """Khi chuột vào checkbox"""
        self._is_hovered = True
        self.update()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Khi chuột rời khỏi checkbox"""
        self._is_hovered = False
        self.update()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Xử lý sự kiện click chuột"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Kích thước indicator
            indicator_size = 20
            indicator_x = 1
            indicator_y = max(0, (self.height() - indicator_size) // 2)
            indicator_rect = QRect(indicator_x, indicator_y, indicator_size, indicator_size)
            
            # Kiểm tra xem click vào indicator hay text
            if indicator_rect.contains(event.pos()):
                # Click vào indicator - toggle checkbox bình thường
                super().mousePressEvent(event)
            else:
                # Click vào text - chỉ phát signal, không toggle checkbox
                if self._allow_text_click:
                    self.textClicked.emit()
                else:
                    # Nếu không cho phép click vào text, vẫn toggle checkbox
                    super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)
    
    def set_allow_text_click(self, allow: bool):
        """Cho phép click vào text mà không toggle checkbox"""
        self._allow_text_click = allow
    
    def paintEvent(self, event):
        """Vẽ checkbox tùy chỉnh với nền xanh lá cây và checkmark màu trắng"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Lấy style option
        option = QStyleOptionButton()
        self.initStyleOption(option)
        
        # Kích thước checkbox indicator - căn chỉnh tốt hơn
        indicator_size = 20
        indicator_x = 1  # Thêm 1px để tránh bị hõm bên trái
        indicator_y = max(0, (self.height() - indicator_size) // 2)
        indicator_rect = QRect(indicator_x, indicator_y, indicator_size, indicator_size)
        
        # Kiểm tra theme
        try:
            is_dark = self.palette().color(self.palette().ColorRole.Window).lightness() < 128
        except:
            is_dark = False
        
        # Xác định màu border và background
        if self.isChecked():
            # Checked: nền xanh lá cây tươi, border xanh lá cây
            green_color = QColor("#22c55e")  # Màu xanh lá cây tươi
            bg_color = green_color
            border_color = green_color
        elif self._is_hovered:
            # Hover: border màu xanh lá cây
            border_color = QColor("#22c55e")
            bg_color = QColor("#1e1e1e") if is_dark else QColor("#ffffff")
        else:
            # Unchecked: border xám
            border_color = QColor("#666666") if is_dark else QColor("#999999")
            bg_color = QColor("#1e1e1e") if is_dark else QColor("#ffffff")
        
        # Vẽ checkbox indicator
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, 2))
        painter.drawRoundedRect(indicator_rect, 4, 4)
        
        # Vẽ checkmark màu trắng nếu checked
        if self.isChecked():
            # Màu trắng cho checkmark
            white_color = QColor("#ffffff")
            
            painter.setPen(QPen(white_color, 3))
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Vẽ checkmark hình chữ V với thanh trái thẳng đứng, cao hơn, gần thanh phải hơn
            # Điểm bắt đầu: trái (cao hơn, gần giữa trên)
            start_x = indicator_x + 5
            start_y = indicator_y + 10  # Bắt đầu từ trên, cao hơn
            # Điểm giữa: gần giữa dưới (đỉnh của chữ V, gần nhau hơn)
            mid_x = indicator_x + indicator_size // 2 - 1  # Gần nhau hơn (chỉ cách 1px)
            mid_y = indicator_y + indicator_size - 5  # Điểm thấp nhất của chữ V
            # Điểm kết thúc: phải trên
            end_x = indicator_x + indicator_size - 5
            end_y = indicator_y + 5
            
            # Vẽ đường từ trái trên (thẳng đứng) xuống giữa dưới (tạo cạnh trái thẳng của chữ V)
            painter.drawLine(start_x, start_y, mid_x, mid_y)
            # Vẽ đường từ giữa dưới lên phải trên (tạo cạnh phải của chữ V)
            painter.drawLine(mid_x, mid_y, end_x, end_y)
        
        # Vẽ text - căn chỉnh tốt
        text_x = indicator_size + 6
        text_rect = QRect(
            text_x, 
            0, 
            max(0, self.width() - text_x), 
            self.height()
        )
        
        # Lấy màu text từ palette
        try:
            text_color = self.palette().color(self.palette().ColorRole.WindowText)
        except:
            text_color = QColor("#000000") if not is_dark else QColor("#e0e0e0")
        
        painter.setPen(QPen(text_color))
        
        # Vẽ text với căn chỉnh
        font_metrics = painter.fontMetrics()
        text_y_centered = (self.height() - font_metrics.height()) // 2 + font_metrics.ascent()
        
        if text_rect.width() > 0 and self.text():
            painter.drawText(
                text_rect.x(),
                text_y_centered,
                self.text()
            )
        
        painter.end()
    
    def sizeHint(self):
        """Trả về kích thước đề xuất"""
        base_size = super().sizeHint()
        return QSize(base_size.width() + 2, max(base_size.height(), 22))
    
    def minimumSizeHint(self):
        """Trả về kích thước tối thiểu"""
        return QSize(20 + 6 + 50, 22)
