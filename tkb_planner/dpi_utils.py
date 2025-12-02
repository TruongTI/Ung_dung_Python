"""
Các helper liên quan đến DPI để giao diện hiển thị hài hòa trên nhiều màn hình
(laptop DPI cao, màn hình PC DPI thấp).
"""

from PyQt6.QtGui import QGuiApplication
from PyQt6.QtCore import QRect


def get_dpi_scale_factor() -> float:
    """
    Tính toán DPI scale factor dựa trên màn hình chính.

    - 96 DPI được coi là 100% (scale = 1.0)
    - Trả về giá trị tối thiểu 1.0 để tránh font quá nhỏ trên màn hình DPI thấp
    """
    screen = QGuiApplication.primaryScreen()
    if not screen:
        return 1.0
    dpi = screen.logicalDotsPerInch()
    return max(1.0, dpi / 96.0)


def get_scaled_font_size(base_size: int = 10, min_size: int = 9) -> int:
    """
    Trả về cỡ chữ đã scale theo DPI, với cỡ tối thiểu min_size.
    """
    scale = get_dpi_scale_factor()
    return max(min_size, int(base_size * scale))


def get_screen_geometry() -> QRect:
    """
    Lấy geometry của màn hình chính (availableGeometry).
    Dùng để tính toán kích thước/position cửa sổ theo phần trăm màn hình.
    """
    screen = QGuiApplication.primaryScreen()
    if not screen:
        # Fallback nếu không lấy được screen
        return QRect(0, 0, 1280, 800)
    return screen.availableGeometry()


