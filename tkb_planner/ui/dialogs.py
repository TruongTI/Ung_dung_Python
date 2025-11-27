"""
Các dialog dùng để nhập liệu
"""

from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDialogButtonBox,
    QComboBox, QSpinBox, QVBoxLayout, QListWidget, QPushButton,
    QLabel, QHBoxLayout, QMessageBox, QScrollArea, QWidget, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

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
    
    def __init__(self, all_courses, default_thu=None, default_tiet=None, fixed_mon_hoc=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Thêm Lớp học mới")
        self.all_courses = all_courses
        self.layout = QFormLayout(self)
        
        self.mon_hoc_combo = QComboBox()
        self.mon_hoc_combo.addItems(sorted(all_courses.keys()))
        # Nếu có fixed_mon_hoc, set và disable combo box
        if fixed_mon_hoc:
            self.mon_hoc_combo.setCurrentText(fixed_mon_hoc.ma_mon)
            self.mon_hoc_combo.setEnabled(False)
        self.ma_lop_edit = QLineEdit()
        self.ten_gv_edit = QLineEdit()
        # Combo box để chọn loại lớp
        self.loai_lop_combo = QComboBox()
        self.loai_lop_combo.addItems(["Lý thuyết", "Bài tập", "Lớp"])
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
        self.layout.addRow("Phòng học:", self.ma_lop_edit)
        self.layout.addRow("Tên GV:", self.ten_gv_edit)
        self.layout.addRow("Loại lớp:", self.loai_lop_combo)
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
        from ..models import chuan_hoa_ma_lop, chuan_hoa_ten_giao_vien
        
        ma_mon = self.mon_hoc_combo.currentText()
        ma_lop_raw = self.ma_lop_edit.text().strip()
        ten_gv_raw = self.ten_gv_edit.text().strip()
        loai_lop = self.loai_lop_combo.currentText()
        ten_thu = self.thu_combo.currentText()
        thu = [k for k, v in TEN_THU_TRONG_TUAN.items() if v == ten_thu][0]
        tiet_bd = self.tiet_bd_spin.value()
        tiet_kt = self.tiet_kt_spin.value()
        
        # Chuẩn hóa định dạng
        ma_lop = chuan_hoa_ma_lop(ma_lop_raw)
        ten_gv = chuan_hoa_ten_giao_vien(ten_gv_raw)
        
        if not ma_mon or not ma_lop or not ten_gv or tiet_bd > tiet_kt:
            return None
        return {
            'ma_mon': ma_mon, 
            'ma_lop': ma_lop, 
            'ten_gv': ten_gv,
            'loai_lop': loai_lop,
            'thu': thu, 
            'tiet_bd': tiet_bd, 
            'tiet_kt': tiet_kt
        }


class CompletedCoursesDialog(QDialog):
    """Dialog để nhập môn đã học"""
    
    def __init__(self, all_courses, completed_courses=None, add_course_callback=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nhập môn đã học")
        self.all_courses = all_courses
        self.completed_courses = completed_courses or []
        self.add_course_callback = add_course_callback  # Callback để thêm môn mới
        
        layout = QVBoxLayout(self)
        
        # Label hướng dẫn
        label = QLabel("Chọn các môn đã học (có thể chọn nhiều môn):")
        layout.addWidget(label)
        
        # List widget để chọn môn
        self.course_list = QListWidget()
        self.course_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        
        # Thêm các môn học vào list
        self._populate_course_list()
        
        layout.addWidget(self.course_list)
        
        # Nút thêm môn
        if self.add_course_callback:
            add_button_layout = QHBoxLayout()
            add_button = QPushButton("Thêm môn")
            add_button.clicked.connect(self.handle_add_course)
            add_button_layout.addWidget(add_button)
            add_button_layout.addStretch()
            layout.addLayout(add_button_layout)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _populate_course_list(self):
        """Cập nhật danh sách môn học trong list widget"""
        self.course_list.clear()
        for ma_mon in sorted(self.all_courses.keys()):
            mon_hoc = self.all_courses[ma_mon]
            item_text = f"{mon_hoc.ten_mon} ({ma_mon})"
            self.course_list.addItem(item_text)
            
            # Đánh dấu các môn đã học và disable để không thể bỏ chọn
            item = self.course_list.item(self.course_list.count() - 1)
            if ma_mon in self.completed_courses:
                item.setSelected(True)
                # Disable item để không thể bỏ chọn (giữ lại ItemIsSelectable để vẫn hiển thị được)
                flags = item.flags()
                flags &= ~Qt.ItemFlag.ItemIsEnabled
                item.setFlags(flags)
                # Thêm tooltip để giải thích
                item.setToolTip("Môn này đã được đánh dấu là đã học và không thể bỏ chọn")
                # Hiển thị gạch ngang cho môn đã học
                font = item.font()
                font.setStrikeOut(True)
                item.setFont(font)
            else:
                # Đảm bảo các môn không còn trong danh sách môn đã học được hiển thị bình thường
                item.setSelected(False)
                # Enable item để có thể chọn
                flags = item.flags()
                flags |= Qt.ItemFlag.ItemIsEnabled
                item.setFlags(flags)
                # Bỏ gạch ngang nếu có
                font = item.font()
                font.setStrikeOut(False)
                item.setFont(font)
                item.setToolTip("")
    
    def handle_add_course(self):
        """Xử lý thêm môn mới"""
        if not self.add_course_callback:
            return
        
        # Gọi callback để thêm môn mới
        new_ma_mon = self.add_course_callback()
        if new_ma_mon:
            # Cập nhật lại danh sách (giữ nguyên các môn đã học)
            self._populate_course_list()
            
            # Tự động chọn môn vừa thêm (chỉ nếu chưa có trong danh sách môn đã học)
            if new_ma_mon not in self.completed_courses:
                for i in range(self.course_list.count()):
                    item = self.course_list.item(i)
                    text = item.text()
                    if '(' in text and ')' in text:
                        ma_mon = text.split('(')[1].split(')')[0].strip()
                        if ma_mon == new_ma_mon:
                            item.setSelected(True)
                            self.course_list.scrollToItem(item)
                            break
    
    def get_selected_courses(self):
        """Lấy danh sách mã môn đã chọn (bao gồm cả các môn đã học không thể bỏ chọn)"""
        selected_items = self.course_list.selectedItems()
        selected_courses = []
        for item in selected_items:
            # Lấy mã môn từ text (format: "Tên môn (Mã môn)")
            text = item.text()
            if '(' in text and ')' in text:
                ma_mon = text.split('(')[1].split(')')[0].strip()
                selected_courses.append(ma_mon)
        
        # Thêm các môn đã học (không thể bỏ chọn) vào danh sách
        for ma_mon in self.completed_courses:
            if ma_mon not in selected_courses:
                selected_courses.append(ma_mon)
        
        return selected_courses


class ViewCompletedCoursesDialog(QDialog):
    """Dialog để hiển thị danh sách môn đã học"""
    
    def __init__(self, all_courses, completed_courses, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Danh sách môn đã học")
        self.setMinimumSize(500, 400)
        self.all_courses = all_courses
        self.completed_courses = completed_courses.copy()  # Sao chép để có thể chỉnh sửa
        
        layout = QVBoxLayout(self)
        
        # Label
        self.label = QLabel(f"Tổng số môn đã học: {len(completed_courses)}")
        layout.addWidget(self.label)
        
        # List widget để hiển thị với checkbox
        self.course_list = QListWidget()
        self.course_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        
        if completed_courses:
            for ma_mon in sorted(completed_courses):
                if ma_mon in all_courses:
                    mon_hoc = all_courses[ma_mon]
                    item_text = f"{mon_hoc.ten_mon} ({ma_mon})"
                    self.course_list.addItem(item_text)
                    # Lấy item vừa thêm (item cuối cùng)
                    item = self.course_list.item(self.course_list.count() - 1)
                    item.setSelected(False)  # Mặc định không chọn
                else:
                    # Môn không còn trong danh sách
                    item_text = f"{ma_mon} (Môn không còn trong hệ thống)"
                    self.course_list.addItem(item_text)
                    # Lấy item vừa thêm (item cuối cùng)
                    item = self.course_list.item(self.course_list.count() - 1)
                    item.setSelected(False)
        else:
            self.course_list.addItem("Chưa có môn nào được đánh dấu là đã học")
        
        layout.addWidget(self.course_list)
        
        # Nút xóa
        button_layout = QHBoxLayout()
        delete_button = QPushButton("Xóa các môn đã chọn")
        delete_button.clicked.connect(self.handle_delete_selected)
        button_layout.addWidget(delete_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Buttons - Thêm cả OK và Close để có thể xác nhận thay đổi
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Close
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def handle_delete_selected(self):
        """Xóa các môn đã chọn khỏi danh sách môn đã học"""
        selected_items = self.course_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Chưa chọn môn", "Vui lòng chọn ít nhất một môn để xóa.")
            return
        
        # Lấy danh sách mã môn cần xóa
        courses_to_remove = []
        for item in selected_items:
            text = item.text()
            if '(' in text and ')' in text:
                ma_mon = text.split('(')[1].split(')')[0].strip()
                if ma_mon in self.completed_courses:
                    courses_to_remove.append(ma_mon)
        
        if not courses_to_remove:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy môn nào để xóa.")
            return
        
        # Xác nhận xóa
        reply = QMessageBox.question(
            self, 'Xác nhận xóa', 
            f"Bạn có chắc muốn xóa {len(courses_to_remove)} môn khỏi danh sách môn đã học?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Xóa khỏi danh sách
            for ma_mon in courses_to_remove:
                self.completed_courses.remove(ma_mon)
            
            # Cập nhật lại danh sách hiển thị
            self.course_list.clear()
            if self.completed_courses:
                for ma_mon in sorted(self.completed_courses):
                    if ma_mon in self.all_courses:
                        mon_hoc = self.all_courses[ma_mon]
                        item_text = f"{mon_hoc.ten_mon} ({ma_mon})"
                        self.course_list.addItem(item_text)
                        # Lấy item vừa thêm (item cuối cùng)
                        item = self.course_list.item(self.course_list.count() - 1)
                        item.setSelected(False)
                    else:
                        item_text = f"{ma_mon} (Môn không còn trong hệ thống)"
                        self.course_list.addItem(item_text)
                        # Lấy item vừa thêm (item cuối cùng)
                        item = self.course_list.item(self.course_list.count() - 1)
                        item.setSelected(False)
            else:
                self.course_list.addItem("Chưa có môn nào được đánh dấu là đã học")
            
            # Cập nhật label
            self.label.setText(f"Tổng số môn đã học: {len(self.completed_courses)}")
            
            QMessageBox.information(self, "Thành công", 
                                  f"Đã xóa {len(courses_to_remove)} môn khỏi danh sách môn đã học.")
    
    def get_updated_completed_courses(self):
        """Lấy danh sách môn đã học sau khi chỉnh sửa"""
        return self.completed_courses

