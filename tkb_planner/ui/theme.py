"""
Quản lý theme (sáng/tối) cho ứng dụng
"""

# Theme sáng (Light Mode)
LIGHT_THEME = """
QMainWindow {
    background-color: #f5f5f5;
}

QWidget {
    background-color: #ffffff;
    color: #000000;
}

QGroupBox {
    font-weight: bold;
    border: 2px solid #cccccc;
    border-radius: 5px;
    margin-top: 10px;
    padding-top: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}

QPushButton {
    background-color: #e0e0e0;
    border: 1px solid #999999;
    border-radius: 4px;
    padding: 5px 15px;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #d0d0d0;
}

QPushButton:pressed {
    background-color: #b0b0b0;
}

QLineEdit, QTextEdit, QTextBrowser {
    background-color: #ffffff;
    border: 1px solid #cccccc;
    border-radius: 3px;
    padding: 3px;
    selection-background-color: #4a90e2;
}

QLineEdit:focus, QTextEdit:focus {
    border: 2px solid #4a90e2;
}

QCheckBox {
    spacing: 5px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #999999;
    border-radius: 3px;
    background-color: #ffffff;
}

QCheckBox::indicator:checked {
    background-color: #4a90e2;
    border-color: #4a90e2;
}

QScrollArea {
    border: 1px solid #cccccc;
    background-color: #ffffff;
}

QDateEdit, QTimeEdit {
    background-color: #ffffff;
    border: 1px solid #cccccc;
    border-radius: 3px;
    padding: 3px;
}

QTimeEdit::up-button, QDateEdit::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 16px;
    border-left: 1px solid #cccccc;
    border-top-right-radius: 3px;
    background-color: #f0f0f0;
}

QTimeEdit::up-button:hover, QDateEdit::up-button:hover {
    background-color: #e0e0e0;
}

QTimeEdit::up-button:pressed, QDateEdit::up-button:pressed {
    background-color: #d0d0d0;
}

QTimeEdit::down-button, QDateEdit::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 16px;
    border-left: 1px solid #cccccc;
    border-bottom-right-radius: 3px;
    background-color: #f0f0f0;
}

QTimeEdit::down-button:hover, QDateEdit::down-button:hover {
    background-color: #e0e0e0;
}

QTimeEdit::down-button:pressed, QDateEdit::down-button:pressed {
    background-color: #d0d0d0;
}

QTimeEdit::up-arrow, QDateEdit::up-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 5px solid #666666;
    width: 0px;
    height: 0px;
}

QTimeEdit::down-arrow, QDateEdit::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #666666;
    width: 0px;
    height: 0px;
}

QComboBox {
    background-color: #ffffff;
    border: 1px solid #cccccc;
    border-radius: 3px;
    padding: 3px;
}

QComboBox::drop-down {
    border: none;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid #666666;
    margin-right: 5px;
}

QSpinBox {
    background-color: #ffffff;
    border: 1px solid #cccccc;
    border-radius: 3px;
    padding: 3px;
}

QSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 16px;
    border-left: 1px solid #cccccc;
    border-top-right-radius: 3px;
    background-color: #f0f0f0;
}

QSpinBox::up-button:hover {
    background-color: #e0e0e0;
}

QSpinBox::up-button:pressed {
    background-color: #d0d0d0;
}

QSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 16px;
    border-left: 1px solid #cccccc;
    border-bottom-right-radius: 3px;
    background-color: #f0f0f0;
}

QSpinBox::down-button:hover {
    background-color: #e0e0e0;
}

QSpinBox::down-button:pressed {
    background-color: #d0d0d0;
}

QSpinBox::up-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 5px solid #666666;
    width: 0px;
    height: 0px;
}

QSpinBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #666666;
    width: 0px;
    height: 0px;
}

QStatusBar {
    background-color: #e0e0e0;
    color: #000000;
}

QMenuBar {
    background-color: #f0f0f0;
    color: #000000;
}

QMenuBar::item:selected {
    background-color: #d0d0d0;
}

QMenu {
    background-color: #ffffff;
    color: #000000;
    border: 1px solid #cccccc;
}

QMenu::item:selected {
    background-color: #4a90e2;
    color: #ffffff;
}
"""

# Theme tối (Dark Mode)
DARK_THEME = """
QMainWindow {
    background-color: #1e1e1e;
}

QWidget {
    background-color: #2d2d2d;
    color: #e0e0e0;
}

QGroupBox {
    font-weight: bold;
    border: 2px solid #555555;
    border-radius: 5px;
    margin-top: 10px;
    padding-top: 10px;
    color: #e0e0e0;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}

QPushButton {
    background-color: #404040;
    border: 1px solid #666666;
    border-radius: 4px;
    padding: 5px 15px;
    min-height: 20px;
    color: #e0e0e0;
}

QPushButton:hover {
    background-color: #505050;
}

QPushButton:pressed {
    background-color: #303030;
}

QLineEdit, QTextEdit, QTextBrowser {
    background-color: #1e1e1e;
    border: 1px solid #555555;
    border-radius: 3px;
    padding: 3px;
    color: #e0e0e0;
    selection-background-color: #4a90e2;
}

QLineEdit:focus, QTextEdit:focus {
    border: 2px solid #4a90e2;
}

QCheckBox {
    spacing: 5px;
    color: #e0e0e0;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #666666;
    border-radius: 3px;
    background-color: #1e1e1e;
}

QCheckBox::indicator:checked {
    background-color: #4a90e2;
    border-color: #4a90e2;
}

QScrollArea {
    border: 1px solid #555555;
    background-color: #2d2d2d;
}

QDateEdit, QTimeEdit {
    background-color: #1e1e1e;
    border: 1px solid #555555;
    border-radius: 3px;
    padding: 3px;
    color: #e0e0e0;
}

QTimeEdit::up-button, QDateEdit::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 16px;
    border-left: 1px solid #555555;
    border-top-right-radius: 3px;
    background-color: #404040;
}

QTimeEdit::up-button:hover, QDateEdit::up-button:hover {
    background-color: #505050;
}

QTimeEdit::up-button:pressed, QDateEdit::up-button:pressed {
    background-color: #303030;
}

QTimeEdit::down-button, QDateEdit::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 16px;
    border-left: 1px solid #555555;
    border-bottom-right-radius: 3px;
    background-color: #404040;
}

QTimeEdit::down-button:hover, QDateEdit::down-button:hover {
    background-color: #505050;
}

QTimeEdit::down-button:pressed, QDateEdit::down-button:pressed {
    background-color: #303030;
}

QTimeEdit::up-arrow, QDateEdit::up-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 5px solid #e0e0e0;
    width: 0px;
    height: 0px;
}

QTimeEdit::down-arrow, QDateEdit::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #e0e0e0;
    width: 0px;
    height: 0px;
}

QComboBox {
    background-color: #1e1e1e;
    border: 1px solid #555555;
    border-radius: 3px;
    padding: 3px;
    color: #e0e0e0;
}

QComboBox::drop-down {
    border: none;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid #e0e0e0;
    margin-right: 5px;
}

QComboBox QAbstractItemView {
    background-color: #2d2d2d;
    color: #e0e0e0;
    selection-background-color: #4a90e2;
}

QSpinBox {
    background-color: #1e1e1e;
    border: 1px solid #555555;
    border-radius: 3px;
    padding: 3px;
    color: #e0e0e0;
}

QSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 16px;
    border-left: 1px solid #555555;
    border-top-right-radius: 3px;
    background-color: #404040;
}

QSpinBox::up-button:hover {
    background-color: #505050;
}

QSpinBox::up-button:pressed {
    background-color: #303030;
}

QSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 16px;
    border-left: 1px solid #555555;
    border-bottom-right-radius: 3px;
    background-color: #404040;
}

QSpinBox::down-button:hover {
    background-color: #505050;
}

QSpinBox::down-button:pressed {
    background-color: #303030;
}

QSpinBox::up-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 5px solid #e0e0e0;
    width: 0px;
    height: 0px;
}

QSpinBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #e0e0e0;
    width: 0px;
    height: 0px;
}

QStatusBar {
    background-color: #2d2d2d;
    color: #e0e0e0;
}

QMenuBar {
    background-color: #2d2d2d;
    color: #e0e0e0;
}

QMenuBar::item:selected {
    background-color: #404040;
}

QMenu {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #555555;
}

QMenu::item:selected {
    background-color: #4a90e2;
    color: #ffffff;
}
"""


