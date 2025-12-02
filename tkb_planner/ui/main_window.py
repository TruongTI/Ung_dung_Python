"""
Main window của ứng dụng TKB Planner Pro
"""

import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QCheckBox, QScrollArea, QFrame,
    QTextBrowser, QStatusBar, QFileDialog, QMessageBox,
    QTimeEdit, QSizePolicy, QComboBox
)
from PyQt6.QtCore import Qt, QTime, QSettings
from PyQt6.QtGui import QFont, QAction

from ..models import MonHoc, LopHoc, LichBan
from ..scheduler import tim_thoi_khoa_bieu, kiem_tra_trung_trong_cung_mon, update_bidirectional_constraints, _kiem_tra_trung_voi_lich
from ..data_handler import (
    save_data, load_data, create_sample_data_if_not_exists,
    save_completed_courses, load_completed_courses,
    save_busy_times, load_busy_times
)
from ..constants import DATA_FILE, TEN_THU_TRONG_TUAN
from .schedule_widget import ScheduleWidget
from .dialogs import SubjectDialog, ClassDialog, CompletedCoursesDialog, ViewCompletedCoursesDialog, EditAllSubjectsDialog, EditAllClassesDialog
from .course_classes_dialog import CourseClassesDialog
from .theme import LIGHT_THEME, DARK_THEME
from .custom_checkbox import CustomCheckBox


class MainWindow(QMainWindow):
    """Cửa sổ chính của ứng dụng"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Công cụ Sắp xếp TKB Pro")
        self.setGeometry(100, 100, 1288, 900)  # Tăng chiều cao từ 780 lên 900
        self.setFont(QFont("Segoe UI", 10))
        
        # Load settings
        self.settings = QSettings("TKBPlanner", "TKBPlannerPro")
        self.dark_mode = self.settings.value("dark_mode", True, type=bool)  # Mặc định là chế độ tối
        
        create_sample_data_if_not_exists()
        self.all_courses = load_data()
        self.danh_sach_gio_ban = load_busy_times()  # Load giờ bận từ file
        self.danh_sach_tkb_tim_duoc = []
        self.current_tkb_index = -1
        self.course_widgets = {}
        self.busy_time_widgets = {}
        self.busy_time_checkboxes = {}  # Lưu checkbox của từng giờ bận
        self.toggle_theme_action = None  # Khởi tạo trước
        # Danh sách môn đã học
        self.completed_courses = load_completed_courses()
        self._setup_ui()
        self._setup_menu_bar()
        self._populate_course_list()
        self._populate_busy_times()  # Load và hiển thị giờ bận đã lưu
        self._connect_signals()
        self.apply_theme()  # Áp dụng theme sau khi setup UI
        # Hiển thị giờ bận ngay khi khởi động
        self._update_schedule_display()
        self.log_message("Chào mừng! Chọn môn học và giờ bận để bắt đầu.")

    def _setup_ui(self):
        """Thiết lập giao diện người dùng"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QHBoxLayout(self.central_widget)
        
        # Panel bên trái
        left_panel = QGroupBox("Bảng điều khiển")
        left_panel.setMinimumHeight(700)  # Đặt chiều cao tối thiểu cho panel bên trái
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
        # Nút Thêm Môn bên cạnh ô nhập
        self.add_subject_btn = QPushButton("Thêm Môn")
        self.add_subject_btn.setMinimumHeight(30)
        search_layout.addWidget(self.add_subject_btn)
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
        busy_layout.setSpacing(8)  # Thêm khoảng cách giữa các hàng
        
        # Hàng 1: Thứ và Lý do
        busy_input_layout1 = QHBoxLayout()
        busy_input_layout1.setSpacing(8)
        thu_label = QLabel("Thứ:")
        thu_label.setMinimumWidth(40)
        self.busy_thu_combo = QComboBox()
        self.busy_thu_combo.addItems(TEN_THU_TRONG_TUAN.values())
        self.busy_thu_combo.setMinimumWidth(120)
        self.busy_thu_combo.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        
        reason_label = QLabel("Lý do:")
        reason_label.setMinimumWidth(40)
        self.busy_reason_input = QLineEdit()
        self.busy_reason_input.setPlaceholderText("Nhập lý do bận...")
        self.busy_reason_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        busy_input_layout1.addWidget(thu_label, 0)
        busy_input_layout1.addWidget(self.busy_thu_combo, 0)
        busy_input_layout1.addWidget(reason_label, 0)
        busy_input_layout1.addWidget(self.busy_reason_input, 1)  # Ô lý do chiếm không gian còn lại
        
        # Hàng 2: Giờ bắt đầu, giờ kết thúc và nút Thêm
        busy_input_layout2 = QHBoxLayout()
        busy_input_layout2.setSpacing(8)
        
        start_label = QLabel("Bắt đầu:")
        start_label.setMinimumWidth(60)
        self.busy_start_time = QTimeEdit(QTime(7, 0))
        self.busy_start_time.setDisplayFormat("HH:mm")  # Format 24 giờ
        self.busy_start_time.setMinimumWidth(80)
        self.busy_start_time.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        
        end_label = QLabel("Kết thúc:")
        end_label.setMinimumWidth(60)
        self.busy_end_time = QTimeEdit(QTime(8, 0))
        self.busy_end_time.setDisplayFormat("HH:mm")  # Format 24 giờ
        self.busy_end_time.setMinimumWidth(80)
        self.busy_end_time.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        
        self.add_busy_btn = QPushButton("Thêm")
        self.add_busy_btn.setMinimumWidth(70)
        self.add_busy_btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        
        busy_input_layout2.addWidget(start_label, 0)
        busy_input_layout2.addWidget(self.busy_start_time, 0)
        busy_input_layout2.addWidget(end_label, 0)
        busy_input_layout2.addWidget(self.busy_end_time, 0)
        busy_input_layout2.addStretch()  # Thêm khoảng trống để đẩy nút sang phải
        busy_input_layout2.addWidget(self.add_busy_btn, 0)
        
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
        
        left_panel_layout.addWidget(course_group, 4)  # Tăng từ 3 lên 4
        left_panel_layout.addWidget(busy_group, 3)    # Tăng từ 2 lên 3
        left_panel_layout.addWidget(notification_group, 1)  # Giữ nguyên
        
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
        
        # Label hiển thị số thời khóa biểu hiện tại/tổng số (giữa 2 nút)
        self.tkb_info_label = QLabel("Chưa có thời khóa biểu")
        self.tkb_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tkb_info_label.setStyleSheet("font-weight: bold; padding: 5px;")
        
        self.next_tkb_btn = QPushButton("TKB Tiếp >")
        self.save_tkb_btn = QPushButton("Lưu TKB")
        self.clear_tkb_btn = QPushButton("Xoá TKB")
        self.pack_early_btn = QPushButton("Dồn lịch đầu tuần")
        self.pack_late_btn = QPushButton("Dồn lịch cuối tuần")

        button_height = 30
        self.find_tkb_btn.setMinimumHeight(button_height)
        self.prev_tkb_btn.setMinimumHeight(button_height)
        self.next_tkb_btn.setMinimumHeight(button_height)
        self.save_tkb_btn.setMinimumHeight(button_height)
        self.clear_tkb_btn.setMinimumHeight(button_height)
        self.pack_early_btn.setMinimumHeight(button_height)
        self.pack_late_btn.setMinimumHeight(button_height)

        button_layout.addWidget(self.find_tkb_btn)
        button_layout.addWidget(self.prev_tkb_btn)
        button_layout.addWidget(self.tkb_info_label)  # Label ở giữa 2 nút
        button_layout.addWidget(self.next_tkb_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.save_tkb_btn)
        button_layout.addWidget(self.clear_tkb_btn)
        right_panel_layout.addLayout(button_layout)
        
        # Layout cho 2 nút dồn lịch
        pack_button_layout = QHBoxLayout()
        pack_button_layout.addWidget(self.pack_early_btn)
        pack_button_layout.addWidget(self.pack_late_btn)
        right_panel_layout.addLayout(pack_button_layout)
        
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
        import_tkb_action = QAction("Import thời khóa biểu", self)
        import_tkb_action.triggered.connect(self.handle_import_tkb)
        file_menu.addAction(import_tkb_action)
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
        edit_menu.addSeparator()
        edit_subject_action = QAction("Sửa môn học", self)
        edit_subject_action.triggered.connect(self.handle_edit_all_subjects)
        edit_menu.addAction(edit_subject_action)
        edit_class_action = QAction("Sửa lớp học", self)
        edit_class_action.triggered.connect(self.handle_edit_all_classes)
        edit_menu.addAction(edit_class_action)
        
        # Menu View
        view_menu = menu_bar.addMenu("&View")
        select_all_action = QAction("Chọn tất cả các môn", self)
        select_all_action.triggered.connect(lambda: self.handle_select_all(True))
        view_menu.addAction(select_all_action)
        deselect_all_action = QAction("Bỏ chọn tất cả", self)
        deselect_all_action.triggered.connect(lambda: self.handle_select_all(False))
        view_menu.addAction(deselect_all_action)
        view_menu.addSeparator()
        # Menu xóa toàn bộ dữ liệu
        clear_all_action = QAction("Xóa toàn bộ dữ liệu", self)
        clear_all_action.triggered.connect(self.handle_clear_all_data)
        view_menu.addAction(clear_all_action)
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
        tkb_menu.addSeparator()
        # Menu môn đã học
        input_completed_action = QAction("Nhập môn đã học", self)
        input_completed_action.triggered.connect(self.handle_input_completed_courses)
        tkb_menu.addAction(input_completed_action)
        view_completed_action = QAction("Xem danh sách môn đã học", self)
        view_completed_action.triggered.connect(self.handle_view_completed_courses)
        tkb_menu.addAction(view_completed_action)
        
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
            
            check = CustomCheckBox(f"{mon_hoc.ten_mon} ({mon_hoc.ma_mon})")
            check.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            # Cho phép click vào text mà không toggle checkbox
            check.set_allow_text_click(True)
            # Kết nối sự kiện click vào text để hiển thị các lớp của môn học
            check.textClicked.connect(lambda m=mon_hoc: self.handle_show_course_classes(m))
            # Disable checkbox cho các môn đã có trong danh sách môn đã học
            if mon_hoc.ma_mon in self.completed_courses:
                check.setEnabled(False)
                check.setToolTip("Môn này đã được đánh dấu là đã học")
            mandatory_check = CustomCheckBox("Bắt buộc")
            mandatory_check.setToolTip("TKB tìm được phải chứa môn này")
            mandatory_check.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
            # Disable checkbox bắt buộc cho các môn đã học
            if mon_hoc.ma_mon in self.completed_courses:
                mandatory_check.setEnabled(False)
            
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
        self.pack_early_btn.clicked.connect(self.handle_pack_early_week)
        self.pack_late_btn.clicked.connect(self.handle_pack_late_week)
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
                # Refresh lại danh sách môn học để cập nhật thông tin
                self._populate_course_list()
                # Cập nhật lại schedule nếu đang hiển thị
                active_busy_times = self._get_active_busy_times()
                if self.current_tkb_index >= 0 and self.danh_sach_tkb_tim_duoc:
                    self.schedule_view.display_schedule(
                        self.danh_sach_tkb_tim_duoc[self.current_tkb_index],
                        self.all_courses,
                        active_busy_times
                    )
                else:
                    self.schedule_view.display_schedule([], self.all_courses, active_busy_times)
                self.log_message(f"Đã cập nhật môn học: {ma_mon}")
            else:
                QMessageBox.warning(self, "Lỗi", "Tên môn không được để trống.")

    def handle_add_class_dialog(self, default_thu=None, default_tiet=None):
        """Xử lý thêm lớp học mới"""
        if not self.all_courses:
            QMessageBox.warning(self, "Chưa có môn học", 
                              "Vui lòng thêm một môn học trước khi thêm lớp.")
            return
        dialog = ClassDialog(self.all_courses, default_thu, default_tiet, fixed_mon_hoc=None, parent=self)
        if dialog.exec():
            data = dialog.get_data()
            if data:
                mon_hoc = self.all_courses[data['ma_mon']]
                new_lop = LopHoc(data['ma_lop'], data['ten_gv'], 
                               mon_hoc.ma_mon, mon_hoc.ten_mon,
                               loai_lop=data.get('loai_lop', 'Lớp'),
                               lop_rang_buoc=data.get('lop_rang_buoc', []))
                new_lop.them_khung_gio(data['thu'], data['tiet_bd'], data['tiet_kt'])
                
                # Kiểm tra trùng trong cùng môn (phòng học, giáo viên và trùng giờ)
                is_valid, error_msg = kiem_tra_trung_trong_cung_mon(new_lop, mon_hoc)
                if not is_valid:
                    QMessageBox.warning(self, "Lỗi", error_msg)
                    return
                
                # Thêm lớp học (hàm này sẽ kiểm tra trùng giờ trong cùng môn và cùng phòng)
                if not mon_hoc.them_lop_hoc(new_lop):
                    QMessageBox.warning(self, "Lỗi", 
                                      f"Lớp học '{data['ma_lop']}' đã tồn tại với cùng giờ học trong môn này.")
                    return
                
                # Cập nhật ràng buộc 2 chiều cho lớp mới
                new_lop_id = new_lop.get_id()
                new_rang_buoc = data.get('lop_rang_buoc', [])
                update_bidirectional_constraints(None, [], new_lop_id, new_rang_buoc, self.all_courses)
                
                save_data(self.all_courses)
                self.log_message(f"Đã thêm lớp {data['ma_lop']} cho môn {data['ma_mon']}")
            else:
                QMessageBox.warning(self, "Lỗi", 
                                  "Vui lòng điền đủ thông tin và đảm bảo tiết bắt đầu <= tiết kết thúc.")

    def handle_cell_click(self, thu, tiet):
        """Xử lý khi click vào ô lịch"""
        try:
            ten_thu = TEN_THU_TRONG_TUAN.get(thu, f"Thứ {thu}")
            self.log_message(f"Chọn thêm lớp mới vào {ten_thu}, Tiết {tiet}...")
            
            # Kiểm tra xem có môn học nào chưa
            if not self.all_courses:
                QMessageBox.warning(self, "Chưa có môn học", 
                                  "Vui lòng thêm một môn học trước khi thêm lớp.")
                return
            
            # Mở dialog thêm lớp với thứ và tiết đã chọn
            self.handle_add_class_dialog(default_thu=thu, default_tiet=tiet)
        except Exception as e:
            self.log_message(f"Lỗi khi xử lý click vào lịch: {e}")
            QMessageBox.warning(self, "Lỗi", f"Đã xảy ra lỗi: {e}")

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

    def handle_clear_all_data(self):
        """Xóa toàn bộ môn học và lớp học"""
        if not self.all_courses:
            QMessageBox.information(self, "Thông báo", "Không có dữ liệu để xóa.")
            return
        
        # Xác nhận xóa
        reply = QMessageBox.question(
            self, 
            'Xác nhận xóa', 
            'Bạn có chắc muốn xóa TOÀN BỘ môn học và lớp học?\n\nHành động này không thể hoàn tác!',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Xóa tất cả môn học
            self.all_courses.clear()
            
            # Xóa danh sách môn đã học
            self.completed_courses.clear()
            save_completed_courses(self.completed_courses)
            
            # Xóa kết quả tìm kiếm TKB
            self.danh_sach_tkb_tim_duoc = []
            self.current_tkb_index = -1
            active_busy_times = self._get_active_busy_times()
            self.schedule_view.display_schedule([], self.all_courses, active_busy_times)
            self.update_tkb_info_label()
            
            # Xóa danh sách giờ bận
            self.danh_sach_gio_ban = []
            for widget in self.busy_time_widgets.values():
                widget.deleteLater()
            self.busy_time_widgets.clear()
            
            # Cập nhật UI
            self._populate_course_list()
            
            # Lưu file (file sẽ trống)
            save_data(self.all_courses)
            
            self.log_message("Đã xóa toàn bộ dữ liệu môn học và lớp học.")
            QMessageBox.information(self, "Thành công", "Đã xóa toàn bộ dữ liệu.")

    def handle_about(self):
        """Hiển thị thông tin về ứng dụng"""
        QMessageBox.about(self, "Giới thiệu", 
                        "Công cụ Sắp xếp TKB Pro\n\n"
                        "Phiên bản 3.0")
    
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
            # Xóa môn khỏi danh sách môn đã học nếu có
            if ma_mon in self.completed_courses:
                self.completed_courses.remove(ma_mon)
                save_completed_courses(self.completed_courses)
            save_data(self.all_courses)
            # Refresh lại danh sách môn học
            self._populate_course_list()
            # Cập nhật lại schedule nếu đang hiển thị
            active_busy_times = self._get_active_busy_times()
            if self.current_tkb_index >= 0 and self.danh_sach_tkb_tim_duoc:
                self.schedule_view.display_schedule(
                    self.danh_sach_tkb_tim_duoc[self.current_tkb_index],
                    self.all_courses,
                    active_busy_times
                )
            else:
                self.schedule_view.display_schedule([], self.all_courses, active_busy_times)
            self.log_message(f"Đã xoá môn {ma_mon}.")

    def filter_course_list(self):
        """Lọc danh sách môn học theo từ khóa"""
        filter_text = self.search_input.text().lower()
        for ma_mon, widgets in self.course_widgets.items():
            mon_hoc = self.all_courses[ma_mon]
            text_to_check = f"{mon_hoc.ten_mon} ({mon_hoc.ma_mon})".lower()
            widgets['container'].setVisible(filter_text in text_to_check)
    
    def _populate_busy_times(self):
        """Load và hiển thị danh sách giờ bận đã lưu"""
        for busy_time in self.danh_sach_gio_ban:
            busy_id = busy_time.id
            container = QFrame()
            container.setFrameShape(QFrame.Shape.StyledPanel)
            layout = QHBoxLayout(container)
            layout.setContentsMargins(5, 3, 5, 3)
            layout.setSpacing(5)
            
            check = CustomCheckBox(str(busy_time))
            check.setChecked(True)  # Mặc định tích
            check.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            check.toggled.connect(lambda: self._update_schedule_display())  # Cập nhật khi toggle
            
            delete_btn = QPushButton("Xoá")
            delete_btn.setMinimumWidth(55)
            delete_btn.setMaximumWidth(70)
            delete_btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
            
            layout.addWidget(check, 1)
            layout.addWidget(delete_btn, 0)
            delete_btn.clicked.connect(lambda _, bid=busy_id: self.handle_delete_busy_time(bid))
            self.busy_list_layout.addWidget(container)
            self.busy_time_widgets[busy_id] = container
            self.busy_time_checkboxes[busy_id] = check
            
    def handle_add_busy_time(self):
        """Xử lý thêm giờ bận"""
        ten_thu = self.busy_thu_combo.currentText()
        # Tìm thứ từ tên thứ
        thu = [k for k, v in TEN_THU_TRONG_TUAN.items() if v == ten_thu][0]
        start_time = self.busy_start_time.time()
        end_time = self.busy_end_time.time()
        reason = self.busy_reason_input.text() or "Bận"
        if start_time >= end_time:
            self.log_message("Lỗi: Giờ bắt đầu phải trước giờ kết thúc.")
            return
        
        busy_id = datetime.datetime.now().timestamp()
        new_busy_time = LichBan(thu, start_time, end_time, reason, busy_id)
        self.danh_sach_gio_ban.append(new_busy_time)
        
        container = QFrame()
        container.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(5, 3, 5, 3)  # Thêm margin để tránh bị che
        layout.setSpacing(5)  # Thêm khoảng cách giữa các widget
        
        check = CustomCheckBox(str(new_busy_time))
        check.setChecked(True)
        check.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        check.toggled.connect(lambda: self._update_schedule_display())  # Cập nhật khi toggle
        
        delete_btn = QPushButton("Xoá")
        delete_btn.setMinimumWidth(55)  # Thay vì setFixedWidth
        delete_btn.setMaximumWidth(70)
        delete_btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        
        layout.addWidget(check, 1)  # Checkbox chiếm không gian còn lại
        layout.addWidget(delete_btn, 0)  # Nút Xoá không co giãn
        delete_btn.clicked.connect(lambda: self.handle_delete_busy_time(busy_id))
        self.busy_list_layout.addWidget(container)
        self.busy_time_widgets[busy_id] = container
        self.busy_time_checkboxes[busy_id] = check
        self.log_message(f"Đã thêm giờ bận: {new_busy_time}")
        
        # Lưu vào file
        save_busy_times(self.danh_sach_gio_ban)
        
        # Cập nhật hiển thị giờ bận trên lịch (SAU KHI đã thêm checkbox)
        self._update_schedule_display()

    def handle_delete_busy_time(self, busy_id):
        """Xử lý xóa giờ bận"""
        self.danh_sach_gio_ban = [b for b in self.danh_sach_gio_ban if b.id != busy_id]
        if busy_id in self.busy_time_widgets:
            self.busy_time_widgets[busy_id].deleteLater()
            del self.busy_time_widgets[busy_id]
        if busy_id in self.busy_time_checkboxes:
            del self.busy_time_checkboxes[busy_id]
        self.log_message("Đã xoá một giờ bận.")
        # Lưu vào file
        save_busy_times(self.danh_sach_gio_ban)
        # Cập nhật hiển thị giờ bận trên lịch
        self._update_schedule_display()

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
        # Chỉ lấy giờ bận được tích checkbox
        active_busy_times = self._get_active_busy_times()
        self.log_message("Đang tìm kiếm TKB...")
        QApplication.processEvents()
        self.danh_sach_tkb_tim_duoc, error_msg = tim_thoi_khoa_bieu(
            selected_courses, active_busy_times, mandatory_courses, self.completed_courses, self.all_courses
        )
        if error_msg:
            self.log_message(error_msg)
            self.schedule_view.display_schedule([], self.all_courses, active_busy_times)
            self.current_tkb_index = -1
            self.update_tkb_info_label()
        elif not self.danh_sach_tkb_tim_duoc:
            self.log_message("Không tìm thấy TKB nào phù hợp.")
            self.schedule_view.display_schedule([], self.all_courses, active_busy_times)
            self.current_tkb_index = -1
            self.update_tkb_info_label()
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
        active_busy_times = self._get_active_busy_times()
        self.schedule_view.display_schedule(tkb, self.all_courses, active_busy_times)
        self.statusBar().showMessage(f"Đang xem TKB {index + 1} / {len(self.danh_sach_tkb_tim_duoc)}")
        # Cập nhật label hiển thị số thời khóa biểu
        self.update_tkb_info_label()

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
        has_current_tkb = has_results and self.current_tkb_index >= 0
        self.prev_tkb_btn.setEnabled(has_results)
        self.next_tkb_btn.setEnabled(has_results)
        self.save_tkb_btn.setEnabled(has_results)
        self.clear_tkb_btn.setEnabled(has_results)
        self.pack_early_btn.setEnabled(has_current_tkb)
        self.pack_late_btn.setEnabled(has_current_tkb)

    def handle_clear_tkb(self):
        """Xóa kết quả tìm kiếm TKB"""
        self.danh_sach_tkb_tim_duoc = []
        self.current_tkb_index = -1
        active_busy_times = self._get_active_busy_times()
        self.schedule_view.display_schedule([], self.all_courses, active_busy_times)
        self.update_tkb_info_label()
        self.log_message("Đã xoá kết quả tìm kiếm TKB.")
        self.statusBar().showMessage("Sẵn sàng")
        self.update_nav_buttons()
    
    def _get_active_busy_times(self):
        """Lấy danh sách giờ bận được tích checkbox"""
        return [
            b for b in self.danh_sach_gio_ban 
            if b.id in self.busy_time_checkboxes and self.busy_time_checkboxes[b.id].isChecked()
        ]
    
    def _update_schedule_display(self):
        """Cập nhật hiển thị lịch với giờ bận hiện tại (chỉ hiển thị giờ bận được tích checkbox)"""
        active_busy_times = self._get_active_busy_times()
        if self.current_tkb_index >= 0 and self.danh_sach_tkb_tim_duoc:
            tkb = self.danh_sach_tkb_tim_duoc[self.current_tkb_index]
            self.schedule_view.display_schedule(tkb, self.all_courses, active_busy_times)
        else:
            self.schedule_view.display_schedule([], self.all_courses, active_busy_times)

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

    def handle_import_tkb(self):
        """Import TKB từ file đã lưu"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Thời khóa biểu", "", "Text Files (*.txt);;All Files (*)"
        )
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse file để tìm các lớp học
            imported_classes = []
            lines = content.split('\n')
            i = 0
            current_ma_mon = None
            current_ma_lop = None
            current_ten_gv = None
            current_khung_gio = []
            
            while i < len(lines):
                line = lines[i].strip()
                
                # Tìm dòng "Môn: ..."
                if line.startswith("Môn:"):
                    # Lưu lớp học trước đó nếu có
                    if current_ma_mon and current_ma_lop and current_ten_gv and current_khung_gio:
                        # Tìm lớp học trong all_courses
                        if current_ma_mon in self.all_courses:
                            mon_hoc = self.all_courses[current_ma_mon]
                            for lop in mon_hoc.cac_lop_hoc:
                                if (lop.ma_lop == current_ma_lop and 
                                    lop.ten_giao_vien.strip().lower() == current_ten_gv.strip().lower()):
                                    # Kiểm tra khung giờ có khớp không
                                    lop_khung_gio = [(g.thu, g.tiet_bat_dau, g.tiet_ket_thuc) 
                                                     for g in lop.cac_khung_gio]
                                    if set(current_khung_gio) == set(lop_khung_gio):
                                        imported_classes.append(lop)
                                        break
                    
                    # Parse mã môn từ dòng "Môn: Tên môn (Mã môn)"
                    if '(' in line and ')' in line:
                        ma_mon = line.split('(')[1].split(')')[0].strip()
                        current_ma_mon = ma_mon
                        current_ma_lop = None
                        current_ten_gv = None
                        current_khung_gio = []
                
                # Tìm dòng "  Lớp: ..."
                elif line.startswith("Lớp:"):
                    current_ma_lop = line.replace("Lớp:", "").strip()
                
                # Tìm dòng "  GV: ..."
                elif line.startswith("GV:"):
                    current_ten_gv = line.replace("GV:", "").strip()
                
                # Tìm dòng "  Thời gian: ..."
                elif line.startswith("Thời gian:"):
                    # Parse "Thời gian: Thứ X, Tiết Y-Z"
                    time_part = line.replace("Thời gian:", "").strip()
                    if "," in time_part:
                        thu_part = time_part.split(",")[0].strip()
                        tiet_part = time_part.split(",")[1].strip()
                        
                        # Tìm số thứ từ tên thứ
                        thu = None
                        for k, v in TEN_THU_TRONG_TUAN.items():
                            if v == thu_part:
                                thu = k
                                break
                        
                        # Parse tiết "Tiết Y-Z"
                        if thu and "Tiết" in tiet_part:
                            tiet_str = tiet_part.replace("Tiết", "").strip()
                            if "-" in tiet_str:
                                tiet_bd = int(tiet_str.split("-")[0].strip())
                                tiet_kt = int(tiet_str.split("-")[1].strip())
                                current_khung_gio.append((thu, tiet_bd, tiet_kt))
                
                i += 1
            
            # Lưu lớp học cuối cùng
            if current_ma_mon and current_ma_lop and current_ten_gv and current_khung_gio:
                if current_ma_mon in self.all_courses:
                    mon_hoc = self.all_courses[current_ma_mon]
                    for lop in mon_hoc.cac_lop_hoc:
                        if (lop.ma_lop == current_ma_lop and 
                            lop.ten_giao_vien.strip().lower() == current_ten_gv.strip().lower()):
                            lop_khung_gio = [(g.thu, g.tiet_bat_dau, g.tiet_ket_thuc) 
                                             for g in lop.cac_khung_gio]
                            if set(current_khung_gio) == set(lop_khung_gio):
                                imported_classes.append(lop)
                                break
            
            if not imported_classes:
                QMessageBox.warning(self, "Lỗi", 
                                  "Không tìm thấy lớp học nào trong file. "
                                  "Vui lòng kiểm tra lại file hoặc đảm bảo các lớp học đã được thêm vào hệ thống.")
                return
            
            # Hiển thị TKB đã import
            self.danh_sach_tkb_tim_duoc = [imported_classes]
            self.current_tkb_index = 0
            active_busy_times = self._get_active_busy_times()
            self.schedule_view.display_schedule(imported_classes, self.all_courses, active_busy_times)
            self.update_nav_buttons()
            self.update_tkb_info_label()
            self.log_message(f"Đã import TKB thành công: {len(imported_classes)} lớp học")
            QMessageBox.information(self, "Thành công", 
                                  f"Đã import TKB thành công!\nTìm thấy {len(imported_classes)} lớp học.")
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể import TKB: {e}")
            self.log_message(f"Lỗi khi import TKB: {e}")

    def log_message(self, message):
        """Ghi log vào notification browser"""
        self.notification_browser.append(
            f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {message}"
        )

    def update_tkb_info_label(self):
        """Cập nhật label hiển thị số thời khóa biểu hiện tại/tổng số"""
        if not self.danh_sach_tkb_tim_duoc or self.current_tkb_index == -1:
            self.tkb_info_label.setText("Chưa có thời khóa biểu")
        else:
            current = self.current_tkb_index + 1
            total = len(self.danh_sach_tkb_tim_duoc)
            self.tkb_info_label.setText(f"Thời khóa biểu: {current}/{total}")

    def handle_show_course_classes(self, mon_hoc):
        """Hiển thị dialog các lớp học của môn học"""
        dialog = CourseClassesDialog(mon_hoc, all_courses=self.all_courses, parent=self)
        dialog.exec()  # Luôn refresh sau khi đóng dialog, không cần kiểm tra return value
        # Xử lý các lớp đã xóa (nếu có)
        deleted_classes = dialog.get_deleted_classes()
        if deleted_classes:
            for lop in deleted_classes:
                mon_hoc.cac_lop_hoc = [l for l in mon_hoc.cac_lop_hoc if l.get_id() != lop.get_id()]
                mon_hoc.cac_lop_hoc_dict.pop(lop.get_id(), None)
                self.log_message(f"Đã xóa lớp {lop.ma_lop} khỏi môn {mon_hoc.ma_mon}")
            # Lưu dữ liệu
            save_data(self.all_courses)
            self.log_message(f"Đã cập nhật danh sách lớp học của môn {mon_hoc.ma_mon}")
        
        # Luôn refresh lại danh sách môn học để cập nhật số lớp học
        self._populate_course_list()
        # Cập nhật lại schedule nếu đang hiển thị
        active_busy_times = self._get_active_busy_times()
        if self.current_tkb_index >= 0 and self.danh_sach_tkb_tim_duoc:
            self.schedule_view.display_schedule(
                self.danh_sach_tkb_tim_duoc[self.current_tkb_index],
                self.all_courses,
                active_busy_times
            )
        else:
            self.schedule_view.display_schedule([], self.all_courses, active_busy_times)

    def handle_input_completed_courses(self):
        """Xử lý nhập môn đã học"""
        # Callback để thêm môn mới từ dialog
        def add_course_from_dialog():
            """Callback để thêm môn mới và trả về mã môn vừa thêm"""
            dialog_subject = SubjectDialog(self, mon_hoc=None)
            if dialog_subject.exec():
                data = dialog_subject.get_data()
                if data and data['ma_mon'] not in self.all_courses:
                    new_mon = MonHoc(data['ma_mon'], data['ten_mon'], data['tien_quyet'])
                    self.all_courses[data['ma_mon']] = new_mon
                    self._populate_course_list()
                    save_data(self.all_courses)
                    self.log_message(f"Đã thêm môn học mới: {data['ma_mon']}")
                    return data['ma_mon']
                elif not data:
                    QMessageBox.warning(self, "Lỗi", "Mã môn và Tên môn không được để trống.")
                else:
                    QMessageBox.warning(self, "Lỗi", f"Mã môn '{data['ma_mon']}' đã tồn tại.")
            return None
        
        dialog = CompletedCoursesDialog(
            self.all_courses, 
            self.completed_courses, 
            add_course_callback=add_course_from_dialog,
            parent=self
        )
        if dialog.exec():
            selected_courses = dialog.get_selected_courses()
            self.completed_courses = selected_courses
            if save_completed_courses(self.completed_courses):
                self.log_message(f"Đã lưu {len(self.completed_courses)} môn đã học.")
                # Cập nhật lại danh sách môn học để cập nhật trạng thái disable/enable
                self._populate_course_list()
                QMessageBox.information(self, "Thành công", 
                                      f"Đã lưu {len(self.completed_courses)} môn đã học.")
            else:
                self.log_message("Lỗi khi lưu danh sách môn đã học.")

    def handle_view_completed_courses(self):
        """Hiển thị danh sách môn đã học"""
        dialog = ViewCompletedCoursesDialog(self.all_courses, self.completed_courses, self)
        # Luôn cập nhật danh sách sau khi đóng dialog (dù có thay đổi hay không)
        dialog.exec()
        # Lấy danh sách đã cập nhật (có thể đã thay đổi trong dialog)
        updated_courses = dialog.get_updated_completed_courses()
        if updated_courses != self.completed_courses:
            self.completed_courses = updated_courses
            if save_completed_courses(self.completed_courses):
                self.log_message(f"Đã cập nhật danh sách môn đã học: {len(self.completed_courses)} môn.")
                # Cập nhật lại danh sách môn học để cập nhật trạng thái disable/enable
                self._populate_course_list()
            else:
                self.log_message("Lỗi khi lưu danh sách môn đã học.")

    def handle_edit_all_subjects(self):
        """Hiển thị dialog để sửa/xóa tất cả môn học"""
        if not self.all_courses:
            QMessageBox.information(self, "Thông báo", "Chưa có môn học nào để sửa.")
            return
        
        dialog = EditAllSubjectsDialog(self.all_courses, self)
        dialog.exec()
        # Refresh lại danh sách môn học sau khi đóng dialog
        self._populate_course_list()
        # Cập nhật lại schedule nếu đang hiển thị
        active_busy_times = self._get_active_busy_times()
        if self.current_tkb_index >= 0 and self.danh_sach_tkb_tim_duoc:
            self.schedule_view.display_schedule(
                self.danh_sach_tkb_tim_duoc[self.current_tkb_index],
                self.all_courses,
                active_busy_times
            )
        else:
            self.schedule_view.display_schedule([], self.all_courses, active_busy_times)
    
    def handle_edit_all_classes(self):
        """Hiển thị dialog để sửa/xóa tất cả lớp học"""
        if not self.all_courses:
            QMessageBox.information(self, "Thông báo", "Chưa có môn học nào.")
            return
        
        # Kiểm tra xem có lớp học nào không
        has_classes = any(mon.cac_lop_hoc for mon in self.all_courses.values())
        if not has_classes:
            QMessageBox.information(self, "Thông báo", "Chưa có lớp học nào để sửa.")
            return
        
        dialog = EditAllClassesDialog(self.all_courses, self)
        dialog.exec()
        # Refresh lại danh sách môn học sau khi đóng dialog
        self._populate_course_list()
        # Cập nhật lại schedule nếu đang hiển thị
        active_busy_times = self._get_active_busy_times()
        if self.current_tkb_index >= 0 and self.danh_sach_tkb_tim_duoc:
            self.schedule_view.display_schedule(
                self.danh_sach_tkb_tim_duoc[self.current_tkb_index],
                self.all_courses,
                active_busy_times
            )
        else:
            self.schedule_view.display_schedule([], self.all_courses, active_busy_times)

    def _get_earliest_thu(self, lop):
        """Lấy thứ sớm nhất trong các khung giờ của lớp học"""
        if not lop.cac_khung_gio:
            return None
        return min(gio.thu for gio in lop.cac_khung_gio)
    
    def _pack_schedule(self, pack_to_early=True):
        """
        Dồn lịch học vào đầu tuần hoặc cuối tuần
        
        Args:
            pack_to_early: True nếu dồn vào đầu tuần, False nếu dồn vào cuối tuần
        """
        if self.current_tkb_index == -1 or not self.danh_sach_tkb_tim_duoc:
            QMessageBox.warning(self, "Cảnh báo", "Chưa có TKB để dồn lịch.")
            return
        
        tkb = self.danh_sach_tkb_tim_duoc[self.current_tkb_index]
        active_busy_times = self._get_active_busy_times()
        
        # Tạo bản sao của TKB để sửa đổi
        new_tkb = list(tkb)
        changed = False
        
        # Sắp xếp các lớp học theo thứ hiện tại để xử lý
        # Đầu tuần: xử lý từ thứ muộn nhất đến sớm nhất (8->2)
        # Cuối tuần: xử lý từ thứ sớm nhất đến muộn nhất (2->8)
        # Tạo list với index gốc để có thể thay thế đúng
        indexed_lops = [(i, lop) for i, lop in enumerate(new_tkb)]
        sorted_indexed_lops = sorted(indexed_lops, 
                                     key=lambda x: self._get_earliest_thu(x[1]) or 0, 
                                     reverse=pack_to_early)
        
        for orig_index, current_lop in sorted_indexed_lops:
            if not current_lop.cac_khung_gio:
                continue
            
            current_thu = self._get_earliest_thu(current_lop)
            if current_thu is None:
                continue
            
            # Tìm môn học tương ứng
            mon_hoc = self.all_courses.get(current_lop.ma_mon)
            if not mon_hoc:
                continue
            
            # Tìm các lớp học khác cùng môn có thể thay thế
            alternative_lops = []
            for alt_lop in mon_hoc.cac_lop_hoc:
                # Bỏ qua lớp hiện tại
                if alt_lop is current_lop:
                    continue
                alt_thu = self._get_earliest_thu(alt_lop)
                if alt_thu is None:
                    continue
                
                # Kiểm tra xem lớp thay thế có thứ tốt hơn không
                if pack_to_early:
                    # Đầu tuần: thứ nhỏ hơn là tốt hơn
                    if alt_thu < current_thu:
                        alternative_lops.append((alt_thu, alt_lop))
                else:
                    # Cuối tuần: thứ lớn hơn là tốt hơn
                    if alt_thu > current_thu:
                        alternative_lops.append((alt_thu, alt_lop))
            
            # Sắp xếp các lớp thay thế: đầu tuần (tăng dần) hoặc cuối tuần (giảm dần)
            alternative_lops.sort(key=lambda x: x[0], reverse=not pack_to_early)
            
            # Thử thay thế từng lớp
            for alt_thu, alt_lop in alternative_lops:
                # Tạo TKB tạm thời để kiểm tra (thay thế lớp hiện tại)
                temp_tkb = [lop if lop is not current_lop else alt_lop for lop in new_tkb]
                
                # Kiểm tra xung đột
                if not _kiem_tra_trung_voi_lich(alt_lop, temp_tkb, active_busy_times):
                    # Không xung đột, thay thế
                    new_tkb[orig_index] = alt_lop
                    changed = True
                    break
        
        if changed:
            # Cập nhật TKB
            self.danh_sach_tkb_tim_duoc[self.current_tkb_index] = new_tkb
            self.show_tkb_at_index(self.current_tkb_index)
            self.log_message(f"Đã dồn lịch vào {'đầu' if pack_to_early else 'cuối'} tuần thành công!")
        else:
            QMessageBox.information(self, "Thông báo", 
                                  f"Không thể dồn lịch vào {'đầu' if pack_to_early else 'cuối'} tuần. "
                                  "Có thể do xung đột hoặc các lớp học đã ở vị trí tối ưu.")
    
    def handle_pack_early_week(self):
        """Dồn lịch học vào đầu tuần"""
        self._pack_schedule(pack_to_early=True)
    
    def handle_pack_late_week(self):
        """Dồn lịch học vào cuối tuần"""
        self._pack_schedule(pack_to_early=False)

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

