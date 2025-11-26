"""
Các dialog dùng để nhập liệu
"""

from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDialogButtonBox,
    QComboBox, QSpinBox
)

from ..constants import TEN_THU_TRONG_TUAN


class SubjectDialog(QDialog):
    """Dialog để thêm hoặc sửa môn học"""
    
    def __init__(self, parent=None, mon_hoc=None):
        super().__init__(parent)
        self.setWindowTitle("Thêm Môn học mới" if not mon_hoc else "Chỉnh sửa Môn học")
        self.layout = QFormLayout(self)
        
        self.ma_mon_edit = QLineEdit()
        self.ten_mon_edit = QLineEdit()
        self.tien_quyet_edit = QLineEdit()
        self.tien_quyet_edit.setPlaceholderText("VD: MI1111, IT1110 (cách nhau bởi dấu phẩy)")
        
        if mon_hoc:
            self.ma_mon_edit.setText(mon_hoc.ma_mon)
            self.ma_mon_edit.setReadOnly(True)  # Không cho sửa Mã môn (ID)
            self.ten_mon_edit.setText(mon_hoc.ten_mon)
            self.tien_quyet_edit.setText(", ".join(mon_hoc.tien_quyet))

        self.layout.addRow("Mã môn:", self.ma_mon_edit)
        self.layout.addRow("Tên môn:", self.ten_mon_edit)
        self.layout.addRow("Môn tiên quyết:", self.tien_quyet_edit)
        
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def get_data(self):
        """Lấy dữ liệu từ dialog"""
        ma_mon = self.ma_mon_edit.text().strip().upper()
        ten_mon = self.ten_mon_edit.text().strip()
        tien_quyet = [ma.strip().upper() 
                     for ma in self.tien_quyet_edit.text().split(',') if ma.strip()]
        if not ma_mon or not ten_mon:
            return None
        return {'ma_mon': ma_mon, 'ten_mon': ten_mon, 'tien_quyet': tien_quyet}


class ClassDialog(QDialog):
    """Dialog để thêm lớp học mới"""
    
    def __init__(self, all_courses, default_thu=None, default_tiet=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Thêm Lớp học mới")
        self.all_courses = all_courses
        self.layout = QFormLayout(self)
        
        self.mon_hoc_combo = QComboBox()
        self.mon_hoc_combo.addItems(sorted(all_courses.keys()))
        self.ma_lop_edit = QLineEdit()
        self.ten_gv_edit = QLineEdit()
        self.thu_combo = QComboBox()
        self.thu_combo.addItems(TEN_THU_TRONG_TUAN.values())
        self.tiet_bd_spin = QSpinBox()
        self.tiet_bd_spin.setRange(1, 12)
        self.tiet_kt_spin = QSpinBox()
        self.tiet_kt_spin.setRange(1, 12)
        
        if default_thu:
            self.thu_combo.setCurrentText(TEN_THU_TRONG_TUAN.get(default_thu, "Thứ 2"))
        if default_tiet:
            self.tiet_bd_spin.setValue(default_tiet)
            self.tiet_kt_spin.setValue(default_tiet)
        
        self.layout.addRow("Môn học:", self.mon_hoc_combo)
        self.layout.addRow("Mã lớp:", self.ma_lop_edit)
        self.layout.addRow("Tên GV:", self.ten_gv_edit)
        self.layout.addRow("Thứ:", self.thu_combo)
        self.layout.addRow("Tiết bắt đầu:", self.tiet_bd_spin)
        self.layout.addRow("Tiết kết thúc:", self.tiet_kt_spin)
        
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def get_data(self):
        """Lấy dữ liệu từ dialog"""
        ma_mon = self.mon_hoc_combo.currentText()
        ma_lop = self.ma_lop_edit.text().strip().upper()
        ten_gv = self.ten_gv_edit.text().strip()
        ten_thu = self.thu_combo.currentText()
        thu = [k for k, v in TEN_THU_TRONG_TUAN.items() if v == ten_thu][0]
        tiet_bd = self.tiet_bd_spin.value()
        tiet_kt = self.tiet_kt_spin.value()
        if not ma_mon or not ma_lop or not ten_gv or tiet_bd > tiet_kt:
            return None
        return {
            'ma_mon': ma_mon, 
            'ma_lop': ma_lop, 
            'ten_gv': ten_gv, 
            'thu': thu, 
            'tiet_bd': tiet_bd, 
            'tiet_kt': tiet_kt
        }

