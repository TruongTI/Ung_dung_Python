"""
Entry point của ứng dụng TKB Planner Pro
"""

import sys
from PyQt6.QtWidgets import QApplication
from tkb_planner.ui.main_window import MainWindow


def main():
    """Hàm main để chạy ứng dụng"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

