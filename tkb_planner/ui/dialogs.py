"""
Các dialog dùng để nhập liệu
"""

from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDialogButtonBox,
    QComboBox, QSpinBox, QVBoxLayout, QListWidget, QPushButton,
    QLabel, QHBoxLayout, QMessageBox, QScrollArea, QWidget, QGroupBox,
    QListWidgetItem, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QBrush, QColor

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
    
    def __init__(self, all_courses, default_thu=None, default_tiet=None, fixed_mon_hoc=None, lop_hoc_hien_tai=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sửa Lớp học" if lop_hoc_hien_tai else "Thêm Lớp học mới")
        self.all_courses = all_courses
        self.lop_hoc_hien_tai = lop_hoc_hien_tai
        self.layout = QFormLayout(self)
        
        # Lưu font gốc của dialog để đảm bảo font size không bị thay đổi
        self.original_dialog_font = self.font()
        # Đảm bảo font size tối thiểu là 10
        if self.original_dialog_font.pointSize() < 10 or self.original_dialog_font.pointSize() == -1:
            self.original_dialog_font.setPointSize(10)
        
        self.mon_hoc_combo = QComboBox()
        self.mon_hoc_combo.addItems(sorted(all_courses.keys()))
        # Nếu có fixed_mon_hoc, set và disable combo box
        self.fixed_mon_hoc = fixed_mon_hoc
        if fixed_mon_hoc:
            self.mon_hoc_combo.setCurrentText(fixed_mon_hoc.ma_mon)
            self.mon_hoc_combo.setEnabled(False)
        else:
            # Kết nối signal để cập nhật danh sách lớp ràng buộc khi thay đổi môn học
            self.mon_hoc_combo.currentTextChanged.connect(self._populate_rang_buoc_list)
        
        self.ma_lop_edit = QLineEdit()
        self.ten_gv_edit = QLineEdit()
        # Combo box để chọn loại lớp
        self.loai_lop_combo = QComboBox()
        self.loai_lop_combo.addItems(["Lý thuyết", "Bài tập", "Lớp"])
        # Kết nối signal để cập nhật danh sách lớp ràng buộc khi thay đổi loại lớp
        self.loai_lop_combo.currentTextChanged.connect(self._populate_rang_buoc_list)
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
        
        # List widget để chọn lớp ràng buộc
        rang_buoc_label = QLabel("Lớp ràng buộc (click vào lớp để chọn/bỏ chọn - nền xám = đã chọn):")
        self.rang_buoc_list = QListWidget()
        # Dùng NoSelection để tự quản lý selection thông qua background color
        # Điều này tránh việc MultiSelection tự động chọn nhiều item cùng lúc
        self.rang_buoc_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        # Thêm padding cho list widget items
        self.rang_buoc_list.setStyleSheet("QListWidget::item { padding: 5px; }")
        # Kết nối signal để toggle selection và highlight khi click
        self.rang_buoc_list.itemClicked.connect(self._on_rang_buoc_item_clicked)
        
        # Nếu đang sửa lớp, set loại lớp trước khi populate list
        if lop_hoc_hien_tai:
            loai_lop = getattr(lop_hoc_hien_tai, 'loai_lop', 'Lớp')
            self.loai_lop_combo.setCurrentText(loai_lop)
        
        # Populate list sau khi đã set tất cả thông tin
        self._populate_rang_buoc_list()
        self.layout.addRow(rang_buoc_label)
        self.layout.addRow(self.rang_buoc_list)
        
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)
    
    def _populate_rang_buoc_list(self):
        """Điền danh sách các lớp có thể ràng buộc (chỉ hiển thị các lớp của cùng môn học, khác giờ).
        Các lớp đã có trong danh sách ràng buộc sẽ luôn được hiển thị, ngay cả khi trùng giờ."""
        from ..scheduler import check_trung_lich
        
        # Lưu lại danh sách các lớp đã chọn trước khi clear (dùng UserRole + 1)
        # CHỈ lấy những lớp thực sự được chọn (is_selected = True)
        selected_lop_ids = set()
        for i in range(self.rang_buoc_list.count()):
            item = self.rang_buoc_list.item(i)
            is_selected = item.data(Qt.ItemDataRole.UserRole + 1)
            # CHỈ thêm vào nếu is_selected là True (không phải None hoặc False)
            if is_selected is True:
                lop_id = item.data(Qt.ItemDataRole.UserRole)
                if lop_id:
                    selected_lop_ids.add(lop_id)
        
        self.rang_buoc_list.clear()
        lop_hien_tai_id = None
        loai_lop_hien_tai = None
        lop_hien_tai = None
        
        # Ưu tiên lấy từ lop_hoc_hien_tai nếu có (khi sửa)
        if self.lop_hoc_hien_tai:
            lop_hien_tai = self.lop_hoc_hien_tai
            lop_hien_tai_id = lop_hien_tai.get_id()
            loai_lop_hien_tai = getattr(lop_hien_tai, 'loai_lop', 'Lớp')
        else:
            # Nếu đang thêm mới, lấy loại lớp từ combo box
            loai_lop_hien_tai = self.loai_lop_combo.currentText()
        
        # Tìm tất cả các lớp ràng buộc 2 chiều (cả lớp ràng buộc trực tiếp và lớp ràng buộc ngược lại)
        # Sử dụng set các object reference để đảm bảo chỉ lưu lớp cụ thể, không phải tất cả lớp cùng ID
        from ..scheduler import _find_lop_by_id_helper
        lop_rang_buoc_objects = set()
        if self.lop_hoc_hien_tai:
            # Lấy các lớp ràng buộc trực tiếp (lớp hiện tại ràng buộc với các lớp này)
            if self.lop_hoc_hien_tai.lop_rang_buoc:
                # Tìm các lớp object cụ thể từ ID (sử dụng helper để hỗ trợ cả format cũ và mới)
                for rang_buoc_id in self.lop_hoc_hien_tai.lop_rang_buoc:
                    lop_rang_buoc = _find_lop_by_id_helper(rang_buoc_id, self.all_courses)
                    if lop_rang_buoc:
                        lop_rang_buoc_objects.add(lop_rang_buoc)
            
            # Thêm logic ràng buộc 2 chiều: nếu lớp hiện tại được ràng buộc bởi lớp khác,
            # thì lớp đó cũng phải được hiển thị trong list
            current_lop_id = self.lop_hoc_hien_tai.get_id()
            # Tìm tất cả các lớp có ràng buộc với lớp hiện tại (chỉ lấy lớp cụ thể)
            for mon_hoc in self.all_courses.values():
                for lop in mon_hoc.cac_lop_hoc:
                    if lop.lop_rang_buoc and current_lop_id in lop.lop_rang_buoc:
                        # Lớp này ràng buộc với lớp hiện tại, thêm object cụ thể vào danh sách
                        lop_rang_buoc_objects.add(lop)
        
        # Lấy môn học hiện tại
        if self.fixed_mon_hoc:
            ma_mon_hien_tai = self.fixed_mon_hoc.ma_mon
        else:
            ma_mon_hien_tai = self.mon_hoc_combo.currentText()
        
        # Chỉ hiển thị các lớp của môn học hiện tại
        if ma_mon_hien_tai and ma_mon_hien_tai in self.all_courses:
            mon_hoc = self.all_courses[ma_mon_hien_tai]
            for lop in mon_hoc.cac_lop_hoc:
                # Loại trừ lớp hiện tại (không thể ràng buộc với chính nó)
                # So sánh bằng object reference để đảm bảo chỉ loại bỏ chính xác lớp đang sửa
                if lop_hien_tai and lop is lop_hien_tai:
                    continue
                
                lop_id = lop.get_id()
                # Kiểm tra xem lớp này có phải là lớp ràng buộc 2 chiều không (so sánh bằng object reference)
                is_rang_buoc_2_chieu = lop in lop_rang_buoc_objects
                
                # Nếu lớp này là lớp ràng buộc 2 chiều, luôn hiển thị (bỏ qua tất cả filter)
                if not is_rang_buoc_2_chieu:
                    # Nếu lớp hiện tại là "Lý thuyết" hoặc "Bài tập", chỉ hiển thị các lớp "Lý thuyết" và "Bài tập"
                    # Nếu lớp hiện tại là "Lớp", hiển thị tất cả các lớp khác
                    if loai_lop_hien_tai in ["Lý thuyết", "Bài tập"]:
                        # Chỉ hiển thị lớp "Lý thuyết" và "Bài tập", không hiển thị "Lớp"
                        if lop.loai_lop not in ["Lý thuyết", "Bài tập"]:
                            continue
                    # Nếu loại lớp hiện tại là "Lớp", hiển thị tất cả (không cần filter)
                    
                    # Kiểm tra trùng giờ: chỉ hiển thị các lớp không trùng giờ với lớp hiện tại
                    # Tuy nhiên, nếu lớp đó đã được chọn, vẫn hiển thị
                    # Chỉ kiểm tra khi đang sửa lớp (có lop_hien_tai)
                    if lop_hien_tai:
                        # Kiểm tra xem lớp này có trong danh sách đã chọn không
                        is_in_selected = lop_id in selected_lop_ids
                        
                        # Nếu trùng giờ và không phải là lớp ràng buộc/đã chọn, bỏ qua
                        if check_trung_lich(lop_hien_tai, lop) and not is_in_selected:
                            continue  # Bỏ qua lớp trùng giờ (trừ khi đã được chọn)
                
                # Tạo chuỗi hiển thị thứ và giờ học
                gio_hoc_str = ""
                if lop.cac_khung_gio:
                    gio_list = []
                    for gio in lop.cac_khung_gio:
                        ten_thu = TEN_THU_TRONG_TUAN.get(gio.thu, f"Thứ {gio.thu}")
                        gio_list.append(f"{ten_thu} Tiết {gio.tiet_bat_dau}-{gio.tiet_ket_thuc}")
                    gio_hoc_str = " | ".join(gio_list)
                
                item_text = f"{lop.ma_lop} - {lop.ten_giao_vien} [{lop.loai_lop}] - {gio_hoc_str}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, lop.get_id())  # Lưu ID của lớp
                # Đảm bảo font size không bị nhỏ hơn - dùng font gốc của dialog
                # Tạo font mới từ font gốc của dialog để đảm bảo font size không bị thay đổi
                item_font = QFont(self.original_dialog_font)
                # Đảm bảo font size tối thiểu là 10, nhưng giữ nguyên nếu lớn hơn
                if item_font.pointSize() < 10 or item_font.pointSize() == -1:
                    item_font.setPointSize(10)
                item.setFont(item_font)
                # Lưu font size gốc vào data để có thể khôi phục sau
                item.setData(Qt.ItemDataRole.UserRole + 2, item_font.pointSize())
                self.rang_buoc_list.addItem(item)
        
        # Lấy danh sách tất cả các lop_id có trong list mới (sau khi populate)
        available_lop_ids = set()
        # Tạo mapping từ ID sang object để kiểm tra chính xác
        available_lop_objects = {}  # {lop_id: [list of lop objects]}
        for i in range(self.rang_buoc_list.count()):
            item = self.rang_buoc_list.item(i)
            lop_id = item.data(Qt.ItemDataRole.UserRole)
            if lop_id:
                available_lop_ids.add(lop_id)
                # Tìm object tương ứng với ID này
                if ma_mon_hien_tai and ma_mon_hien_tai in self.all_courses:
                    mon_hoc = self.all_courses[ma_mon_hien_tai]
                    for lop in mon_hoc.cac_lop_hoc:
                        if lop.get_id() == lop_id:
                            if lop_id not in available_lop_objects:
                                available_lop_objects[lop_id] = []
                            available_lop_objects[lop_id].append(lop)
        
        # Tìm các ID của các lớp ràng buộc 2 chiều có trong list hiện tại
        lop_rang_buoc_ids_in_list = set()
        for lop in lop_rang_buoc_objects:
            lop_id = lop.get_id()
            # Kiểm tra xem lớp này có trong list hiện tại không (so sánh object reference)
            if lop_id in available_lop_objects:
                for available_lop in available_lop_objects[lop_id]:
                    if available_lop is lop:  # So sánh object reference
                        lop_rang_buoc_ids_in_list.add(lop_id)
                        break
        
        # Xử lý việc chọn các lớp ràng buộc
        if not selected_lop_ids:
            # Lần đầu populate: Tự động chọn các lớp ràng buộc 2 chiều
            # Điều này đảm bảo khi mở dialog sửa, các lớp ràng buộc đã được chọn sẵn
            final_selected_ids = lop_rang_buoc_ids_in_list
        else:
            # Lần populate lại: Giữ lại những lớp đã được chọn trước đó VÀ có trong list mới
            # Điều này đảm bảo không chọn những lớp không còn trong list
            selected_lop_ids = selected_lop_ids.intersection(available_lop_ids)
            # Đảm bảo các lớp ràng buộc 2 chiều luôn được chọn
            final_selected_ids = selected_lop_ids.union(lop_rang_buoc_ids_in_list)
        
        # Gán lại để dùng ở dưới
        selected_lop_ids = final_selected_ids
        
        # Đánh dấu các lớp đã chọn (dùng UserRole + 1 để lưu trạng thái selected)
        for i in range(self.rang_buoc_list.count()):
            item = self.rang_buoc_list.item(i)
            lop_id = item.data(Qt.ItemDataRole.UserRole)
            is_selected = lop_id in selected_lop_ids
            item.setData(Qt.ItemDataRole.UserRole + 1, is_selected)
            # Cập nhật highlight
            self._update_item_highlight(item, is_selected)
    
    def _on_rang_buoc_item_clicked(self, item):
        """Xử lý khi click vào item trong danh sách ràng buộc"""
        # Lấy trạng thái hiện tại từ data (không dùng setSelected vì đã tắt selection mode)
        is_selected = item.data(Qt.ItemDataRole.UserRole + 1)  # Dùng UserRole + 1 để lưu trạng thái selected
        if is_selected is None:
            is_selected = False
        
        # Toggle trạng thái
        is_selected = not is_selected
        item.setData(Qt.ItemDataRole.UserRole + 1, is_selected)
        
        # Cập nhật highlight cho item này
        self._update_item_highlight(item, is_selected)
    
    def _update_item_highlight(self, item, is_selected):
        """Cập nhật highlight cho một item cụ thể"""
        # Lấy font size gốc đã lưu, hoặc lấy từ font hiện tại
        original_font_size = item.data(Qt.ItemDataRole.UserRole + 2)
        if original_font_size is None or original_font_size < 10:
            # Nếu chưa có font size gốc, lấy từ font hiện tại hoặc dùng font gốc của dialog
            current_font = item.font()
            font_size = current_font.pointSize()
            if font_size < 10 or font_size == -1:
                original_font_size = self.original_dialog_font.pointSize()
                if original_font_size < 10:
                    original_font_size = 10
            else:
                original_font_size = font_size
            # Lưu lại font size gốc
            item.setData(Qt.ItemDataRole.UserRole + 2, original_font_size)
        
        # Tạo font mới với font size gốc
        preserved_font = QFont(self.original_dialog_font)
        preserved_font.setPointSize(original_font_size)
        
        if is_selected:
            # Highlight với nền xám nhạt (mờ hơn, opacity thấp hơn)
            brush = QBrush(QColor(220, 220, 220, 200))  # Màu xám nhạt với độ mờ
            item.setBackground(brush)
            # Đổi màu chữ sang đỏ để dễ nhìn hơn
            item.setForeground(QBrush(QColor(200, 0, 0)))  # Màu đỏ
        else:
            # Bỏ highlight
            item.setBackground(QBrush(Qt.GlobalColor.transparent))
            # Màu chữ trắng khi chưa chọn
            item.setForeground(QBrush(QColor(255, 255, 255)))  # Màu trắng
        
        # Đảm bảo font size không bị thay đổi - set lại font với size gốc sau khi đổi màu
        item.setFont(preserved_font)
    
    def _update_rang_buoc_highlight(self):
        """Cập nhật highlight (nền xám) cho tất cả các item đã chọn"""
        for i in range(self.rang_buoc_list.count()):
            item = self.rang_buoc_list.item(i)
            is_selected = item.data(Qt.ItemDataRole.UserRole + 1)
            if is_selected is None:
                is_selected = False
            self._update_item_highlight(item, is_selected)

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
        
        # Lấy danh sách lớp ràng buộc đã chọn (dùng UserRole + 1 để lấy trạng thái selected)
        # CHỈ lấy những lớp thực sự được chọn (is_selected = True), không phải None hoặc truthy khác
        lop_rang_buoc = []
        for i in range(self.rang_buoc_list.count()):
            item = self.rang_buoc_list.item(i)
            is_selected = item.data(Qt.ItemDataRole.UserRole + 1)
            # CHỈ thêm vào nếu is_selected là True (không phải None hoặc truthy khác)
            if is_selected is True:
                lop_id = item.data(Qt.ItemDataRole.UserRole)
                if lop_id:
                    lop_rang_buoc.append(lop_id)
        
        return {
            'ma_mon': ma_mon, 
            'ma_lop': ma_lop, 
            'ten_gv': ten_gv,
            'loai_lop': loai_lop,
            'thu': thu, 
            'tiet_bd': tiet_bd, 
            'tiet_kt': tiet_kt,
            'lop_rang_buoc': lop_rang_buoc
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


class EditAllSubjectsDialog(QDialog):
    """Dialog để hiển thị và sửa/xóa tất cả môn học"""
    
    def __init__(self, all_courses, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sửa môn học")
        self.setMinimumSize(800, 600)
        self.all_courses = all_courses
        
        layout = QVBoxLayout(self)
        
        # Scroll area để chứa danh sách môn học
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(10)
        
        self._populate_subjects()
        
        scroll.setWidget(self.scroll_widget)
        layout.addWidget(scroll)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close
        )
        buttons.rejected.connect(self.accept)
        layout.addWidget(buttons)
    
    def _populate_subjects(self):
        """Điền danh sách môn học vào scroll area"""
        # Xóa tất cả widget cũ
        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Hiển thị từng môn học
        for ma_mon in sorted(self.all_courses.keys()):
            mon_hoc = self.all_courses[ma_mon]
            group = QGroupBox(f"{mon_hoc.ten_mon} ({ma_mon})")
            group_layout = QVBoxLayout(group)
            
            # Thông tin môn học
            info_layout = QHBoxLayout()
            info_layout.addWidget(QLabel(f"Mã môn: {ma_mon}"))
            info_layout.addWidget(QLabel(f"Tên môn: {mon_hoc.ten_mon}"))
            if mon_hoc.tien_quyet:
                info_layout.addWidget(QLabel(f"Môn tiên quyết: {', '.join(mon_hoc.tien_quyet)}"))
            info_layout.addStretch()
            
            # Nút sửa và xóa
            edit_btn = QPushButton("Sửa")
            edit_btn.setMinimumWidth(80)
            edit_btn.clicked.connect(lambda checked, m=mon_hoc: self.handle_edit_subject(m))
            
            delete_btn = QPushButton("Xóa")
            delete_btn.setMinimumWidth(80)
            delete_btn.clicked.connect(lambda checked, m=ma_mon: self.handle_delete_subject(m))
            
            info_layout.addWidget(edit_btn)
            info_layout.addWidget(delete_btn)
            
            group_layout.addLayout(info_layout)
            
            # Hiển thị số lượng lớp học
            num_classes = len(mon_hoc.cac_lop_hoc)
            classes_label = QLabel(f"Số lớp học: {num_classes}")
            group_layout.addWidget(classes_label)
            
            self.scroll_layout.addWidget(group)
    
    def handle_edit_subject(self, mon_hoc):
        """Xử lý sửa môn học"""
        dialog = SubjectDialog(self, mon_hoc=mon_hoc)
        if dialog.exec():
            data = dialog.get_data()
            if data:
                # Cập nhật thông tin môn học
                mon_hoc.ten_mon = data['ten_mon']
                mon_hoc.tien_quyet = data['tien_quyet']
                # Lưu dữ liệu
                from ..data_handler import save_data
                save_data(self.all_courses)
                # Refresh lại danh sách
                self._populate_subjects()
                QMessageBox.information(self, "Thành công", f"Đã cập nhật môn {mon_hoc.ma_mon}")
    
    def handle_delete_subject(self, ma_mon):
        """Xử lý xóa môn học"""
        mon_hoc = self.all_courses.get(ma_mon)
        if not mon_hoc:
            return
        
        reply = QMessageBox.question(
            self, 'Xác nhận xóa', 
            f"Bạn có chắc muốn xóa môn '{mon_hoc.ten_mon}' ({ma_mon})?\n\nTất cả lớp học của môn này cũng sẽ bị xóa!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            del self.all_courses[ma_mon]
            # Lưu dữ liệu
            from ..data_handler import save_data
            save_data(self.all_courses)
            # Refresh lại danh sách
            self._populate_subjects()
            QMessageBox.information(self, "Thành công", f"Đã xóa môn {ma_mon}")


class EditAllClassesDialog(QDialog):
    """Dialog để hiển thị và sửa/xóa tất cả lớp học (giống area các lớp học)"""
    
    def __init__(self, all_courses, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sửa lớp học")
        self.setMinimumSize(1000, 700)
        self.all_courses = all_courses
        
        layout = QVBoxLayout(self)
        
        # Scroll area để chứa các nhóm lớp
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(10)
        
        self._populate_all_classes()
        
        scroll.setWidget(self.scroll_widget)
        layout.addWidget(scroll)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close
        )
        buttons.rejected.connect(self.accept)
        layout.addWidget(buttons)
    
    def _create_class_widget(self, lop, gio, is_first_row, mon_hoc):
        """Tạo widget hiển thị thông tin một khung giờ của lớp học"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 0, 0, 0)
        
        # Label mã lớp (chỉ hiển thị ở dòng đầu tiên)
        if is_first_row:
            ma_lop_label = QLabel(lop.ma_lop)
        else:
            ma_lop_label = QLabel("")
        ma_lop_label.setStyleSheet("padding-left: 0px;")
        layout.addWidget(ma_lop_label)
        
        # Label giờ học
        gio_label = QLabel(f"Tiết {gio.tiet_bat_dau}-{gio.tiet_ket_thuc}")
        gio_label.setStyleSheet("padding-left: 0px;")
        layout.addWidget(gio_label)
        
        # Label thứ
        ten_thu = TEN_THU_TRONG_TUAN.get(gio.thu, f"Thứ {gio.thu}")
        thu_label = QLabel(ten_thu)
        thu_label.setStyleSheet("padding-left: 10px;")
        layout.addWidget(thu_label)
        
        # Label tên giáo viên (chỉ hiển thị ở dòng đầu tiên)
        if is_first_row:
            gv_label = QLabel(lop.ten_giao_vien)
        else:
            gv_label = QLabel("")
        gv_label.setStyleSheet("padding-left: 0px;")
        layout.addWidget(gv_label)
        
        # Label môn học (chỉ hiển thị ở dòng đầu tiên)
        if is_first_row:
            mon_label = QLabel(f"{mon_hoc.ten_mon} ({mon_hoc.ma_mon})")
        else:
            mon_label = QLabel("")
        mon_label.setStyleSheet("padding-left: 10px;")
        layout.addWidget(mon_label)
        
        # Nút sửa (chỉ hiển thị ở dòng đầu tiên)
        if is_first_row:
            edit_btn = QPushButton("Sửa")
            edit_btn.setMinimumWidth(60)
            edit_btn.clicked.connect(lambda: self.handle_edit_class(lop, mon_hoc))
            layout.addWidget(edit_btn, 0)
        else:
            layout.addWidget(QLabel(""), 0)
        
        # Nút xóa (chỉ hiển thị ở dòng đầu tiên)
        if is_first_row:
            delete_btn = QPushButton("Xóa")
            delete_btn.setMinimumWidth(60)
            delete_btn.clicked.connect(lambda: self.handle_delete_class(lop, mon_hoc))
            layout.addWidget(delete_btn, 0)
        else:
            layout.addWidget(QLabel(""), 0)
        
        return widget
    
    def handle_edit_class(self, lop, mon_hoc):
        """Xử lý sửa lớp học"""
        # Lấy khung giờ đầu tiên để điền sẵn vào dialog
        default_thu = None
        default_tiet_bd = None
        default_tiet_kt = None
        if lop.cac_khung_gio:
            gio_dau = lop.cac_khung_gio[0]
            default_thu = gio_dau.thu
            default_tiet_bd = gio_dau.tiet_bat_dau
            default_tiet_kt = gio_dau.tiet_ket_thuc
        
        dialog = ClassDialog(
            self.all_courses,
            default_thu=default_thu,
            default_tiet=default_tiet_bd,
            fixed_mon_hoc=mon_hoc,
            lop_hoc_hien_tai=lop,
            parent=self,
        )
        
        # Điền sẵn thông tin lớp hiện tại
        dialog.ma_lop_edit.setText(lop.ma_lop)
        dialog.ten_gv_edit.setText(lop.ten_giao_vien)
        dialog.loai_lop_combo.setCurrentText(getattr(lop, "loai_lop", "Lớp"))
        # Set tiết kết thúc đúng
        if default_tiet_kt:
            dialog.tiet_kt_spin.setValue(default_tiet_kt)
        # Populate lại list sau khi set loại lớp
        dialog._populate_rang_buoc_list()
        
        if dialog.exec():
            data = dialog.get_data()
            if not data:
                QMessageBox.warning(
                    self,
                    "Lỗi",
                    "Vui lòng điền đủ thông tin và đảm bảo tiết bắt đầu <= tiết kết thúc.",
                )
                return
            
            # Tạo lớp tạm để kiểm tra trùng phòng học
            from ..models import LopHoc
            from ..scheduler import kiem_tra_trung_trong_cung_mon, update_bidirectional_constraints
            old_id = lop.get_id()
            old_rang_buoc = list(lop.lop_rang_buoc) if lop.lop_rang_buoc else []
            temp_lop = LopHoc(
                data["ma_lop"],
                data["ten_gv"],
                mon_hoc.ma_mon,
                mon_hoc.ten_mon,
                loai_lop=data.get("loai_lop", lop.loai_lop),
                lop_rang_buoc=data.get("lop_rang_buoc", lop.lop_rang_buoc)
            )
            temp_lop.them_khung_gio(data["thu"], data["tiet_bd"], data["tiet_kt"])
            
            # Kiểm tra trùng trong cùng môn (loại trừ lớp hiện tại)
            is_valid, error_msg = kiem_tra_trung_trong_cung_mon(temp_lop, mon_hoc, exclude_lop_id=old_id)
            if not is_valid:
                QMessageBox.warning(self, "Lỗi", error_msg)
                return
            
            # Cập nhật thông tin lớp hiện tại
            lop.ma_lop = data["ma_lop"]
            lop.ten_giao_vien = data["ten_gv"]
            lop.loai_lop = data.get("loai_lop", lop.loai_lop)
            lop.lop_rang_buoc = data.get("lop_rang_buoc", [])
            # Cập nhật lại khung giờ
            lop.cac_khung_gio.clear()
            lop.them_khung_gio(data["thu"], data["tiet_bd"], data["tiet_kt"])
            
            # Nếu mã lớp thay đổi, cần cập nhật lại dict của môn học
            new_id = lop.get_id()
            if old_id != new_id:
                if old_id in mon_hoc.cac_lop_hoc_dict:
                    del mon_hoc.cac_lop_hoc_dict[old_id]
                mon_hoc.cac_lop_hoc_dict[new_id] = lop
            
            # Cập nhật ràng buộc 2 chiều
            new_rang_buoc = data.get("lop_rang_buoc", [])
            update_bidirectional_constraints(old_id, old_rang_buoc, new_id, new_rang_buoc, self.all_courses)
            
            # Lưu và refresh lại giao diện
            from ..data_handler import save_data
            save_data(self.all_courses)
            self._populate_all_classes()
            QMessageBox.information(self, "Thành công", f"Đã cập nhật lớp {lop.ma_lop}")
    
    def handle_delete_class(self, lop, mon_hoc):
        """Xử lý xóa lớp học"""
        reply = QMessageBox.question(
            self, 'Xác nhận xóa', 
            f"Bạn có chắc muốn xóa lớp '{lop.ma_lop}' của môn '{mon_hoc.ten_mon}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            # Xóa ràng buộc 2 chiều trước khi xóa lớp
            from ..scheduler import remove_bidirectional_constraints
            lop_id = lop.get_id()
            remove_bidirectional_constraints(lop_id, self.all_courses)
            
            # Xóa khỏi danh sách lớp của môn học
            if lop in mon_hoc.cac_lop_hoc:
                mon_hoc.cac_lop_hoc.remove(lop)
            # Xóa khỏi dict nếu có
            if lop_id in mon_hoc.cac_lop_hoc_dict:
                del mon_hoc.cac_lop_hoc_dict[lop_id]
            
            # Lưu và refresh lại danh sách lớp
            from ..data_handler import save_data
            save_data(self.all_courses)
            self._populate_all_classes()
            QMessageBox.information(self, "Thành công", f"Đã xóa lớp {lop.ma_lop}")
    
    def _populate_all_classes(self):
        """Điền danh sách tất cả lớp học vào scroll area"""
        # Xóa tất cả widget cũ
        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Hiển thị theo từng môn học
        for ma_mon in sorted(self.all_courses.keys()):
            mon_hoc = self.all_courses[ma_mon]
            if not mon_hoc.cac_lop_hoc:
                continue
            
            # Group box cho mỗi môn học
            mon_group = QGroupBox(f"{mon_hoc.ten_mon} ({ma_mon})")
            mon_layout = QVBoxLayout(mon_group)
            
            # Phân loại các lớp theo loại
            classes_by_type = {
                "Lý thuyết": [],
                "Bài tập": [],
                "Lớp": []
            }
            
            for lop in mon_hoc.cac_lop_hoc:
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
                    header_layout.setSpacing(20)
                    header_layout.setContentsMargins(8, 0, 0, 0)
                    header_layout.addWidget(QLabel("Phòng học"))
                    header_layout.addWidget(QLabel("Giờ học"))
                    header_layout.addWidget(QLabel("Thứ"))
                    header_layout.addWidget(QLabel("GV"))
                    header_layout.addWidget(QLabel("Môn học"))
                    header_layout.addWidget(QLabel(""))  # Cho nút
                    header_layout.addWidget(QLabel(""))  # Cho nút
                    group_layout.addLayout(header_layout)
                    
                    # Hiển thị từng lớp
                    for lop in classes_by_type[loai_lop]:
                        # Hiển thị từng khung giờ của lớp
                        for idx, gio in enumerate(lop.cac_khung_gio):
                            class_widget = self._create_class_widget(lop, gio, idx == 0, mon_hoc)
                            group_layout.addWidget(class_widget)
                    
                    mon_layout.addWidget(group)
            
            self.scroll_layout.addWidget(mon_group)
