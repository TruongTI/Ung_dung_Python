"""
Entry point của ứng dụng TKB Planner Pro
"""

import os
import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from tkb_planner.ui.main_window import MainWindow


def main():
    """Hàm main để chạy ứng dụng với hỗ trợ High DPI"""
    # Bật High DPI scaling để PyQt tự động scale theo DPI hệ thống
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
    os.environ.setdefault("QT_SCALE_FACTOR_ROUNDING_POLICY", "Round")

    app = QApplication(sys.argv)

    # Thiết lập chính sách rounding cho scale factor (nếu hỗ trợ)
    try:
        app.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
    except AttributeError:
        # Một số phiên bản/ hệ thống có thể không hỗ trợ, bỏ qua an toàn
        pass

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

