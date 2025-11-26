"""
Dialog để hiển thị các lớp học của một môn học
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QScrollArea, QWidget, QGroupBox, QMessageBox, QDialogButtonBox
)
from PyQt6.QtCore import Qt

from ..constants import TEN_THU_TRONG_TUAN
from ..models import LopHoc
from .dialogs import ClassDialog


class CourseClassesDialog(QDialog):
    """Dialog để hiển thị các lớp học của một môn học"""
    
    def __init__(self, mon_hoc, all_courses=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Các lớp học - {mon_hoc.ten_mon} ({mon_hoc.ma_mon})")
        self.setMinimumSize(700, 500)
        self.mon_hoc = mon_hoc
        self.all_courses = all_courses or {mon_hoc.ma_mon: mon_hoc}
        self.deleted_classes = []  # Lưu các lớp đã xóa
        self.edited_classes = {}  # Lưu các lớp đã chỉnh sửa
        
        layout = QVBoxLayout(self)
        
        # Nút thêm lớp học
        add_class_btn = QPushButton("Thêm lớp học")
        add_class_btn.clicked.connect(self.handle_add_class)
        layout.addWidget(add_class_btn)
        
        # Scroll area để chứa các nhóm lớp
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        
        self._populate_classes()
        
        self.scroll.setWidget(self.scroll_widget)
        layout.addWidget(self.scroll)
        
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _create_class_widget(self, lop, gio, is_first_row):
        """Tạo widget hiển thị thông tin một khung giờ của lớp học"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 3, 5, 3)
        
        # Label mã lớp (chỉ hiển thị ở dòng đầu tiên)
        if is_first_row:
            ma_lop_label = QLabel(lop.ma_lop)
        else:
            ma_lop_label = QLabel("")
        layout.addWidget(ma_lop_label, 1)
        
        # Label giờ học (hiển thị dạng "Tiết X-Y")
        gio_label = QLabel(f"Tiết {gio.tiet_bat_dau}-{gio.tiet_ket_thuc}")
        layout.addWidget(gio_label, 1)
        
        # Label thứ
        ten_thu = TEN_THU_TRONG_TUAN.get(gio.thu, f"Thứ {gio.thu}")
        thu_label = QLabel(ten_thu)
        layout.addWidget(thu_label, 1)
        
        # Label tiết bắt đầu
        tiet_bd_label = QLabel(str(gio.tiet_bat_dau))
        layout.addWidget(tiet_bd_label, 1)
        
        # Label tiết kết thúc
        tiet_kt_label = QLabel(str(gio.tiet_ket_thuc))
        layout.addWidget(tiet_kt_label, 1)
        
        # Nút sửa (chỉ hiển thị ở dòng đầu tiên)
        if is_first_row:
            edit_btn = QPushButton("Sửa")
            edit_btn.setMinimumWidth(60)
            edit_btn.clicked.connect(lambda: self.handle_edit_class(lop))
            layout.addWidget(edit_btn, 0)
        else:
            layout.addWidget(QLabel(""), 0)
        
        # Nút xóa (chỉ hiển thị ở dòng đầu tiên)
        if is_first_row:
            delete_btn = QPushButton("Xóa")
            delete_btn.setMinimumWidth(60)
            delete_btn.clicked.connect(lambda: self.handle_delete_class(lop))
            layout.addWidget(delete_btn, 0)
        else:
            layout.addWidget(QLabel(""), 0)
        
        return widget
    
    def handle_edit_class(self, lop):
        """Xử lý sửa lớp học"""
        # Lưu lớp vào danh sách đã chỉnh sửa để xử lý sau
        self.edited_classes[lop.get_id()] = lop
        # Đóng dialog và trả về kết quả
        self.accept()
    
    def handle_delete_class(self, lop):
        """Xử lý xóa lớp học"""
        reply = QMessageBox.question(
            self, 'Xác nhận xóa', 
            f"Bạn có chắc muốn xóa lớp '{lop.ma_lop}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if lop not in self.deleted_classes:
                self.deleted_classes.append(lop)
            # Đóng dialog để áp dụng thay đổi
            self.accept()
    
    def get_deleted_classes(self):
        """Lấy danh sách các lớp đã xóa"""
        return self.deleted_classes
    
    def get_edited_classes(self):
        """Lấy danh sách các lớp đã chỉnh sửa"""
        return self.edited_classes
    
    def _populate_classes(self):
        """Điền danh sách các lớp vào scroll area"""
        # Xóa tất cả widget cũ
        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Phân loại các lớp theo loại
        classes_by_type = {
            "Lý thuyết": [],
            "Bài tập": [],
            "Lớp": []
        }
        
        for lop in self.mon_hoc.cac_lop_hoc:
            loai = getattr(lop, 'loai_lop', 'Lớp')
            if loai in classes_by_type:
                classes_by_type[loai].append(lop)
            else:
                classes_by_type["Lớp"].append(lop)
        
        # Hiển thị từng loại lớp
        for loai_lop in ["Lý thuyết", "Bài tập", "Lớp"]:
            if classes_by_type[loai_lop]:
                group = QGroupBox(loai_lop)
                group_layout = QVBoxLayout(group)
                
                # Header
                header_layout = QHBoxLayout()
                header_layout.addWidget(QLabel("Mã lớp"))
                header_layout.addWidget(QLabel("Giờ học"))
                header_layout.addWidget(QLabel("Thứ"))
                header_layout.addWidget(QLabel("Tiết bắt đầu"))
                header_layout.addWidget(QLabel("Tiết kết thúc"))
                header_layout.addWidget(QLabel(""))  # Cho nút
                header_layout.addWidget(QLabel(""))  # Cho nút
                group_layout.addLayout(header_layout)
                
                # Hiển thị từng lớp
                for lop in classes_by_type[loai_lop]:
                    # Hiển thị từng khung giờ của lớp
                    for idx, gio in enumerate(lop.cac_khung_gio):
                        class_widget = self._create_class_widget(lop, gio, idx == 0)
                        group_layout.addWidget(class_widget)
                
                self.scroll_layout.addWidget(group)
    
    def handle_add_class(self):
        """Xử lý thêm lớp học mới"""
        dialog = ClassDialog(self.all_courses, fixed_mon_hoc=self.mon_hoc, parent=self)
        if dialog.exec():
            data = dialog.get_data()
            if data:
                from ..data_handler import save_data
                new_lop = LopHoc(
                    data['ma_lop'], 
                    data['ten_gv'], 
                    self.mon_hoc.ma_mon, 
                    self.mon_hoc.ten_mon,
                    loai_lop=data.get('loai_lop', 'Lớp')
                )
                new_lop.them_khung_gio(data['thu'], data['tiet_bd'], data['tiet_kt'])
                self.mon_hoc.them_lop_hoc(new_lop)
                save_data(self.all_courses)
                # Refresh lại danh sách
                self._populate_classes()
                QMessageBox.information(self, "Thành công", f"Đã thêm lớp {data['ma_lop']} cho môn {self.mon_hoc.ma_mon}")
            else:
                QMessageBox.warning(self, "Lỗi", 
                                  "Vui lòng điền đủ thông tin và đảm bảo tiết bắt đầu <= tiết kết thúc.")

