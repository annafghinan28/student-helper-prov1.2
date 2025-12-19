<<<<<<< HEAD
import random
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QMessageBox, QFrame, QScrollArea, QFileDialog, QStackedWidget,
    QProgressBar, QCalendarWidget, QDateEdit, QTabWidget
)
from PyQt5.QtCore import Qt, QDateTime, QUrl, QTimer, QDate, QTime
from PyQt5.QtGui import QDesktopServices, QPainter, QPen, QColor
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class TimelineItem(QFrame):
    """Widget custom untuk menampilkan satu item jadwal dalam timeline."""
    def __init__(self, time, title, subtitle, icon, color, is_link=False):
        super().__init__()
        self.setProperty("class", "timelineItem")
        self.setCursor(Qt.PointingHandCursor if is_link else Qt.ArrowCursor)
        encoded_title = str(QUrl.toPercentEncoding(f"tutorial {title}"), 'utf-8')
        self.link = "https://www.google.com/search?q=" + encoded_title if is_link else None
        main_layout = QHBoxLayout(self)
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setProperty("class", "timelineIcon")
        icon_label.setStyleSheet(f"background-color: {color};")
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)
        time_label = QLabel(time)
        time_label.setStyleSheet("font-size: 12px; color: #64748b;")
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #1e293b;")
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("font-size: 13px; color: #475569;")
        subtitle_label.setWordWrap(True)
        content_layout.addWidget(time_label)
        content_layout.addWidget(title_label)
        content_layout.addWidget(subtitle_label)
        main_layout.addWidget(icon_label)
        main_layout.addLayout(content_layout, 1)

    def mousePressEvent(self, event):
        if self.link:
            QDesktopServices.openUrl(QUrl(self.link))

class ProductivityChart(QWidget):
    """Widget custom untuk menampilkan grafik distribusi waktu."""
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(150)
        self.study_time = 0
        self.break_time = 0
        self.has_data = False

    def set_data(self, study_time, break_time):
        self.study_time = study_time
        self.break_time = break_time
        self.has_data = True
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if not self.has_data:
            painter.setPen(QColor("#64748b"))
            painter.drawText(self.rect(), Qt.AlignCenter, "Buat jadwal dulu!")
            return
        total_time = self.study_time + self.break_time
        if total_time == 0:
            return
        width = self.width()
        height = self.height() - 20
        bar_width = width // 2 - 20
        study_height = (self.study_time / total_time) * height if total_time > 0 else 0
        painter.setBrush(QColor("#3b82f6"))
        painter.setPen(Qt.NoPen)
        painter.drawRect(20, height - int(study_height), bar_width, int(study_height))
        painter.setPen(QColor("#1e293b"))
        painter.drawText(20, height + 15, f"Belajar: {self.study_time} menit")
        break_height = (self.break_time / total_time) * height if total_time > 0 else 0
        painter.setBrush(QColor("#10b981"))
        painter.drawRect(bar_width + 40, height - int(break_height), bar_width, int(break_height))
        painter.drawText(bar_width + 40, height + 15, f"Istirahat: {self.break_time} menit")

class PomodoroInfoWidget(QWidget):
    """Widget custom untuk menampilkan informasi teknik Pomodoro."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "modernCard")
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        title = QLabel("<b>Teknik Pomodoro</b>")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; padding-bottom: 10px;")
        layout.addWidget(title)
        desc_frame = QFrame()
        desc_frame.setProperty("class", "modernCard")
        desc_layout = QVBoxLayout(desc_frame)
        desc_layout.setContentsMargins(10, 10, 10, 10)
        desc_label = QLabel(
            "Teknik Pomodoro adalah metode manajemen waktu yang meningkatkan produktivitas dengan membagi pekerjaan menjadi sesi fokus 25 menit diikuti istirahat singkat 5 menit, dengan istirahat panjang 15-30 menit setelah empat sesi untuk menjaga konsentrasi dan mencegah kelelahan."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("font-size: 13px; color: #475569; padding: 8px;")
        desc_layout.addWidget(desc_label)
        layout.addWidget(desc_frame)
        stats_frame = QFrame()
        stats_frame.setProperty("class", "modernCard")
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(10, 10, 10, 10)
        stats_layout.addWidget(QLabel("<b>Statistik Sesi:</b>"))
        self.focus_sessions_label = QLabel("Sesi Fokus: 0")
        self.break_sessions_label = QLabel("Sesi Istirahat: 0")
        stats_layout.addWidget(self.focus_sessions_label)
        stats_layout.addWidget(self.break_sessions_label)
        stats_layout.addStretch()
        layout.addWidget(stats_frame)
        tips_frame = QFrame()
        tips_frame.setProperty("class", "modernCard")
        tips_layout = QVBoxLayout(tips_frame)
        tips_layout.setContentsMargins(10, 10, 10, 10)
        tips_layout.addWidget(QLabel("<b>Tips Spesifik:</b>"))
        self.dynamic_tip_label = QLabel("Tips akan muncul setelah jadwal dibuat.")
        self.dynamic_tip_label.setWordWrap(True)
        self.dynamic_tip_label.setStyleSheet("font-size: 12px; color: #64748b; padding-top: 5px;")
        tips_layout.addWidget(self.dynamic_tip_label)
        layout.addWidget(tips_frame)
        layout.addStretch()

    def update_stats(self, focus_sessions, break_sessions):
        self.focus_sessions_label.setText(f"Sesi Fokus: {focus_sessions}")
        self.break_sessions_label.setText(f"Sesi Istirahat: {break_sessions}")

    def update_tip(self, tip_text):
        self.dynamic_tip_label.setText(tip_text)

class TaskTab(QWidget):
    """Minimal TaskTab class to store tasks for scheduling."""
    def __init__(self):
        super().__init__()
        self.tasks = [
            {"name": "Belajar Matematika", "deadline": "2025-09-23 12:00", "is_done": False},
            {"name": "Persiapan Presentasi", "deadline": "2025-09-24 15:00", "is_done": False},
            {"name": "Latihan Ujian Fisika", "deadline": "2025-09-22 09:00", "is_done": False}
        ]

    def to_dict(self):
        return self.tasks

class ScheduleTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.schedule_data = []
        self.progress = 0
        self.current_pomodoro_session = None
        self.pomodoro_seconds_left = 0
        self.is_pomodoro_running = False
        self.has_generated_schedule = False
        self.init_ai_data()
        self.init_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_pomodoro)
        self.urgent_timer = QTimer()
        self.urgent_timer.timeout.connect(self.check_urgent_tasks)
        self.urgent_timer.start(60000)

    def init_ai_data(self):
        self.quotes = [
            "Pendidikan adalah senjata paling ampuh yang bisa kamu gunakan untuk mengubah dunia. - Nelson Mandela",
            "Satu-satunya sumber pengetahuan adalah pengalaman. - Albert Einstein",
            "Jangan berhenti ketika lelah. Berhentilah ketika selesai.",
            "Masa depanmu diciptakan oleh apa yang kamu lakukan hari ini, bukan besok.",
            "Perjalanan seribu mil dimulai dengan satu langkah. - Lao Tzu"
        ]
        self.study_tips = {
            "default": [
                "Gunakan teknik Pomodoro: 50 menit fokus, 10 menit istirahat.",
                "Jauhkan ponsel dan gangguan lainnya saat sesi belajar.",
                "Pastikan kamu minum cukup air agar tetap terhidrasi.",
                "Buat ringkasan kecil setelah setiap sesi belajar untuk memperkuat ingatan."
            ],
            "ujian": [
                "Fokus pada latihan soal dari tahun-tahun sebelumnya.",
                "Buat peta konsep (mind map) untuk menghubungkan materi.",
                "Pastikan tidur yang cukup malam sebelum ujian agar otak segar."
            ],
            "presentasi": [
                "Latih presentasimu di depan cermin atau rekam dirimu sendiri.",
                "Pahami audiensmu dan sesuaikan bahasamu.",
                "Siapkan slide yang ringkas dan visual, jangan terlalu banyak teks."
            ],
            "proyek": [
                "Bagi proyek besar menjadi tugas-tugas kecil yang lebih mudah dikelola.",
                "Tetapkan deadline kecil untuk setiap bagian dari proyek.",
                "Jangan ragu untuk meminta feedback dari teman atau dosen."
            ]
        }

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        header_layout = QHBoxLayout()
        title_label = QLabel("Perencana Jadwal Cerdas")
        title_label.setObjectName("tabTitle")
        self.export_btn = QPushButton("📄 Ekspor Jadwal")
        self.export_btn.clicked.connect(self.export_schedule)
        self.export_btn.setEnabled(False)
        self.export_btn.setProperty("variant", "primary")  # Tombol utama, biru terisi
        self.reset_btn = QPushButton("🔄 Reset Jadwal")
        self.reset_btn.clicked.connect(self.reset_schedule)
        self.reset_btn.setEnabled(False)
        self.reset_btn.setProperty("variant", "secondary")  # Tombol sekunder, outline biru
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.export_btn)
        header_layout.addWidget(self.reset_btn)
        main_layout.addLayout(header_layout)
        control_frame = QFrame()
        control_frame.setProperty("class", "modernCard")
        control_layout = QHBoxLayout(control_frame)
        control_layout.addWidget(QLabel("Waktu fokus hari ini:"))
        self.hours_input = QComboBox()
        self.hours_input.addItems([f"{i} jam" for i in range(1, 11)])
        self.hours_input.setCurrentIndex(0)
        self.priority_input = QComboBox()
        self.priority_input.addItems(["Otomatis (berdasarkan deadline)", "Manual (tertinggi ke terendah)", "Manual (terendah ke tertinggi)"])
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.generate_btn = QPushButton("🤖 Buat Jadwal")
        self.generate_btn.clicked.connect(self.generate_schedule)
        self.generate_btn.setProperty("variant", "primary")  # Tombol utama, biru terisi
        control_layout.addWidget(self.hours_input)
        control_layout.addWidget(QLabel("Prioritas:"))
        control_layout.addWidget(self.priority_input)
        control_layout.addWidget(QLabel("Tanggal:"))
        control_layout.addWidget(self.date_input)
        control_layout.addWidget(self.generate_btn)
        control_layout.addStretch()
        main_layout.addWidget(control_frame)
        content_area_layout = QHBoxLayout()
        content_area_layout.setSpacing(20)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.timeline_container = QStackedWidget()
        self.timeline_content_widget = QWidget()
        self.timeline_layout = QVBoxLayout(self.timeline_content_widget)
        self.timeline_layout.setAlignment(Qt.AlignTop)
        self.timeline_container.addWidget(self.timeline_content_widget)
        self.pomodoro_info_widget = PomodoroInfoWidget()
        self.timeline_container.addWidget(self.pomodoro_info_widget)
        scroll_area.setWidget(self.timeline_container)
        content_area_layout.addWidget(scroll_area, 2)
        ai_panel = QFrame()
        ai_panel.setProperty("class", "modernCard")
        ai_layout = QVBoxLayout(ai_panel)
        ai_layout.setSpacing(15)
        pomodoro_timer_section = QFrame()
        pomodoro_timer_section.setProperty("class", "modernCard")
        pomodoro_timer_layout = QVBoxLayout(pomodoro_timer_section)
        pomodoro_timer_layout.addWidget(QLabel("<b>Pomodoro Timer</b>"))
        self.pomodoro_label = QLabel("25:00")
        self.pomodoro_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b;")
        self.pomodoro_label.setAlignment(Qt.AlignCenter)
        pomodoro_timer_layout.addWidget(self.pomodoro_label)
        pomodoro_buttons_layout = QHBoxLayout()
        self.start_pomodoro_btn = QPushButton("▶ Mulai")
        self.start_pomodoro_btn.clicked.connect(self.start_pomodoro)
        self.start_pomodoro_btn.setEnabled(False)
        self.start_pomodoro_btn.setProperty("variant", "primary")  # Tombol utama, biru terisi
        self.pause_pomodoro_btn = QPushButton("⏸ Jeda")
        self.pause_pomodoro_btn.clicked.connect(self.pause_pomodoro)
        self.pause_pomodoro_btn.setEnabled(False)
        self.pause_pomodoro_btn.setProperty("variant", "secondary")  # Tombol sekunder, outline biru
        self.reset_pomodoro_btn = QPushButton("🔄 Reset")
        self.reset_pomodoro_btn.clicked.connect(self.reset_pomodoro)
        self.reset_pomodoro_btn.setEnabled(False)
        self.reset_pomodoro_btn.setProperty("variant", "secondary")  # Tombol sekunder, outline biru
        pomodoro_buttons_layout.addWidget(self.start_pomodoro_btn)
        pomodoro_buttons_layout.addWidget(self.pause_pomodoro_btn)
        pomodoro_buttons_layout.addWidget(self.reset_pomodoro_btn)
        pomodoro_timer_layout.addLayout(pomodoro_buttons_layout)
        ai_layout.addWidget(pomodoro_timer_section)
        progress_section = QFrame()
        progress_section.setProperty("class", "modernCard")
        progress_layout = QVBoxLayout(progress_section)
        progress_layout.addWidget(QLabel("<b>Progress Harian</b>"))
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("QProgressBar { border: 1px solid #e6eef9; border-radius: 4px; text-align: center; } QProgressBar::chunk { background: #4a90e2; border-radius: 4px; }")
        self.progress_label = QLabel("0/0 sesi selesai (0%)")
        self.progress_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)
        ai_layout.addWidget(progress_section)
        chart_section = QFrame()
        chart_section.setProperty("class", "modernCard")
        chart_layout = QVBoxLayout(chart_section)
        chart_layout.addWidget(QLabel("<b>Distribusi Waktu</b>"))
        self.productivity_chart = ProductivityChart()
        chart_layout.addWidget(self.productivity_chart)
        ai_layout.addWidget(chart_section)
        calendar_section = QFrame()
        calendar_section.setProperty("class", "modernCard")
        calendar_layout = QVBoxLayout(calendar_section)
        calendar_layout.addWidget(QLabel("<b>Kalender Harian</b>"))
        self.calendar = QCalendarWidget()
        self.calendar.setSelectedDate(QDate.currentDate())
        self.calendar.selectionChanged.connect(self.display_schedule)
        calendar_layout.addWidget(self.calendar)
        ai_layout.addWidget(calendar_section)
        self.urgent_tasks_label = QLabel("Tugas mendesak: 0")
        self.urgent_tasks_label.setAlignment(Qt.AlignCenter)
        ai_layout.addWidget(self.urgent_tasks_label)
        ai_layout.addWidget(QLabel("<b>Kutipan Motivasi</b>"))
        self.quote_label = QLabel(random.choice(self.quotes))
        self.quote_label.setWordWrap(True)
        self.quote_label.setStyleSheet("font-style: italic; color: #475569;")
        ai_layout.addWidget(self.quote_label)
        ai_layout.addStretch()
        content_area_layout.addWidget(ai_panel, 1)
        main_layout.addLayout(content_area_layout, 1)
        self.display_schedule()

    def start_pomodoro(self):
        if not self.schedule_data or self.is_pomodoro_running:
            return
        study_sessions = [item for item in self.schedule_data if item['type'] == 'study']
        if not study_sessions:
            return
        self.current_pomodoro_session = study_sessions[self.progress]
        if self.pomodoro_seconds_left == 0:
            self.pomodoro_seconds_left = 25 * 60
        self.is_pomodoro_running = True
        self.start_pomodoro_btn.setEnabled(False)
        self.pause_pomodoro_btn.setEnabled(True)
        self.reset_pomodoro_btn.setEnabled(True)
        self.timer.start(1000)
        self.update_pomodoro_label()

    def pause_pomodoro(self):
        if self.is_pomodoro_running:
            self.is_pomodoro_running = False
            self.timer.stop()
            self.start_pomodoro_btn.setText("▶ Lanjut")
            self.start_pomodoro_btn.setEnabled(True)
            self.pause_pomodoro_btn.setEnabled(False)
            self.reset_pomodoro_btn.setEnabled(True)

    def reset_pomodoro(self):
        self.is_pomodoro_running = False
        self.timer.stop()
        self.pomodoro_seconds_left = 0
        self.current_pomodoro_session = None
        self.start_pomodoro_btn.setText("▶ Mulai")
        self.start_pomodoro_btn.setEnabled(True)
        self.pause_pomodoro_btn.setEnabled(False)
        self.reset_pomodoro_btn.setEnabled(False)
        self.update_pomodoro_label()

    def update_pomodoro(self):
        if self.pomodoro_seconds_left > 0 and self.is_pomodoro_running:
            self.pomodoro_seconds_left -= 1
            self.update_pomodoro_label()
            if self.pomodoro_seconds_left == 0:
                self.is_pomodoro_running = False
                self.timer.stop()
                self.progress += 1
                self.update_progress_display()
                self.update_pomodoro_stats()
                QMessageBox.information(self, "Selesai", "Sesi Pomodoro selesai! Ambil istirahat 5 menit.")
                self.start_pomodoro_btn.setText("▶ Mulai")
                self.start_pomodoro_btn.setEnabled(True)
                self.pause_pomodoro_btn.setEnabled(False)
                self.reset_pomodoro_btn.setEnabled(False)
                if self.progress < len([item for item in self.schedule_data if item['type'] == 'study']):
                    self.current_pomodoro_session = None
                    self.pomodoro_seconds_left = 0
                else:
                    QMessageBox.information(self, "Sukses", "Semua sesi belajar hari ini selesai!")
        else:
            self.is_pomodoro_running = False
            self.timer.stop()

    def update_pomodoro_label(self):
        minutes = self.pomodoro_seconds_left // 60
        seconds = self.pomodoro_seconds_left % 60
        self.pomodoro_label.setText(f"{minutes:02d}:{seconds:02d}")

    def update_progress_display(self):
        if self.schedule_data:
            total_sessions = sum(1 for item in self.schedule_data if item['type'] == 'study')
            self.progress_bar.setMaximum(total_sessions)
            self.progress_bar.setValue(self.progress)
            self.progress_label.setText(f"{self.progress}/{total_sessions} sesi selesai ({int((self.progress / total_sessions) * 100) if total_sessions > 0 else 0}%)")

    def update_pomodoro_stats(self):
        if self.schedule_data:
            total_study_sessions = sum(1 for item in self.schedule_data if item['type'] == 'study')
            total_break_sessions = sum(1 for item in self.schedule_data if item['type'] == 'break')
            self.pomodoro_info_widget.update_stats(self.progress, max(0, self.progress - 1))

    def check_urgent_tasks(self):
        tasks = [t for t in self.main_window.task_tab.to_dict() if not t['is_done']]
        urgent_tasks = sum(1 for t in tasks if QDateTime.fromString(t['deadline'], "yyyy-MM-dd HH:mm") < QDateTime.currentDateTime().addDays(2))
        self.urgent_tasks_label.setText(f"Tugas mendesak: {urgent_tasks}")
        if urgent_tasks > 0 and not self.is_pomodoro_running:
            QMessageBox.warning(self, "Peringatan", f"Ada {urgent_tasks} tugas mendesak! Prioritaskan dalam jadwal Anda.")

    def generate_schedule(self):
        tasks = [t for t in self.main_window.task_tab.to_dict() if not t['is_done']]
        if not tasks:
            QMessageBox.information(self, "Informasi", "Tidak ada tugas aktif untuk dijadwalkan!")
            return
        priority_mode = self.priority_input.currentText()
        def get_priority(task, index):
            name = task['name'].lower()
            deadline = QDateTime.fromString(task['deadline'], "yyyy-MM-dd HH:mm")
            days_left = QDateTime.currentDateTime().daysTo(deadline)
            if priority_mode == "Otomatis (berdasarkan deadline)":
                if "ujian" in name or "final" in name:
                    return 0 + days_left
                if "presentasi" in name or "proyek" in name:
                    return 100 + days_left
                if "kuis" in name or "laporan" in name:
                    return 200 + days_left
                return 300 + days_left
            elif priority_mode == "Manual (tertinggi ke terendah)":
                return index
            else:
                return -index
        tasks = [(task, i) for i, task in enumerate(tasks)]
        tasks.sort(key=lambda x: get_priority(x[0], x[1]))
        tasks = [task for task, _ in tasks]
        selected_hours_str = self.hours_input.currentText()
        selected_hours = int(selected_hours_str.split(' ')[0])
        total_minutes = selected_hours * 60
        selected_date = self.date_input.date()
        schedule = []
        current_time = QDateTime(selected_date, QTime(8, 0))
        task_index = 0
        session_count = {}
        if len(tasks) == 1:
            while total_minutes >= 50:
                session_count.setdefault(tasks[0]['name'], 0)
                session_count[tasks[0]['name']] += 1
                start = current_time
                end = start.addSecs(50 * 60)
                schedule.append({
                    "time": f"{start.toString('hh:mm')} - {end.toString('hh:mm')}",
                    "title": f"Fokus: {tasks[0]['name']}",
                    "subtitle": f"Sesi Belajar Produktif: Bagian {session_count[tasks[0]['name']]}",
                    "icon": "📚",
                    "color": "#3b82f6",
                    "type": "study"
                })
                current_time = end
                total_minutes -= 50
                if total_minutes >= 10:
                    start = current_time
                    end = start.addSecs(10 * 60)
                    schedule.append({
                        "time": f"{start.toString('hh:mm')} - {end.toString('hh:mm')}",
                        "title": "Istirahat Singkat",
                        "subtitle": "Regangkan badan atau minum air.",
                        "icon": "☕",
                        "color": "#10b981",
                        "type": "break"
                    })
                    current_time = end
                    total_minutes -= 10
        else:
            while total_minutes >= 50 and task_index < len(tasks):
                start = current_time
                end = start.addSecs(50 * 60)
                schedule.append({
                    "time": f"{start.toString('hh:mm')} - {end.toString('hh:mm')}",
                    "title": f"Fokus: {tasks[task_index]['name']}",
                    "subtitle": "Sesi Belajar Produktif",
                    "icon": "📚",
                    "color": "#3b82f6",
                    "type": "study"
                })
                current_time = end
                total_minutes -= 50
                task_index += 1
                if total_minutes >= 10:
                    start = current_time
                    end = start.addSecs(10 * 60)
                    schedule.append({
                        "time": f"{start.toString('hh:mm')} - {end.toString('hh:mm')}",
                        "title": "Istirahat Singkat",
                        "subtitle": "Regangkan badan atau minum air.",
                        "icon": "☕",
                        "color": "#10b981",
                        "type": "break"
                    })
                    current_time = end
                    total_minutes -= 10
        self.schedule_data = schedule
        self.progress = 0
        self.reset_pomodoro()
        self.update_progress_display()
        self.update_productivity_chart()
        self.display_schedule()
        self.update_ai_insights(tasks)
        self.update_pomodoro_stats()
        self.update_dynamic_tips()
        self.has_generated_schedule = True
        self.export_btn.setEnabled(True)
        self.reset_btn.setEnabled(True)
        self.start_pomodoro_btn.setEnabled(True)
        self.pause_pomodoro_btn.setEnabled(False)
        self.reset_pomodoro_btn.setEnabled(True)

    def reset_schedule(self):
        reply = QMessageBox.question(self, "Konfirmasi Reset", "Apakah Anda yakin ingin mereset jadwal ke setelan awal?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.schedule_data = []
            self.progress = 0
            self.has_generated_schedule = False
            self.reset_pomodoro()
            self.update_progress_display()
            self.productivity_chart.has_data = False
            self.productivity_chart.update()
            self.display_schedule()
            self.update_pomodoro_stats()
            self.update_dynamic_tips()
            self.export_btn.setEnabled(False)
            self.reset_btn.setEnabled(False)
            self.start_pomodoro_btn.setEnabled(False)
            self.pause_pomodoro_btn.setEnabled(False)
            self.reset_pomodoro_btn.setEnabled(False)

    def update_productivity_chart(self):
        study_time = sum(50 for item in self.schedule_data if item['type'] == 'study')
        break_time = sum(10 for item in self.schedule_data if item['type'] == 'break')
        self.productivity_chart.set_data(study_time, break_time)

    def display_schedule(self):
        while self.timeline_layout.count():
            self.timeline_layout.takeAt(0).widget().deleteLater()
        selected_date = self.calendar.selectedDate()
        if not self.schedule_data or selected_date != self.date_input.date():
            self.export_btn.setEnabled(False)
            self.timeline_container.setCurrentIndex(1)
            return
        for item in self.schedule_data:
            timeline_item = TimelineItem(item["time"], item["title"], item["subtitle"], item["icon"], item["color"], is_link=item['type'] == 'study')
            self.timeline_layout.addWidget(timeline_item)
        self.export_btn.setEnabled(True)
        self.timeline_container.setCurrentIndex(0)

    def update_ai_insights(self, tasks):
        self.quote_label.setText(random.choice(self.quotes))
        self.check_urgent_tasks()

    def update_dynamic_tips(self):
        if self.schedule_data:
            current_task = self.schedule_data[self.progress]['title'].split("Fokus: ")[1].lower() if self.progress < len(self.schedule_data) else ""
            tip_found = False
            for keyword, tips in self.study_tips.items():
                if keyword != "default" and keyword in current_task:
                    self.pomodoro_info_widget.update_tip(random.choice(tips))
                    tip_found = True
                    break
            if not tip_found:
                self.pomodoro_info_widget.update_tip(random.choice(self.study_tips["default"]))
        else:
            self.pomodoro_info_widget.update_tip("Tips akan muncul setelah jadwal dibuat.")

    def export_schedule(self):
        if not self.schedule_data:
            QMessageBox.warning(self, "Gagal", "Tidak ada jadwal untuk diekspor.")
            return
        fileName, _ = QFileDialog.getSaveFileName(self, "Simpan Jadwal", "JadwalBelajar.pdf", "PDF Files (*.pdf)")
        if not fileName:
            return
        if not fileName.endswith('.pdf'):
            fileName += '.pdf'
        pdf = SimpleDocTemplate(fileName, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=12,
            alignment=1
        )
        date_style = ParagraphStyle(
            'Date',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=12,
            alignment=1
        )
        elements.append(Paragraph("Jadwal Belajar Harian", title_style))
        elements.append(Paragraph(f"Dibuat pada {QDateTime.currentDateTime().toString('dd MMMM yyyy, hh:mm')}", date_style))
        data = [["Waktu", "Aktivitas", "Detail"]]
        for item in self.schedule_data:
            data.append([item["time"], item["title"], item["subtitle"]])
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(table)
        pdf.build(elements)
        QMessageBox.information(self, "Sukses", f"Jadwal berhasil diekspor ke:\n{fileName}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplikasi Perencana Jadwal")
        self.setGeometry(100, 100, 1000, 600)
        self.task_tab = TaskTab()
        self.schedule_tab = ScheduleTab(self)
        tabs = QTabWidget()
        tabs.addTab(self.task_tab, "Tugas")
        tabs.addTab(self.schedule_tab, "Jadwal")
        self.setCentralWidget(tabs)

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
=======
import random
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QMessageBox, QFrame, QScrollArea, QFileDialog, QStackedWidget,
    QProgressBar, QCalendarWidget, QDateEdit, QTabWidget
)
from PyQt5.QtCore import Qt, QDateTime, QUrl, QTimer, QDate, QTime
from PyQt5.QtGui import QDesktopServices, QPainter, QPen, QColor
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class TimelineItem(QFrame):
    """Widget custom untuk menampilkan satu item jadwal dalam timeline."""
    def __init__(self, time, title, subtitle, icon, color, is_link=False):
        super().__init__()
        self.setProperty("class", "timelineItem")
        self.setCursor(Qt.PointingHandCursor if is_link else Qt.ArrowCursor)
        encoded_title = str(QUrl.toPercentEncoding(f"tutorial {title}"), 'utf-8')
        self.link = "https://www.google.com/search?q=" + encoded_title if is_link else None
        main_layout = QHBoxLayout(self)
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setProperty("class", "timelineIcon")
        icon_label.setStyleSheet(f"background-color: {color};")
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)
        time_label = QLabel(time)
        time_label.setStyleSheet("font-size: 12px; color: #64748b;")
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #1e293b;")
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("font-size: 13px; color: #475569;")
        subtitle_label.setWordWrap(True)
        content_layout.addWidget(time_label)
        content_layout.addWidget(title_label)
        content_layout.addWidget(subtitle_label)
        main_layout.addWidget(icon_label)
        main_layout.addLayout(content_layout, 1)

    def mousePressEvent(self, event):
        if self.link:
            QDesktopServices.openUrl(QUrl(self.link))

class ProductivityChart(QWidget):
    """Widget custom untuk menampilkan grafik distribusi waktu."""
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(150)
        self.study_time = 0
        self.break_time = 0
        self.has_data = False

    def set_data(self, study_time, break_time):
        self.study_time = study_time
        self.break_time = break_time
        self.has_data = True
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if not self.has_data:
            painter.setPen(QColor("#64748b"))
            painter.drawText(self.rect(), Qt.AlignCenter, "Buat jadwal dulu!")
            return
        total_time = self.study_time + self.break_time
        if total_time == 0:
            return
        width = self.width()
        height = self.height() - 20
        bar_width = width // 2 - 20
        study_height = (self.study_time / total_time) * height if total_time > 0 else 0
        painter.setBrush(QColor("#3b82f6"))
        painter.setPen(Qt.NoPen)
        painter.drawRect(20, height - int(study_height), bar_width, int(study_height))
        painter.setPen(QColor("#1e293b"))
        painter.drawText(20, height + 15, f"Belajar: {self.study_time} menit")
        break_height = (self.break_time / total_time) * height if total_time > 0 else 0
        painter.setBrush(QColor("#10b981"))
        painter.drawRect(bar_width + 40, height - int(break_height), bar_width, int(break_height))
        painter.drawText(bar_width + 40, height + 15, f"Istirahat: {self.break_time} menit")

class PomodoroInfoWidget(QWidget):
    """Widget custom untuk menampilkan informasi teknik Pomodoro."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "modernCard")
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        title = QLabel("<b>Teknik Pomodoro</b>")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; padding-bottom: 10px;")
        layout.addWidget(title)
        desc_frame = QFrame()
        desc_frame.setProperty("class", "modernCard")
        desc_layout = QVBoxLayout(desc_frame)
        desc_layout.setContentsMargins(10, 10, 10, 10)
        desc_label = QLabel(
            "Teknik Pomodoro adalah metode manajemen waktu yang meningkatkan produktivitas dengan membagi pekerjaan menjadi sesi fokus 25 menit diikuti istirahat singkat 5 menit, dengan istirahat panjang 15-30 menit setelah empat sesi untuk menjaga konsentrasi dan mencegah kelelahan."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("font-size: 13px; color: #475569; padding: 8px;")
        desc_layout.addWidget(desc_label)
        layout.addWidget(desc_frame)
        stats_frame = QFrame()
        stats_frame.setProperty("class", "modernCard")
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(10, 10, 10, 10)
        stats_layout.addWidget(QLabel("<b>Statistik Sesi:</b>"))
        self.focus_sessions_label = QLabel("Sesi Fokus: 0")
        self.break_sessions_label = QLabel("Sesi Istirahat: 0")
        stats_layout.addWidget(self.focus_sessions_label)
        stats_layout.addWidget(self.break_sessions_label)
        stats_layout.addStretch()
        layout.addWidget(stats_frame)
        tips_frame = QFrame()
        tips_frame.setProperty("class", "modernCard")
        tips_layout = QVBoxLayout(tips_frame)
        tips_layout.setContentsMargins(10, 10, 10, 10)
        tips_layout.addWidget(QLabel("<b>Tips Spesifik:</b>"))
        self.dynamic_tip_label = QLabel("Tips akan muncul setelah jadwal dibuat.")
        self.dynamic_tip_label.setWordWrap(True)
        self.dynamic_tip_label.setStyleSheet("font-size: 12px; color: #64748b; padding-top: 5px;")
        tips_layout.addWidget(self.dynamic_tip_label)
        layout.addWidget(tips_frame)
        layout.addStretch()

    def update_stats(self, focus_sessions, break_sessions):
        self.focus_sessions_label.setText(f"Sesi Fokus: {focus_sessions}")
        self.break_sessions_label.setText(f"Sesi Istirahat: {break_sessions}")

    def update_tip(self, tip_text):
        self.dynamic_tip_label.setText(tip_text)

class TaskTab(QWidget):
    """Minimal TaskTab class to store tasks for scheduling."""
    def __init__(self):
        super().__init__()
        self.tasks = [
            {"name": "Belajar Matematika", "deadline": "2025-09-23 12:00", "is_done": False},
            {"name": "Persiapan Presentasi", "deadline": "2025-09-24 15:00", "is_done": False},
            {"name": "Latihan Ujian Fisika", "deadline": "2025-09-22 09:00", "is_done": False}
        ]

    def to_dict(self):
        return self.tasks

class ScheduleTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.schedule_data = []
        self.progress = 0
        self.current_pomodoro_session = None
        self.pomodoro_seconds_left = 0
        self.is_pomodoro_running = False
        self.has_generated_schedule = False
        self.init_ai_data()
        self.init_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_pomodoro)
        self.urgent_timer = QTimer()
        self.urgent_timer.timeout.connect(self.check_urgent_tasks)
        self.urgent_timer.start(60000)

    def init_ai_data(self):
        self.quotes = [
            "Pendidikan adalah senjata paling ampuh yang bisa kamu gunakan untuk mengubah dunia. - Nelson Mandela",
            "Satu-satunya sumber pengetahuan adalah pengalaman. - Albert Einstein",
            "Jangan berhenti ketika lelah. Berhentilah ketika selesai.",
            "Masa depanmu diciptakan oleh apa yang kamu lakukan hari ini, bukan besok.",
            "Perjalanan seribu mil dimulai dengan satu langkah. - Lao Tzu"
        ]
        self.study_tips = {
            "default": [
                "Gunakan teknik Pomodoro: 50 menit fokus, 10 menit istirahat.",
                "Jauhkan ponsel dan gangguan lainnya saat sesi belajar.",
                "Pastikan kamu minum cukup air agar tetap terhidrasi.",
                "Buat ringkasan kecil setelah setiap sesi belajar untuk memperkuat ingatan."
            ],
            "ujian": [
                "Fokus pada latihan soal dari tahun-tahun sebelumnya.",
                "Buat peta konsep (mind map) untuk menghubungkan materi.",
                "Pastikan tidur yang cukup malam sebelum ujian agar otak segar."
            ],
            "presentasi": [
                "Latih presentasimu di depan cermin atau rekam dirimu sendiri.",
                "Pahami audiensmu dan sesuaikan bahasamu.",
                "Siapkan slide yang ringkas dan visual, jangan terlalu banyak teks."
            ],
            "proyek": [
                "Bagi proyek besar menjadi tugas-tugas kecil yang lebih mudah dikelola.",
                "Tetapkan deadline kecil untuk setiap bagian dari proyek.",
                "Jangan ragu untuk meminta feedback dari teman atau dosen."
            ]
        }

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        header_layout = QHBoxLayout()
        title_label = QLabel("Perencana Jadwal Cerdas")
        title_label.setObjectName("tabTitle")
        self.export_btn = QPushButton("📄 Ekspor Jadwal")
        self.export_btn.clicked.connect(self.export_schedule)
        self.export_btn.setEnabled(False)
        self.export_btn.setProperty("variant", "primary")  # Tombol utama, biru terisi
        self.reset_btn = QPushButton("🔄 Reset Jadwal")
        self.reset_btn.clicked.connect(self.reset_schedule)
        self.reset_btn.setEnabled(False)
        self.reset_btn.setProperty("variant", "secondary")  # Tombol sekunder, outline biru
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.export_btn)
        header_layout.addWidget(self.reset_btn)
        main_layout.addLayout(header_layout)
        control_frame = QFrame()
        control_frame.setProperty("class", "modernCard")
        control_layout = QHBoxLayout(control_frame)
        control_layout.addWidget(QLabel("Waktu fokus hari ini:"))
        self.hours_input = QComboBox()
        self.hours_input.addItems([f"{i} jam" for i in range(1, 11)])
        self.hours_input.setCurrentIndex(0)
        self.priority_input = QComboBox()
        self.priority_input.addItems(["Otomatis (berdasarkan deadline)", "Manual (tertinggi ke terendah)", "Manual (terendah ke tertinggi)"])
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.generate_btn = QPushButton("🤖 Buat Jadwal")
        self.generate_btn.clicked.connect(self.generate_schedule)
        self.generate_btn.setProperty("variant", "primary")  # Tombol utama, biru terisi
        control_layout.addWidget(self.hours_input)
        control_layout.addWidget(QLabel("Prioritas:"))
        control_layout.addWidget(self.priority_input)
        control_layout.addWidget(QLabel("Tanggal:"))
        control_layout.addWidget(self.date_input)
        control_layout.addWidget(self.generate_btn)
        control_layout.addStretch()
        main_layout.addWidget(control_frame)
        content_area_layout = QHBoxLayout()
        content_area_layout.setSpacing(20)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.timeline_container = QStackedWidget()
        self.timeline_content_widget = QWidget()
        self.timeline_layout = QVBoxLayout(self.timeline_content_widget)
        self.timeline_layout.setAlignment(Qt.AlignTop)
        self.timeline_container.addWidget(self.timeline_content_widget)
        self.pomodoro_info_widget = PomodoroInfoWidget()
        self.timeline_container.addWidget(self.pomodoro_info_widget)
        scroll_area.setWidget(self.timeline_container)
        content_area_layout.addWidget(scroll_area, 2)
        ai_panel = QFrame()
        ai_panel.setProperty("class", "modernCard")
        ai_layout = QVBoxLayout(ai_panel)
        ai_layout.setSpacing(15)
        pomodoro_timer_section = QFrame()
        pomodoro_timer_section.setProperty("class", "modernCard")
        pomodoro_timer_layout = QVBoxLayout(pomodoro_timer_section)
        pomodoro_timer_layout.addWidget(QLabel("<b>Pomodoro Timer</b>"))
        self.pomodoro_label = QLabel("25:00")
        self.pomodoro_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b;")
        self.pomodoro_label.setAlignment(Qt.AlignCenter)
        pomodoro_timer_layout.addWidget(self.pomodoro_label)
        pomodoro_buttons_layout = QHBoxLayout()
        self.start_pomodoro_btn = QPushButton("▶ Mulai")
        self.start_pomodoro_btn.clicked.connect(self.start_pomodoro)
        self.start_pomodoro_btn.setEnabled(False)
        self.start_pomodoro_btn.setProperty("variant", "primary")  # Tombol utama, biru terisi
        self.pause_pomodoro_btn = QPushButton("⏸ Jeda")
        self.pause_pomodoro_btn.clicked.connect(self.pause_pomodoro)
        self.pause_pomodoro_btn.setEnabled(False)
        self.pause_pomodoro_btn.setProperty("variant", "secondary")  # Tombol sekunder, outline biru
        self.reset_pomodoro_btn = QPushButton("🔄 Reset")
        self.reset_pomodoro_btn.clicked.connect(self.reset_pomodoro)
        self.reset_pomodoro_btn.setEnabled(False)
        self.reset_pomodoro_btn.setProperty("variant", "secondary")  # Tombol sekunder, outline biru
        pomodoro_buttons_layout.addWidget(self.start_pomodoro_btn)
        pomodoro_buttons_layout.addWidget(self.pause_pomodoro_btn)
        pomodoro_buttons_layout.addWidget(self.reset_pomodoro_btn)
        pomodoro_timer_layout.addLayout(pomodoro_buttons_layout)
        ai_layout.addWidget(pomodoro_timer_section)
        progress_section = QFrame()
        progress_section.setProperty("class", "modernCard")
        progress_layout = QVBoxLayout(progress_section)
        progress_layout.addWidget(QLabel("<b>Progress Harian</b>"))
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("QProgressBar { border: 1px solid #e6eef9; border-radius: 4px; text-align: center; } QProgressBar::chunk { background: #4a90e2; border-radius: 4px; }")
        self.progress_label = QLabel("0/0 sesi selesai (0%)")
        self.progress_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)
        ai_layout.addWidget(progress_section)
        chart_section = QFrame()
        chart_section.setProperty("class", "modernCard")
        chart_layout = QVBoxLayout(chart_section)
        chart_layout.addWidget(QLabel("<b>Distribusi Waktu</b>"))
        self.productivity_chart = ProductivityChart()
        chart_layout.addWidget(self.productivity_chart)
        ai_layout.addWidget(chart_section)
        calendar_section = QFrame()
        calendar_section.setProperty("class", "modernCard")
        calendar_layout = QVBoxLayout(calendar_section)
        calendar_layout.addWidget(QLabel("<b>Kalender Harian</b>"))
        self.calendar = QCalendarWidget()
        self.calendar.setSelectedDate(QDate.currentDate())
        self.calendar.selectionChanged.connect(self.display_schedule)
        calendar_layout.addWidget(self.calendar)
        ai_layout.addWidget(calendar_section)
        self.urgent_tasks_label = QLabel("Tugas mendesak: 0")
        self.urgent_tasks_label.setAlignment(Qt.AlignCenter)
        ai_layout.addWidget(self.urgent_tasks_label)
        ai_layout.addWidget(QLabel("<b>Kutipan Motivasi</b>"))
        self.quote_label = QLabel(random.choice(self.quotes))
        self.quote_label.setWordWrap(True)
        self.quote_label.setStyleSheet("font-style: italic; color: #475569;")
        ai_layout.addWidget(self.quote_label)
        ai_layout.addStretch()
        content_area_layout.addWidget(ai_panel, 1)
        main_layout.addLayout(content_area_layout, 1)
        self.display_schedule()

    def start_pomodoro(self):
        if not self.schedule_data or self.is_pomodoro_running:
            return
        study_sessions = [item for item in self.schedule_data if item['type'] == 'study']
        if not study_sessions:
            return
        self.current_pomodoro_session = study_sessions[self.progress]
        if self.pomodoro_seconds_left == 0:
            self.pomodoro_seconds_left = 25 * 60
        self.is_pomodoro_running = True
        self.start_pomodoro_btn.setEnabled(False)
        self.pause_pomodoro_btn.setEnabled(True)
        self.reset_pomodoro_btn.setEnabled(True)
        self.timer.start(1000)
        self.update_pomodoro_label()

    def pause_pomodoro(self):
        if self.is_pomodoro_running:
            self.is_pomodoro_running = False
            self.timer.stop()
            self.start_pomodoro_btn.setText("▶ Lanjut")
            self.start_pomodoro_btn.setEnabled(True)
            self.pause_pomodoro_btn.setEnabled(False)
            self.reset_pomodoro_btn.setEnabled(True)

    def reset_pomodoro(self):
        self.is_pomodoro_running = False
        self.timer.stop()
        self.pomodoro_seconds_left = 0
        self.current_pomodoro_session = None
        self.start_pomodoro_btn.setText("▶ Mulai")
        self.start_pomodoro_btn.setEnabled(True)
        self.pause_pomodoro_btn.setEnabled(False)
        self.reset_pomodoro_btn.setEnabled(False)
        self.update_pomodoro_label()

    def update_pomodoro(self):
        if self.pomodoro_seconds_left > 0 and self.is_pomodoro_running:
            self.pomodoro_seconds_left -= 1
            self.update_pomodoro_label()
            if self.pomodoro_seconds_left == 0:
                self.is_pomodoro_running = False
                self.timer.stop()
                self.progress += 1
                self.update_progress_display()
                self.update_pomodoro_stats()
                QMessageBox.information(self, "Selesai", "Sesi Pomodoro selesai! Ambil istirahat 5 menit.")
                self.start_pomodoro_btn.setText("▶ Mulai")
                self.start_pomodoro_btn.setEnabled(True)
                self.pause_pomodoro_btn.setEnabled(False)
                self.reset_pomodoro_btn.setEnabled(False)
                if self.progress < len([item for item in self.schedule_data if item['type'] == 'study']):
                    self.current_pomodoro_session = None
                    self.pomodoro_seconds_left = 0
                else:
                    QMessageBox.information(self, "Sukses", "Semua sesi belajar hari ini selesai!")
        else:
            self.is_pomodoro_running = False
            self.timer.stop()

    def update_pomodoro_label(self):
        minutes = self.pomodoro_seconds_left // 60
        seconds = self.pomodoro_seconds_left % 60
        self.pomodoro_label.setText(f"{minutes:02d}:{seconds:02d}")

    def update_progress_display(self):
        if self.schedule_data:
            total_sessions = sum(1 for item in self.schedule_data if item['type'] == 'study')
            self.progress_bar.setMaximum(total_sessions)
            self.progress_bar.setValue(self.progress)
            self.progress_label.setText(f"{self.progress}/{total_sessions} sesi selesai ({int((self.progress / total_sessions) * 100) if total_sessions > 0 else 0}%)")

    def update_pomodoro_stats(self):
        if self.schedule_data:
            total_study_sessions = sum(1 for item in self.schedule_data if item['type'] == 'study')
            total_break_sessions = sum(1 for item in self.schedule_data if item['type'] == 'break')
            self.pomodoro_info_widget.update_stats(self.progress, max(0, self.progress - 1))

    def check_urgent_tasks(self):
        tasks = [t for t in self.main_window.task_tab.to_dict() if not t['is_done']]
        urgent_tasks = sum(1 for t in tasks if QDateTime.fromString(t['deadline'], "yyyy-MM-dd HH:mm") < QDateTime.currentDateTime().addDays(2))
        self.urgent_tasks_label.setText(f"Tugas mendesak: {urgent_tasks}")
        if urgent_tasks > 0 and not self.is_pomodoro_running:
            QMessageBox.warning(self, "Peringatan", f"Ada {urgent_tasks} tugas mendesak! Prioritaskan dalam jadwal Anda.")

    def generate_schedule(self):
        tasks = [t for t in self.main_window.task_tab.to_dict() if not t['is_done']]
        if not tasks:
            QMessageBox.information(self, "Informasi", "Tidak ada tugas aktif untuk dijadwalkan!")
            return
        priority_mode = self.priority_input.currentText()
        def get_priority(task, index):
            name = task['name'].lower()
            deadline = QDateTime.fromString(task['deadline'], "yyyy-MM-dd HH:mm")
            days_left = QDateTime.currentDateTime().daysTo(deadline)
            if priority_mode == "Otomatis (berdasarkan deadline)":
                if "ujian" in name or "final" in name:
                    return 0 + days_left
                if "presentasi" in name or "proyek" in name:
                    return 100 + days_left
                if "kuis" in name or "laporan" in name:
                    return 200 + days_left
                return 300 + days_left
            elif priority_mode == "Manual (tertinggi ke terendah)":
                return index
            else:
                return -index
        tasks = [(task, i) for i, task in enumerate(tasks)]
        tasks.sort(key=lambda x: get_priority(x[0], x[1]))
        tasks = [task for task, _ in tasks]
        selected_hours_str = self.hours_input.currentText()
        selected_hours = int(selected_hours_str.split(' ')[0])
        total_minutes = selected_hours * 60
        selected_date = self.date_input.date()
        schedule = []
        current_time = QDateTime(selected_date, QTime(8, 0))
        task_index = 0
        session_count = {}
        if len(tasks) == 1:
            while total_minutes >= 50:
                session_count.setdefault(tasks[0]['name'], 0)
                session_count[tasks[0]['name']] += 1
                start = current_time
                end = start.addSecs(50 * 60)
                schedule.append({
                    "time": f"{start.toString('hh:mm')} - {end.toString('hh:mm')}",
                    "title": f"Fokus: {tasks[0]['name']}",
                    "subtitle": f"Sesi Belajar Produktif: Bagian {session_count[tasks[0]['name']]}",
                    "icon": "📚",
                    "color": "#3b82f6",
                    "type": "study"
                })
                current_time = end
                total_minutes -= 50
                if total_minutes >= 10:
                    start = current_time
                    end = start.addSecs(10 * 60)
                    schedule.append({
                        "time": f"{start.toString('hh:mm')} - {end.toString('hh:mm')}",
                        "title": "Istirahat Singkat",
                        "subtitle": "Regangkan badan atau minum air.",
                        "icon": "☕",
                        "color": "#10b981",
                        "type": "break"
                    })
                    current_time = end
                    total_minutes -= 10
        else:
            while total_minutes >= 50 and task_index < len(tasks):
                start = current_time
                end = start.addSecs(50 * 60)
                schedule.append({
                    "time": f"{start.toString('hh:mm')} - {end.toString('hh:mm')}",
                    "title": f"Fokus: {tasks[task_index]['name']}",
                    "subtitle": "Sesi Belajar Produktif",
                    "icon": "📚",
                    "color": "#3b82f6",
                    "type": "study"
                })
                current_time = end
                total_minutes -= 50
                task_index += 1
                if total_minutes >= 10:
                    start = current_time
                    end = start.addSecs(10 * 60)
                    schedule.append({
                        "time": f"{start.toString('hh:mm')} - {end.toString('hh:mm')}",
                        "title": "Istirahat Singkat",
                        "subtitle": "Regangkan badan atau minum air.",
                        "icon": "☕",
                        "color": "#10b981",
                        "type": "break"
                    })
                    current_time = end
                    total_minutes -= 10
        self.schedule_data = schedule
        self.progress = 0
        self.reset_pomodoro()
        self.update_progress_display()
        self.update_productivity_chart()
        self.display_schedule()
        self.update_ai_insights(tasks)
        self.update_pomodoro_stats()
        self.update_dynamic_tips()
        self.has_generated_schedule = True
        self.export_btn.setEnabled(True)
        self.reset_btn.setEnabled(True)
        self.start_pomodoro_btn.setEnabled(True)
        self.pause_pomodoro_btn.setEnabled(False)
        self.reset_pomodoro_btn.setEnabled(True)

    def reset_schedule(self):
        reply = QMessageBox.question(self, "Konfirmasi Reset", "Apakah Anda yakin ingin mereset jadwal ke setelan awal?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.schedule_data = []
            self.progress = 0
            self.has_generated_schedule = False
            self.reset_pomodoro()
            self.update_progress_display()
            self.productivity_chart.has_data = False
            self.productivity_chart.update()
            self.display_schedule()
            self.update_pomodoro_stats()
            self.update_dynamic_tips()
            self.export_btn.setEnabled(False)
            self.reset_btn.setEnabled(False)
            self.start_pomodoro_btn.setEnabled(False)
            self.pause_pomodoro_btn.setEnabled(False)
            self.reset_pomodoro_btn.setEnabled(False)

    def update_productivity_chart(self):
        study_time = sum(50 for item in self.schedule_data if item['type'] == 'study')
        break_time = sum(10 for item in self.schedule_data if item['type'] == 'break')
        self.productivity_chart.set_data(study_time, break_time)

    def display_schedule(self):
        while self.timeline_layout.count():
            self.timeline_layout.takeAt(0).widget().deleteLater()
        selected_date = self.calendar.selectedDate()
        if not self.schedule_data or selected_date != self.date_input.date():
            self.export_btn.setEnabled(False)
            self.timeline_container.setCurrentIndex(1)
            return
        for item in self.schedule_data:
            timeline_item = TimelineItem(item["time"], item["title"], item["subtitle"], item["icon"], item["color"], is_link=item['type'] == 'study')
            self.timeline_layout.addWidget(timeline_item)
        self.export_btn.setEnabled(True)
        self.timeline_container.setCurrentIndex(0)

    def update_ai_insights(self, tasks):
        self.quote_label.setText(random.choice(self.quotes))
        self.check_urgent_tasks()

    def update_dynamic_tips(self):
        if self.schedule_data:
            current_task = self.schedule_data[self.progress]['title'].split("Fokus: ")[1].lower() if self.progress < len(self.schedule_data) else ""
            tip_found = False
            for keyword, tips in self.study_tips.items():
                if keyword != "default" and keyword in current_task:
                    self.pomodoro_info_widget.update_tip(random.choice(tips))
                    tip_found = True
                    break
            if not tip_found:
                self.pomodoro_info_widget.update_tip(random.choice(self.study_tips["default"]))
        else:
            self.pomodoro_info_widget.update_tip("Tips akan muncul setelah jadwal dibuat.")

    def export_schedule(self):
        if not self.schedule_data:
            QMessageBox.warning(self, "Gagal", "Tidak ada jadwal untuk diekspor.")
            return
        fileName, _ = QFileDialog.getSaveFileName(self, "Simpan Jadwal", "JadwalBelajar.pdf", "PDF Files (*.pdf)")
        if not fileName:
            return
        if not fileName.endswith('.pdf'):
            fileName += '.pdf'
        pdf = SimpleDocTemplate(fileName, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=12,
            alignment=1
        )
        date_style = ParagraphStyle(
            'Date',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=12,
            alignment=1
        )
        elements.append(Paragraph("Jadwal Belajar Harian", title_style))
        elements.append(Paragraph(f"Dibuat pada {QDateTime.currentDateTime().toString('dd MMMM yyyy, hh:mm')}", date_style))
        data = [["Waktu", "Aktivitas", "Detail"]]
        for item in self.schedule_data:
            data.append([item["time"], item["title"], item["subtitle"]])
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(table)
        pdf.build(elements)
        QMessageBox.information(self, "Sukses", f"Jadwal berhasil diekspor ke:\n{fileName}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplikasi Perencana Jadwal")
        self.setGeometry(100, 100, 1000, 600)
        self.task_tab = TaskTab()
        self.schedule_tab = ScheduleTab(self)
        tabs = QTabWidget()
        tabs.addTab(self.task_tab, "Tugas")
        tabs.addTab(self.schedule_tab, "Jadwal")
        self.setCentralWidget(tabs)

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
>>>>>>> 6f8c74b61db7b91443edac1be989deeb72a66dd3
    app.exec_()