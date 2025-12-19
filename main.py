<<<<<<< HEAD
import sys, os, json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QListWidgetItem, QStackedWidget, QMessageBox, QFrame,
    QPushButton, QInputDialog, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor

# import tab yang sudah ada
from home import HomeTab
from tasks import TaskTab
from notes import NotesTab
from gpa import GPATab
from schedule import ScheduleTab


class StudentApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Direktori data
        if sys.platform.startswith('win'):
            app_data_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'StudentHelperPro_v1_2')
        elif sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
            app_data_dir = os.path.join(os.path.expanduser('~'), '.student_helper_pro_v1_2')
        else:
            app_data_dir = os.path.join(os.path.expanduser('~'), 'StudentHelperPro_v1_2')

        if not os.path.exists(app_data_dir):
            os.makedirs(app_data_dir)

        self.data_file = os.path.join(app_data_dir, "data.json")
        self.settings_file = os.path.join(app_data_dir, "settings.json")
        self.load_settings()

        self.setWindowTitle("Student Helper Pro")
        self.setGeometry(100, 100, 1400, 900)

        # ----------------------
        # Tema warna (ubah di sini kalau mau ganti tema)
        # ----------------------
        primary = "#4a90e2"          # warna utama (accent)
        primary_dark = "#357fc7"     # pressed
        primary_light = "#eaf4ff"    # hover / subtle bg
        bg_main = "#f5f6fa"          # background aplikasi
        card_bg = "#ffffff"          # kartu / panel bg
        card_border = "#e6eef9"      # warna border kartu
        muted_text = "#64748b"       # teks sekunder
        title_text = "#1e293b"       # teks utama
        button_bg = "#ffffff"        # default button bg
        button_hover = primary_light # hover bg untuk tombol
        # ----------------------

        # === Modern Theme stylesheet (consistent colors) ===
        self.setStyleSheet(f"""
            /* Window */
            QMainWindow {{
                background-color: {bg_main};
            }}

            /* Content panel (card) */
            QFrame#contentPanel {{
                background: {card_bg};
                border-radius: 16px;
                border: 1px solid {card_border};
            }}

            /* Summary cards and similar */
            QFrame[class="taskSummaryCard"] {{
                background: {card_bg};
                border: 1px solid {card_border};
                border-radius: 12px;
                padding: 12px;
            }}

            /* Lists */
            QListWidget {{
                background: {card_bg};
                border-radius: 12px;
                padding: 10px;
                font-size: 15px;
            }}
            QListWidget::item {{
                padding: 12px;
                margin: 4px 0;
                border-radius: 8px;
                color: {title_text};
            }}
            QListWidget::item:selected {{
                background: {primary};
                color: white;
            }}

            /* Buttons - default is outline style with accent text */
            QPushButton {{
                background-color: {button_bg};
                color: {primary};
                border: 1px solid {card_border};
                border-radius: 10px;
                padding: 8px 14px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {button_hover};
                color: {primary_dark};
            }}
            QPushButton:pressed {{
                background-color: {primary_dark};
                color: white;
            }}
            QPushButton:disabled {{
                color: #a0a0a0;
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
            }}

            /* Button variants you can set via setProperty("variant", "primary"/"ghost") */
            QPushButton[variant="primary"] {{
                background-color: {primary};
                color: white;
                border: none;
            }}
            QPushButton[variant="primary"]:hover {{
                background-color: {primary_dark};
            }}
            QPushButton[variant="ghost"] {{
                background: transparent;
                color: {primary};
                border: none;
            }}
            QPushButton[variant="ghost"]:hover {{
                background-color: rgba(74,144,226,0.06);
            }}

            /* Toolbar */
            QToolBar {{
                background: transparent;
                border: none;
            }}

            /* Titles and labels */
            QLabel#tabTitle {{
                font-size: 18px;
                font-weight: 600;
                color: {title_text};
            }}
            QLabel {{
                color: {muted_text};
            }}

            /* make content editor area obvious */
            QTextEdit#notesTextEditor {{
                background: transparent;
                border: 1px solid {card_border};
                border-radius: 10px;
                padding: 12px;
                color: {title_text};
            }}

            /* Sidebar frame safe styling */
            QFrame#sidebar {{
                background: transparent;
            }}
        """)

        central_widget = QWidget()
        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)

        # === Sidebar ===
        sidebar_frame = QFrame()
        sidebar_frame.setObjectName("sidebar")
        sidebar_frame.setFixedWidth(260)
        sidebar_layout = QVBoxLayout(sidebar_frame)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)

        self.sidebar = QListWidget()
        self.sidebar.setIconSize(QSize(20, 20))
        sidebar_layout.addWidget(self.sidebar, 1)
        self.add_sidebar_items()

        settings_about_layout = QVBoxLayout()
        self.settings_btn = QPushButton("⚙️ Pengaturan")
        self.settings_btn.clicked.connect(self.show_settings)
        # mark this as ghost (transparent) so it blends in as minor action
        self.settings_btn.setProperty("variant", "ghost")

        self.about_btn = QPushButton("ℹ️ Tentang Aplikasi")
        self.about_btn.clicked.connect(self.show_about_dialog)
        self.about_btn.setProperty("variant", "ghost")

        settings_about_layout.addWidget(self.settings_btn)
        settings_about_layout.addWidget(self.about_btn)
        sidebar_layout.addLayout(settings_about_layout)

        # === Content Panel ===
        content_panel = QFrame()
        content_panel.setObjectName("contentPanel")
        content_layout = QVBoxLayout(content_panel)
        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack)

        # Tambahkan efek shadow sekali saja
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 60))
        content_panel.setGraphicsEffect(shadow)

        # === Tabs ===
        self.task_tab = TaskTab(self.save_app_data, self.refresh_home_dashboard)
        self.notes_tab = NotesTab(self.save_app_data, self.refresh_home_dashboard)
        self.gpa_tab = GPATab(self.save_app_data, self.refresh_home_dashboard)
        self.schedule_tab = ScheduleTab(self)
        self.home_tab = HomeTab(self)

        for tab in [self.home_tab, self.task_tab, self.notes_tab, self.gpa_tab, self.schedule_tab]:
            self.stack.addWidget(tab)

        self.sidebar.currentRowChanged.connect(self.attempt_sidebar_change)

        self.main_layout.addWidget(sidebar_frame)
        self.main_layout.addWidget(content_panel, 1)
        self.setCentralWidget(central_widget)

        self.load_app_data()
        self.sidebar.setCurrentRow(0)

    # === fungsi lainnya tetap sama ===
    def refresh_home_dashboard(self):
        self.home_tab.refresh_dashboard()

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def attempt_sidebar_change(self, index):
        current_index = self.stack.currentIndex()
        if current_index == 2 and self.notes_tab.has_unsaved_changes and self.notes_tab.is_edit_mode:
            reply = QMessageBox.question(self, 'Perubahan Belum Disimpan',
                                         "Anda memiliki perubahan yang belum disimpan di tab Catatan. Keluar tanpa menyimpan?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                self.sidebar.blockSignals(True)
                self.sidebar.setCurrentRow(current_index)
                self.sidebar.blockSignals(False)
                return
        if current_index == 3 and self.gpa_tab.has_unsaved_changes:
            reply = QMessageBox.question(self, 'Perubahan Belum Disimpan',
                                         "Anda memiliki perubahan yang belum disimpan di tab IPK. Keluar tanpa menyimpan?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                self.sidebar.blockSignals(True)
                self.sidebar.setCurrentRow(current_index)
                self.sidebar.blockSignals(False)
                return
        self.stack.setCurrentIndex(index)
        if index == 0:
            self.refresh_home_dashboard()

    def show_settings(self):
        current_name = self.settings.get("user_name", "")
        text, ok = QInputDialog.getText(self, 'Pengaturan', 'Masukkan Nama Anda:', text=current_name)
        if ok and text:
            self.settings["user_name"] = text
            self.save_settings()
            self.refresh_home_dashboard()

    def show_about_dialog(self):
        QMessageBox.about(self, "Tentang Aplikasi",
                          "<b>Student Helper Pro</b><br><br>"
                          "Aplikasi ini dibuat untuk membantu mahasiswa mengelola tugas, catatan, dan nilai dengan lebih mudah.<br><br>"
                          "<b>Versi: 1.2</b><br>"
                          "<b>Pengembang:</b> Annaf Rehn<br>"
                          "<b>Copyright © 2025</b>")

    def add_sidebar_items(self):
        self.sidebar.addItem(QListWidgetItem("🏠 Beranda"))
        self.sidebar.addItem(QListWidgetItem("📝 Tugas"))
        self.sidebar.addItem(QListWidgetItem("📒 Catatan"))
        self.sidebar.addItem(QListWidgetItem("🎓 IPK"))
        self.sidebar.addItem(QListWidgetItem("🤖 Jadwal Cerdas"))

    def load_app_data(self):
        if not os.path.exists(self.data_file):
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump({"tasks": [], "notes": [], "gpa": {"courses": [], "system": "Sistem A, AB, B"}}, f, indent=2)
            return
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.task_tab.from_dict(data.get("tasks", []))
            self.notes_tab.from_dict(data.get("notes", []))
            self.gpa_tab.from_dict(data.get("gpa", {}))
        except Exception:
            QMessageBox.warning(self, "Error Data", "Gagal memuat data aplikasi.")
        self.refresh_home_dashboard()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    self.settings = json.load(f)
            except Exception:
                self.settings = {"user_name": "Mahasiswa"}
                self.save_settings()
        else:
            self.settings = {"user_name": "Mahasiswa"}
            self.save_settings()

    def save_app_data(self):
        data = {"tasks": self.task_tab.to_dict(), "notes": self.notes_tab.to_dict(), "gpa": self.gpa_tab.to_dict()}
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def save_settings(self):
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=2, ensure_ascii=False)

    def closeEvent(self, event):
        if self.notes_tab.has_unsaved_changes and self.notes_tab.is_edit_mode:
            reply = QMessageBox.question(self, 'Perubahan Belum Disimpan',
                                         "Anda memiliki perubahan yang belum disimpan di tab Catatan. Keluar tanpa menyimpan?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                event.ignore()
                return
        if self.gpa_tab.has_unsaved_changes:
            reply = QMessageBox.question(self, 'Perubahan Belum Disimpan',
                                         "Anda memiliki perubahan yang belum disimpan di tab IPK. Keluar tanpa menyimpan?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                event.ignore()
                return
        self.save_app_data()
        self.save_settings()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StudentApp()
    window.show()
    sys.exit(app.exec_())
=======
import sys, os, json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QListWidgetItem, QStackedWidget, QMessageBox, QFrame,
    QPushButton, QInputDialog, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor

# import tab yang sudah ada
from home import HomeTab
from tasks import TaskTab
from notes import NotesTab
from gpa import GPATab
from schedule import ScheduleTab


class StudentApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Direktori data
        if sys.platform.startswith('win'):
            app_data_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'StudentHelperPro_v1_2')
        elif sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
            app_data_dir = os.path.join(os.path.expanduser('~'), '.student_helper_pro_v1_2')
        else:
            app_data_dir = os.path.join(os.path.expanduser('~'), 'StudentHelperPro_v1_2')

        if not os.path.exists(app_data_dir):
            os.makedirs(app_data_dir)

        self.data_file = os.path.join(app_data_dir, "data.json")
        self.settings_file = os.path.join(app_data_dir, "settings.json")
        self.load_settings()

        self.setWindowTitle("Student Helper Pro")
        self.setGeometry(100, 100, 1400, 900)

        # ----------------------
        # Tema warna (ubah di sini kalau mau ganti tema)
        # ----------------------
        primary = "#4a90e2"          # warna utama (accent)
        primary_dark = "#357fc7"     # pressed
        primary_light = "#eaf4ff"    # hover / subtle bg
        bg_main = "#f5f6fa"          # background aplikasi
        card_bg = "#ffffff"          # kartu / panel bg
        card_border = "#e6eef9"      # warna border kartu
        muted_text = "#64748b"       # teks sekunder
        title_text = "#1e293b"       # teks utama
        button_bg = "#ffffff"        # default button bg
        button_hover = primary_light # hover bg untuk tombol
        # ----------------------

        # === Modern Theme stylesheet (consistent colors) ===
        self.setStyleSheet(f"""
            /* Window */
            QMainWindow {{
                background-color: {bg_main};
            }}

            /* Content panel (card) */
            QFrame#contentPanel {{
                background: {card_bg};
                border-radius: 16px;
                border: 1px solid {card_border};
            }}

            /* Summary cards and similar */
            QFrame[class="taskSummaryCard"] {{
                background: {card_bg};
                border: 1px solid {card_border};
                border-radius: 12px;
                padding: 12px;
            }}

            /* Lists */
            QListWidget {{
                background: {card_bg};
                border-radius: 12px;
                padding: 10px;
                font-size: 15px;
            }}
            QListWidget::item {{
                padding: 12px;
                margin: 4px 0;
                border-radius: 8px;
                color: {title_text};
            }}
            QListWidget::item:selected {{
                background: {primary};
                color: white;
            }}

            /* Buttons - default is outline style with accent text */
            QPushButton {{
                background-color: {button_bg};
                color: {primary};
                border: 1px solid {card_border};
                border-radius: 10px;
                padding: 8px 14px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {button_hover};
                color: {primary_dark};
            }}
            QPushButton:pressed {{
                background-color: {primary_dark};
                color: white;
            }}
            QPushButton:disabled {{
                color: #a0a0a0;
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
            }}

            /* Button variants you can set via setProperty("variant", "primary"/"ghost") */
            QPushButton[variant="primary"] {{
                background-color: {primary};
                color: white;
                border: none;
            }}
            QPushButton[variant="primary"]:hover {{
                background-color: {primary_dark};
            }}
            QPushButton[variant="ghost"] {{
                background: transparent;
                color: {primary};
                border: none;
            }}
            QPushButton[variant="ghost"]:hover {{
                background-color: rgba(74,144,226,0.06);
            }}

            /* Toolbar */
            QToolBar {{
                background: transparent;
                border: none;
            }}

            /* Titles and labels */
            QLabel#tabTitle {{
                font-size: 18px;
                font-weight: 600;
                color: {title_text};
            }}
            QLabel {{
                color: {muted_text};
            }}

            /* make content editor area obvious */
            QTextEdit#notesTextEditor {{
                background: transparent;
                border: 1px solid {card_border};
                border-radius: 10px;
                padding: 12px;
                color: {title_text};
            }}

            /* Sidebar frame safe styling */
            QFrame#sidebar {{
                background: transparent;
            }}
        """)

        central_widget = QWidget()
        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)

        # === Sidebar ===
        sidebar_frame = QFrame()
        sidebar_frame.setObjectName("sidebar")
        sidebar_frame.setFixedWidth(260)
        sidebar_layout = QVBoxLayout(sidebar_frame)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)

        self.sidebar = QListWidget()
        self.sidebar.setIconSize(QSize(20, 20))
        sidebar_layout.addWidget(self.sidebar, 1)
        self.add_sidebar_items()

        settings_about_layout = QVBoxLayout()
        self.settings_btn = QPushButton("⚙️ Pengaturan")
        self.settings_btn.clicked.connect(self.show_settings)
        # mark this as ghost (transparent) so it blends in as minor action
        self.settings_btn.setProperty("variant", "ghost")

        self.about_btn = QPushButton("ℹ️ Tentang Aplikasi")
        self.about_btn.clicked.connect(self.show_about_dialog)
        self.about_btn.setProperty("variant", "ghost")

        settings_about_layout.addWidget(self.settings_btn)
        settings_about_layout.addWidget(self.about_btn)
        sidebar_layout.addLayout(settings_about_layout)

        # === Content Panel ===
        content_panel = QFrame()
        content_panel.setObjectName("contentPanel")
        content_layout = QVBoxLayout(content_panel)
        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack)

        # Tambahkan efek shadow sekali saja
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 60))
        content_panel.setGraphicsEffect(shadow)

        # === Tabs ===
        self.task_tab = TaskTab(self.save_app_data, self.refresh_home_dashboard)
        self.notes_tab = NotesTab(self.save_app_data, self.refresh_home_dashboard)
        self.gpa_tab = GPATab(self.save_app_data, self.refresh_home_dashboard)
        self.schedule_tab = ScheduleTab(self)
        self.home_tab = HomeTab(self)

        for tab in [self.home_tab, self.task_tab, self.notes_tab, self.gpa_tab, self.schedule_tab]:
            self.stack.addWidget(tab)

        self.sidebar.currentRowChanged.connect(self.attempt_sidebar_change)

        self.main_layout.addWidget(sidebar_frame)
        self.main_layout.addWidget(content_panel, 1)
        self.setCentralWidget(central_widget)

        self.load_app_data()
        self.sidebar.setCurrentRow(0)

    # === fungsi lainnya tetap sama ===
    def refresh_home_dashboard(self):
        self.home_tab.refresh_dashboard()

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def attempt_sidebar_change(self, index):
        current_index = self.stack.currentIndex()
        if current_index == 2 and self.notes_tab.has_unsaved_changes and self.notes_tab.is_edit_mode:
            reply = QMessageBox.question(self, 'Perubahan Belum Disimpan',
                                         "Anda memiliki perubahan yang belum disimpan di tab Catatan. Keluar tanpa menyimpan?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                self.sidebar.blockSignals(True)
                self.sidebar.setCurrentRow(current_index)
                self.sidebar.blockSignals(False)
                return
        if current_index == 3 and self.gpa_tab.has_unsaved_changes:
            reply = QMessageBox.question(self, 'Perubahan Belum Disimpan',
                                         "Anda memiliki perubahan yang belum disimpan di tab IPK. Keluar tanpa menyimpan?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                self.sidebar.blockSignals(True)
                self.sidebar.setCurrentRow(current_index)
                self.sidebar.blockSignals(False)
                return
        self.stack.setCurrentIndex(index)
        if index == 0:
            self.refresh_home_dashboard()

    def show_settings(self):
        current_name = self.settings.get("user_name", "")
        text, ok = QInputDialog.getText(self, 'Pengaturan', 'Masukkan Nama Anda:', text=current_name)
        if ok and text:
            self.settings["user_name"] = text
            self.save_settings()
            self.refresh_home_dashboard()

    def show_about_dialog(self):
        QMessageBox.about(self, "Tentang Aplikasi",
                          "<b>Student Helper Pro</b><br><br>"
                          "Aplikasi ini dibuat untuk membantu mahasiswa mengelola tugas, catatan, dan nilai dengan lebih mudah.<br><br>"
                          "<b>Versi: 1.2</b><br>"
                          "<b>Pengembang:</b> Annaf Rehn<br>"
                          "<b>Copyright © 2025</b>")

    def add_sidebar_items(self):
        self.sidebar.addItem(QListWidgetItem("🏠 Beranda"))
        self.sidebar.addItem(QListWidgetItem("📝 Tugas"))
        self.sidebar.addItem(QListWidgetItem("📒 Catatan"))
        self.sidebar.addItem(QListWidgetItem("🎓 IPK"))
        self.sidebar.addItem(QListWidgetItem("🤖 Jadwal Cerdas"))

    def load_app_data(self):
        if not os.path.exists(self.data_file):
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump({"tasks": [], "notes": [], "gpa": {"courses": [], "system": "Sistem A, AB, B"}}, f, indent=2)
            return
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.task_tab.from_dict(data.get("tasks", []))
            self.notes_tab.from_dict(data.get("notes", []))
            self.gpa_tab.from_dict(data.get("gpa", {}))
        except Exception:
            QMessageBox.warning(self, "Error Data", "Gagal memuat data aplikasi.")
        self.refresh_home_dashboard()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    self.settings = json.load(f)
            except Exception:
                self.settings = {"user_name": "Mahasiswa"}
                self.save_settings()
        else:
            self.settings = {"user_name": "Mahasiswa"}
            self.save_settings()

    def save_app_data(self):
        data = {"tasks": self.task_tab.to_dict(), "notes": self.notes_tab.to_dict(), "gpa": self.gpa_tab.to_dict()}
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def save_settings(self):
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=2, ensure_ascii=False)

    def closeEvent(self, event):
        if self.notes_tab.has_unsaved_changes and self.notes_tab.is_edit_mode:
            reply = QMessageBox.question(self, 'Perubahan Belum Disimpan',
                                         "Anda memiliki perubahan yang belum disimpan di tab Catatan. Keluar tanpa menyimpan?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                event.ignore()
                return
        if self.gpa_tab.has_unsaved_changes:
            reply = QMessageBox.question(self, 'Perubahan Belum Disimpan',
                                         "Anda memiliki perubahan yang belum disimpan di tab IPK. Keluar tanpa menyimpan?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                event.ignore()
                return
        self.save_app_data()
        self.save_settings()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StudentApp()
    window.show()
    sys.exit(app.exec_())
>>>>>>> 6f8c74b61db7b91443edac1be989deeb72a66dd3
