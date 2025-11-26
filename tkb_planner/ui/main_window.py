"""
Main window của ứng dụng TKB Planner Pro
"""

import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QCheckBox, QScrollArea, QFrame,
    QTextBrowser, QStatusBar, QFileDialog, QMessageBox,
    QDateEdit, QTimeEdit, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate, QTime, QSettings
from PyQt6.QtGui import QFont, QAction

from ..models import MonHoc, LopHoc, LichBan
from ..scheduler import tim_thoi_khoa_bieu
from ..data_handler import save_data, load_data, create_sample_data_if_not_exists
from ..constants import DATA_FILE, TEN_THU_TRONG_TUAN
from .schedule_widget import ScheduleWidget
from .dialogs import SubjectDialog, ClassDialog
from .theme import LIGHT_THEME, DARK_THEME


class MainWindow(QMainWindow):
    """Cửa sổ chính của ứng dụng"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Công cụ Sắp xếp TKB Pro")
        self.setGeometry(100, 100, 1288, 780)
        self.setFont(QFont("Segoe UI", 10))
        
        # Load settings
        self.settings = QSettings("TKBPlanner", "TKBPlannerPro")
        self.dark_mode = self.settings.value("dark_mode", True, type=bool)  # Mặc định là chế độ tối
        
        create_sample_data_if_not_exists()
        self.all_courses = load_data()
        self.danh_sach_gio_ban = []
        self.danh_sach_tkb_tim_duoc = []
        self.current_tkb_index = -1
        self.course_widgets = {}
        self.busy_time_widgets = {}
        self.toggle_theme_action = None  # Khởi tạo trước
        self._setup_ui()
        self._setup_menu_bar()
        self._populate_course_list()
        self._connect_signals()
        self.apply_theme()  # Áp dụng theme sau khi setup UI
        self.log_message("Chào mừng! Chọn môn học và giờ bận để bắt đầu.")

    def _setup_ui(self):
        """Thiết lập giao diện người dùng"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QHBoxLayout(self.central_widget)
        
        # Panel bên trái
        left_panel = QGroupBox("Bảng điều khiển")
        left_panel_layout = QVBoxLayout(left_panel)
        main_layout.addWidget(left_panel, 1)
        
        # Nhóm chọn môn học
        course_group = QGroupBox("Chọn môn học")
        course_layout = QVBoxLayout(course_group)
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nhập mã hoặc tên môn để lọc...")
        search_layout.addWidget(QLabel("Nhập môn:"))
        search_layout.addWidget(self.search_input)
        course_layout.addLayout(search_layout)
        
        scroll_area_courses = QScrollArea()
        scroll_area_courses.setWidgetResizable(True)
        self.course_list_widget = QWidget()
        self.course_list_layout = QVBoxLayout(self.course_list_widget)
        self.course_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_area_courses.setWidget(self.course_list_widget)
        course_layout.addWidget(scroll_area_courses)
        
        # Nhóm giờ bận
        busy_group = QGroupBox("Giờ bận")
        busy_layout = QVBoxLayout(busy_group)
        busy_input_layout1 = QHBoxLayout()
        self.busy_date_edit = QDateEdit(QDate.currentDate())
        self.busy_date_edit.setCalendarPopup(True)
        self.busy_reason_input = QLineEdit()
        busy_input_layout1.addWidget(QLabel("Ngày:"))
        busy_input_layout1.addWidget(self.busy_date_edit)
        busy_input_layout1.addWidget(QLabel("Lí do:"))
        busy_input_layout1.addWidget(self.busy_reason_input)
        
        busy_input_layout2 = QHBoxLayout()
        self.busy_start_time = QTimeEdit(QTime(7, 0))
        self.busy_end_time = QTimeEdit(QTime(8, 0))
        self.add_busy_btn = QPushButton("Thêm")
        busy_input_layout2.addWidget(QLabel("Bắt đầu:"))
        busy_input_layout2.addWidget(self.busy_start_time)
        busy_input_layout2.addWidget(QLabel("Kết thúc:"))
        busy_input_layout2.addWidget(self.busy_end_time)
        busy_input_layout2.addWidget(self.add_busy_btn)
        busy_layout.addLayout(busy_input_layout1)
        busy_layout.addLayout(busy_input_layout2)
        
        scroll_area_busy = QScrollArea()
        scroll_area_busy.setWidgetResizable(True)
        self.busy_list_widget = QWidget()
        self.busy_list_layout = QVBoxLayout(self.busy_list_widget)
        self.busy_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_area_busy.setWidget(self.busy_list_widget)
        busy_layout.addWidget(scroll_area_busy)
        
        # Nhóm thông báo
        notification_group = QGroupBox("Thông báo")
        notification_layout = QVBoxLayout(notification_group)
        self.notification_browser = QTextBrowser()
        notification_layout.addWidget(self.notification_browser)
        
        left_panel_layout.addWidget(course_group, 3)
        left_panel_layout.addWidget(busy_group, 2)
        left_panel_layout.addWidget(notification_group, 1)
        
        # Panel bên phải
        right_panel = QGroupBox("Lịch Tuần")
        right_panel_layout = QVBoxLayout(right_panel)
        main_layout.addWidget(right_panel, 2)
        self.schedule_view = ScheduleWidget()
        right_panel_layout.addWidget(self.schedule_view)
        
        # Các nút điều khiển
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.find_tkb_btn = QPushButton("Tìm TKB hợp lệ")
        self.prev_tkb_btn = QPushButton("< TKB Trước")
        self.next_tkb_btn = QPushButton("TKB Tiếp >")
        self.add_subject_btn = QPushButton("Thêm Môn")
        self.save_tkb_btn = QPushButton("Lưu TKB")
        self.clear_tkb_btn = QPushButton("Xoá TKB")

        button_height = 30
        self.find_tkb_btn.setMinimumHeight(button_height)
        self.prev_tkb_btn.setMinimumHeight(button_height)
        self.next_tkb_btn.setMinimumHeight(button_height)
        self.add_subject_btn.setMinimumHeight(button_height)
        self.save_tkb_btn.setMinimumHeight(button_height)
        self.clear_tkb_btn.setMinimumHeight(button_height)

        button_layout.addWidget(self.find_tkb_btn)
        button_layout.addWidget(self.prev_tkb_btn)
        button_layout.addWidget(self.next_tkb_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.add_subject_btn)
        button_layout.addWidget(self.save_tkb_btn)
        button_layout.addWidget(self.clear_tkb_btn)
        right_panel_layout.addLayout(button_layout)
        
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Sẵn sàng")

    def _setup_menu_bar(self):
        """Thiết lập thanh menu"""
        menu_bar = self.menuBar()
        
        # Menu File
        file_menu = menu_bar.addMenu("&File")
        save_action = QAction("Lưu dữ liệu môn học", self)
        save_action.triggered.connect(self.handle_save_data)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        exit_action = QAction("Thoát", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Edit
        edit_menu = menu_bar.addMenu("&Edit")
        add_subject_action = QAction("Thêm Môn học", self)
        add_subject_action.triggered.connect(self.handle_add_subject)
        edit_menu.addAction(add_subject_action)
        add_class_action = QAction("Thêm Lớp học", self)
        add_class_action.triggered.connect(lambda: self.handle_add_class_dialog())
        edit_menu.addAction(add_class_action)
        
        # Menu View
        view_menu = menu_bar.addMenu("&View")
        select_all_action = QAction("Chọn tất cả các môn", self)
        select_all_action.triggered.connect(lambda: self.handle_select_all(True))
        view_menu.addAction(select_all_action)
        deselect_all_action = QAction("Bỏ chọn tất cả", self)
        deselect_all_action.triggered.connect(lambda: self.handle_select_all(False))
        view_menu.addAction(deselect_all_action)
        view_menu.addSeparator()
        # Menu chuyển đổi theme
        self.toggle_theme_action = QAction("Chế độ tối", self)
        self.toggle_theme_action.setCheckable(True)
        self.toggle_theme_action.setChecked(self.dark_mode)
        self.toggle_theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(self.toggle_theme_action)
        
        # Menu TKB
        tkb_menu = menu_bar.addMenu("&TKB")
        tkb_menu.addAction(self.find_tkb_btn.text(), self.handle_find_tkb)
        tkb_menu.addAction(self.next_tkb_btn.text(), self.show_next_tkb)
        tkb_menu.addAction(self.prev_tkb_btn.text(), self.show_prev_tkb)
        tkb_menu.addSeparator()
        tkb_menu.addAction(self.clear_tkb_btn.text(), self.handle_clear_tkb)
        
        # Menu Help
        help_menu = menu_bar.addMenu("&Help")
        about_action = QAction("Giới thiệu", self)
        about_action.triggered.connect(self.handle_about)
        help_menu.addAction(about_action)
        
    def _populate_course_list(self):
        """Điền danh sách môn học vào UI"""
        for widget in self.course_widgets.values():
            widget['container'].deleteLater()
        self.course_widgets.clear()
        sorted_courses = sorted(self.all_courses.values(), key=lambda m: m.ma_mon)
        for mon_hoc in sorted_courses:
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(5, 3, 5, 3)  # Thêm margin để tránh bị che
            layout.setSpacing(5)  # Thêm khoảng cách giữa các widget
            
            check = QCheckBox(f"{mon_hoc.ten_mon} ({mon_hoc.ma_mon})")
            check.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            mandatory_check = QCheckBox("Bắt buộc")
            mandatory_check.setToolTip("TKB tìm được phải chứa môn này")
            mandatory_check.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
            
            edit_btn = QPushButton("Sửa")
            edit_btn.setMinimumWidth(55)  # Thay vì setFixedWidth để có thể co giãn
            edit_btn.setMaximumWidth(70)
            edit_btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
            
            delete_btn = QPushButton("Xoá")
            delete_btn.setMinimumWidth(55)
            delete_btn.setMaximumWidth(70)
            delete_btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
            
            layout.addWidget(check, 1)  # Checkbox chiếm không gian còn lại
            layout.addWidget(mandatory_check, 0)  # Checkbox bắt buộc không co giãn
            layout.addWidget(edit_btn, 0)  # Nút Sửa không co giãn
            layout.addWidget(delete_btn, 0)  # Nút Xoá không co giãn
            
            self.course_list_layout.addWidget(container)
            self.course_widgets[mon_hoc.ma_mon] = {
                'container': container,
                'check': check,
                'mandatory': mandatory_check,
                'edit_btn': edit_btn,
                'delete_btn': delete_btn
            }
            edit_btn.clicked.connect(lambda _, m=mon_hoc.ma_mon: self.handle_edit_subject(m))
            delete_btn.clicked.connect(lambda _, m=mon_hoc.ma_mon: self.handle_delete_course(m))

    def _connect_signals(self):
        """Kết nối các signal và slot"""
        self.add_busy_btn.clicked.connect(self.handle_add_busy_time)
        self.find_tkb_btn.clicked.connect(self.handle_find_tkb)
        self.prev_tkb_btn.clicked.connect(self.show_prev_tkb)
        self.next_tkb_btn.clicked.connect(self.show_next_tkb)
        self.clear_tkb_btn.clicked.connect(self.handle_clear_tkb)
        self.save_tkb_btn.clicked.connect(self.handle_save_tkb)
        self.add_subject_btn.clicked.connect(self.handle_add_subject)
        self.search_input.textChanged.connect(self.filter_course_list)
        self.schedule_view.cellClicked.connect(self.handle_cell_click)

    def handle_add_subject(self):
        """Xử lý thêm môn học mới"""
        dialog = SubjectDialog(self, mon_hoc=None)
        if dialog.exec():
            data = dialog.get_data()
            if data and data['ma_mon'] not in self.all_courses:
                new_mon = MonHoc(data['ma_mon'], data['ten_mon'], data['tien_quyet'])
                self.all_courses[data['ma_mon']] = new_mon
                self._populate_course_list()
                save_data(self.all_courses)
                self.log_message(f"Đã thêm môn học mới: {data['ma_mon']}")
            elif not data:
                QMessageBox.warning(self, "Lỗi", "Mã môn và Tên môn không được để trống.")
            else:
                QMessageBox.warning(self, "Lỗi", f"Mã môn '{data['ma_mon']}' đã tồn tại.")

    def handle_edit_subject(self, ma_mon):
        """Xử lý sửa môn học"""
        mon_hoc = self.all_courses.get(ma_mon)
        if not mon_hoc:
            return
        dialog = SubjectDialog(self, mon_hoc=mon_hoc)
        if dialog.exec():
            data = dialog.get_data()
            if data:
                mon_hoc.ten_mon = data['ten_mon']
                mon_hoc.tien_quyet = data['tien_quyet']
                save_data(self.all_courses)
                self._populate_course_list()
                self.log_message(f"Đã cập nhật môn học: {ma_mon}")
            else:
                QMessageBox.warning(self, "Lỗi", "Tên môn không được để trống.")

    def handle_add_class_dialog(self, default_thu=None, default_tiet=None):
        """Xử lý thêm lớp học mới"""
        if not self.all_courses:
            QMessageBox.warning(self, "Chưa có môn học", 
                              "Vui lòng thêm một môn học trước khi thêm lớp.")
            return
        dialog = ClassDialog(self.all_courses, default_thu, default_tiet, self)
        if dialog.exec():
            data = dialog.get_data()
            if data:
                mon_hoc = self.all_courses[data['ma_mon']]
                new_lop = LopHoc(data['ma_lop'], data['ten_gv'], 
                               mon_hoc.ma_mon, mon_hoc.ten_mon)
                new_lop.them_khung_gio(data['thu'], data['tiet_bd'], data['tiet_kt'])
                mon_hoc.them_lop_hoc(new_lop)
                save_data(self.all_courses)
                self.log_message(f"Đã thêm lớp {data['ma_lop']} cho môn {data['ma_mon']}")
            else:
                QMessageBox.warning(self, "Lỗi", 
                                  "Vui lòng điền đủ thông tin và đảm bảo tiết bắt đầu <= tiết kết thúc.")

    def handle_cell_click(self, thu, tiet):
        """Xử lý khi click vào ô lịch"""
        self.log_message(f"Chọn thêm lớp mới vào Thứ {thu}, Tiết {tiet}...")
        self.handle_add_class_dialog(default_thu=thu, default_tiet=tiet)

    def handle_save_data(self):
        """Xử lý lưu dữ liệu"""
        if save_data(self.all_courses):
            self.log_message("Lưu dữ liệu môn học thành công!")
            QMessageBox.information(self, "Thành công", 
                                  f"Đã lưu dữ liệu vào file {DATA_FILE}")

    def handle_select_all(self, state):
        """Chọn/bỏ chọn tất cả môn học"""
        for widgets in self.course_widgets.values():
            widgets['check'].setChecked(state)

    def handle_about(self):
        """Hiển thị thông tin về ứng dụng"""
        QMessageBox.about(self, "Giới thiệu", 
                        "Công cụ Sắp xếp TKB Pro\n\n"
                        "Phiên bản 3.0\n"
                        "Phát triển bởi bạn và Gemini.")
    
    def handle_delete_course(self, ma_mon):
        """Xử lý xóa môn học"""
        mon_hoc = self.all_courses.get(ma_mon)
        if not mon_hoc:
            return
        reply = QMessageBox.question(
            self, 'Xác nhận xoá', 
            f"Bạn có chắc muốn xoá môn '{mon_hoc.ten_mon}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            del self.all_courses[ma_mon]
            self._populate_course_list()
            save_data(self.all_courses)
            self.log_message(f"Đã xoá môn {ma_mon}.")

    def filter_course_list(self):
        """Lọc danh sách môn học theo từ khóa"""
        filter_text = self.search_input.text().lower()
        for ma_mon, widgets in self.course_widgets.items():
            mon_hoc = self.all_courses[ma_mon]
            text_to_check = f"{mon_hoc.ten_mon} ({mon_hoc.ma_mon})".lower()
            widgets['container'].setVisible(filter_text in text_to_check)
            
    def handle_add_busy_time(self):
        """Xử lý thêm giờ bận"""
        date = self.busy_date_edit.date()
        start_time = self.busy_start_time.time()
        end_time = self.busy_end_time.time()
        reason = self.busy_reason_input.text() or "Bận"
        if start_time >= end_time:
            self.log_message("Lỗi: Giờ bắt đầu phải trước giờ kết thúc.")
            return
        
        thu = date.dayOfWeek() + 1  # Monday=1 -> 2, Sunday=7 -> 8
        busy_id = datetime.datetime.now().timestamp()
        new_busy_time = LichBan(thu, start_time, end_time, reason, busy_id)
        self.danh_sach_gio_ban.append(new_busy_time)
        
        container = QFrame()
        container.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(5, 3, 5, 3)  # Thêm margin để tránh bị che
        layout.setSpacing(5)  # Thêm khoảng cách giữa các widget
        
        check = QCheckBox(str(new_busy_time))
        check.setChecked(True)
        check.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        delete_btn = QPushButton("Xoá")
        delete_btn.setMinimumWidth(55)  # Thay vì setFixedWidth
        delete_btn.setMaximumWidth(70)
        delete_btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        
        layout.addWidget(check, 1)  # Checkbox chiếm không gian còn lại
        layout.addWidget(delete_btn, 0)  # Nút Xoá không co giãn
        delete_btn.clicked.connect(lambda: self.handle_delete_busy_time(busy_id))
        self.busy_list_layout.addWidget(container)
        self.busy_time_widgets[busy_id] = container
        self.log_message(f"Đã thêm giờ bận: {new_busy_time}")

    def handle_delete_busy_time(self, busy_id):
        """Xử lý xóa giờ bận"""
        self.danh_sach_gio_ban = [b for b in self.danh_sach_gio_ban if b.id != busy_id]
        if busy_id in self.busy_time_widgets:
            self.busy_time_widgets[busy_id].deleteLater()
            del self.busy_time_widgets[busy_id]
        self.log_message("Đã xoá một giờ bận.")

    def handle_find_tkb(self):
        """Tìm kiếm thời khóa biểu hợp lệ"""
        from PyQt6.QtWidgets import QApplication
        selected_courses = [
            self.all_courses[ma_mon] 
            for ma_mon, widgets in self.course_widgets.items() 
            if widgets['check'].isChecked()
        ]
        if not selected_courses:
            self.log_message("Vui lòng chọn ít nhất một môn học.")
            return
        mandatory_courses = [
            ma_mon 
            for ma_mon, widgets in self.course_widgets.items() 
            if widgets['check'].isChecked() and widgets['mandatory'].isChecked()
        ]
        active_busy_times = self.danh_sach_gio_ban
        self.log_message("Đang tìm kiếm TKB...")
        QApplication.processEvents()
        self.danh_sach_tkb_tim_duoc, error_msg = tim_thoi_khoa_bieu(
            selected_courses, active_busy_times, mandatory_courses
        )
        if error_msg:
            self.log_message(error_msg)
            self.schedule_view.display_schedule([], self.all_courses)
            self.current_tkb_index = -1
        elif not self.danh_sach_tkb_tim_duoc:
            self.log_message("Không tìm thấy TKB nào phù hợp.")
            self.schedule_view.display_schedule([], self.all_courses)
            self.current_tkb_index = -1
        else:
            self.log_message(f"Tìm thấy {len(self.danh_sach_tkb_tim_duoc)} TKB phù hợp!")
            self.show_tkb_at_index(0)
        self.update_nav_buttons()

    def show_tkb_at_index(self, index):
        """Hiển thị TKB tại vị trí index"""
        if not self.danh_sach_tkb_tim_duoc or not (0 <= index < len(self.danh_sach_tkb_tim_duoc)):
            return
        self.current_tkb_index = index
        tkb = self.danh_sach_tkb_tim_duoc[index]
        self.schedule_view.display_schedule(tkb, self.all_courses)
        self.statusBar().showMessage(f"Đang xem TKB {index + 1} / {len(self.danh_sach_tkb_tim_duoc)}")

    def show_next_tkb(self):
        """Hiển thị TKB tiếp theo"""
        if not self.danh_sach_tkb_tim_duoc:
            return
        new_index = (self.current_tkb_index + 1) % len(self.danh_sach_tkb_tim_duoc)
        self.show_tkb_at_index(new_index)
        
    def show_prev_tkb(self):
        """Hiển thị TKB trước đó"""
        if not self.danh_sach_tkb_tim_duoc:
            return
        new_index = (self.current_tkb_index - 1) % len(self.danh_sach_tkb_tim_duoc)
        self.show_tkb_at_index(new_index)

    def update_nav_buttons(self):
        """Cập nhật trạng thái các nút điều hướng"""
        has_results = len(self.danh_sach_tkb_tim_duoc) > 0
        self.prev_tkb_btn.setEnabled(has_results)
        self.next_tkb_btn.setEnabled(has_results)
        self.save_tkb_btn.setEnabled(has_results)
        self.clear_tkb_btn.setEnabled(has_results)

    def handle_clear_tkb(self):
        """Xóa kết quả tìm kiếm TKB"""
        self.danh_sach_tkb_tim_duoc = []
        self.current_tkb_index = -1
        self.schedule_view.display_schedule([], self.all_courses)
        self.log_message("Đã xoá kết quả tìm kiếm TKB.")
        self.statusBar().showMessage("Sẵn sàng")
        self.update_nav_buttons()

    def handle_save_tkb(self):
        """Lưu TKB hiện tại ra file"""
        if self.current_tkb_index == -1 or not self.danh_sach_tkb_tim_duoc:
            self.log_message("Không có TKB để lưu.")
            return
        tkb_to_save = self.danh_sach_tkb_tim_duoc[self.current_tkb_index]
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Lưu Thời khóa biểu", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"THỜI KHÓA BIỂU SỐ {self.current_tkb_index + 1}\n" + "="*30 + "\n\n")
                    sorted_tkb = sorted(
                        tkb_to_save, 
                        key=lambda lop: (
                            min(g.thu for g in lop.cac_khung_gio), 
                            min(g.tiet_bat_dau for g in lop.cac_khung_gio)
                        )
                    )
                    for lop in sorted_tkb:
                        f.write(f"Môn: {lop.ten_mon} ({lop.ma_mon})\n")
                        f.write(f"  Lớp: {lop.ma_lop}\n")
                        f.write(f"  GV: {lop.ten_giao_vien}\n")
                        for gio in lop.cac_khung_gio:
                            ten_thu = TEN_THU_TRONG_TUAN.get(gio.thu, "Không rõ")
                            f.write(f"  Thời gian: {ten_thu}, Tiết {gio.tiet_bat_dau}-{gio.tiet_ket_thuc}\n")
                        f.write("\n")
                self.log_message(f"Đã lưu TKB thành công vào: {file_path}")
            except Exception as e:
                self.log_message(f"Lỗi khi lưu TKB: {e}")

    def log_message(self, message):
        """Ghi log vào notification browser"""
        self.notification_browser.append(
            f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {message}"
        )

    def apply_theme(self):
        """Áp dụng theme (sáng hoặc tối) cho ứng dụng"""
        if self.dark_mode:
            self.setStyleSheet(DARK_THEME)
            if self.toggle_theme_action:
                self.toggle_theme_action.setText("Chế độ sáng")
        else:
            self.setStyleSheet(LIGHT_THEME)
            if self.toggle_theme_action:
                self.toggle_theme_action.setText("Chế độ tối")
        
        # Cập nhật trạng thái checkbox
        if self.toggle_theme_action:
            self.toggle_theme_action.setChecked(self.dark_mode)
        
        # Cập nhật lại schedule widget để vẽ lại với theme mới
        if hasattr(self, 'schedule_view'):
            self.schedule_view.update()

    def toggle_theme(self):
        """Chuyển đổi giữa chế độ sáng và tối"""
        self.dark_mode = not self.dark_mode
        self.settings.setValue("dark_mode", self.dark_mode)
        self.apply_theme()
        mode_text = "tối" if self.dark_mode else "sáng"
        self.log_message(f"Đã chuyển sang chế độ {mode_text}")

