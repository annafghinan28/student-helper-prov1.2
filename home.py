# home.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGridLayout, QProgressBar, QSizePolicy
)
from PyQt5.QtCore import Qt, QDateTime, QPropertyAnimation, QEasingCurve, QPoint
from PyQt5.QtGui import QColor, QPainter, QFont, QPen, QBrush, QLinearGradient
from collections import Counter
import math

class ModernCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "modernCard")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def enterEvent(self, event):
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(200)
        self.animation.setEndValue(self.pos() + QPoint(0, -5))
        self.animation.setEasingCurve(QEasingCurve.OutQuad)
        self.animation.start()
        
    def leaveEvent(self, event):
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(200)
        self.animation.setEndValue(self.pos() + QPoint(0, 5))
        self.animation.setEasingCurve(QEasingCurve.OutQuad)
        self.animation.start()

class GradeChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grade_counts = {}
        self.setMinimumHeight(150)

    def set_data(self, grades):
        self.grade_counts = Counter(grades)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if not self.grade_counts:
            painter.setPen(QColor("#94a3b8"))
            painter.drawText(self.rect(), Qt.AlignCenter, "Data nilai belum cukup.")
            return
            
        grade_order = ['A', 'AB', 'B', 'BC', 'C', 'CD', 'D', 'DE', 'E']
        text_color = QColor("#475569")
        gradient_colors = [QColor("#60a5fa"), QColor("#3b82f6"), QColor("#2563eb")]
        padding_bottom = 40
        padding_top = 20
        padding_sides = 30 
        max_count = max(self.grade_counts.values()) if self.grade_counts else 1
        
        painter.setPen(QPen(QColor("#e2e8f0"), 1))
        grid_lines = min(math.ceil(max_count), 5) if max_count > 0 else 1
        if grid_lines == 0: grid_lines = 1

        for i in range(grid_lines + 1):
            y_pos = self.height() - padding_bottom - (i * (self.height() - padding_bottom - padding_top) / grid_lines)
            
            painter.drawLine(padding_sides, int(y_pos), self.width() - padding_sides, int(y_pos))
            
            value = math.ceil(max_count * (i / grid_lines))
            painter.setPen(QColor("#64748b"))
            painter.drawText(0, int(y_pos - 5), padding_sides - 5, 10, Qt.AlignRight, str(value))
        
        available_width = self.width() - (padding_sides * 2)
        bar_width = available_width / len(grade_order) * 0.7
        spacing = available_width / len(grade_order) * 0.3
        x_pos = padding_sides + spacing / 2
        
        for i, grade in enumerate(grade_order):
            count = self.grade_counts.get(grade, 0)
            bar_height = (self.height() - padding_bottom - padding_top) * (count / max_count)
            
            gradient = QLinearGradient(0, self.height() - padding_bottom - bar_height, 0, self.height() - padding_bottom)
            color_idx = i % len(gradient_colors)
            gradient.setColorAt(0, gradient_colors[color_idx].lighter(120))
            gradient.setColorAt(1, gradient_colors[color_idx])
            
            if bar_height > 0:
                painter.setBrush(QBrush(gradient))
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(int(x_pos), int(self.height() - padding_bottom - bar_height), int(bar_width), int(bar_height), 4, 4)
                
                painter.setPen(QColor("#ffffff"))
                painter.drawText(int(x_pos), int(self.height() - padding_bottom - bar_height + 15), int(bar_width), 15, Qt.AlignCenter, str(count))

            painter.setPen(text_color)
            font = QFont(); font.setBold(True); painter.setFont(font)
            painter.drawText(int(x_pos), self.height() - padding_bottom + 20, int(bar_width), 15, Qt.AlignCenter, grade)
            x_pos += bar_width + spacing

class HomeTab(QWidget):
    def __init__(self, main_window):
        super().__init__(parent=main_window)
        self.main_window = main_window
        self.init_ui()
    
    # Fungsi ini tidak lagi dibutuhkan karena kita akan memperbarui langsung dari refresh_dashboard()
    def set_user_name(self, name):
        pass

    # Fungsi ini tidak lagi dibutuhkan karena kita akan memperbarui langsung dari refresh_dashboard()
    def update_greeting(self):
        pass

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(25)
        
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f0f9ff, stop:1 #e0f2fe);
            border-radius: 10px;
        """)
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 20, 20, 20)
        
        top_header_layout = QHBoxLayout()
        # Perbaikan: Ambil nama pengguna langsung dari main_window.settings
        user_name = self.main_window.settings.get("user_name", "Mahasiswa")
        self.greeting_label = QLabel(f"Halo, {user_name}!")
        self.greeting_label.setStyleSheet("font-size: 32px; font-weight: 700; color: #0f172a;")
        title_label = QLabel("Dashboard Mahasiswa")
        title_label.setObjectName("mainTitle")
        title_label.setStyleSheet("font-size: 24px; font-weight: 600; color: #0f172a;")
        
        top_header_layout.addWidget(self.greeting_label)
        top_header_layout.addStretch()
        top_header_layout.addWidget(title_label)
        
        header_layout.addLayout(top_header_layout)
        
        date_label = QLabel(QDateTime.currentDateTime().toString("dddd, dd MMMM yyyy"))
        date_label.setObjectName("dateLabel")
        date_label.setStyleSheet("font-size: 16px; color: #475569;")
        header_layout.addWidget(date_label)
        
        intro_text = QLabel("Selamat datang kembali! Mari kelola tugas, nilai, dan jadwal Anda dengan lebih efisien.")
        intro_text.setStyleSheet("font-size: 16px; color: #475569; margin-top: -5px;")
        header_layout.addWidget(intro_text)
        
        main_layout.addWidget(header_widget)
        
        preview_label = QLabel("Menu Utama")
        preview_label.setObjectName("sectionTitle")
        main_layout.addWidget(preview_label)
        preview_grid = QGridLayout()
        preview_grid.setSpacing(15)
        tab_previews_data = [
            ("Tugas", "Kelola tugas dan deadline", "📝", "#ef4444", 1),
            ("Catatan", "Tulis dan simpan catatan", "📒", "#f59e0b", 2),
            ("IPK", "Lihat dan kelola nilai", "🎓", "#3b82f6", 3),
            ("Jadwal Cerdas", "Buat jadwal belajar otomatis", "🤖", "#10b981", 4)
        ]
        for i, (title, desc, icon, color, index) in enumerate(tab_previews_data):
            row, col = i // 2, i % 2
            card = TabPreviewCard(title, desc, icon, color)
            card.mousePressEvent = lambda e, idx=index: self.main_window.sidebar.setCurrentRow(idx)
            preview_grid.addWidget(card, row, col)
        main_layout.addLayout(preview_grid)
        dashboard_label = QLabel("Ringkasan")
        dashboard_label.setObjectName("sectionTitle")
        main_layout.addWidget(dashboard_label)
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)
        self.urgent_tasks_card = self.create_card("Tugas Mendesak", "⏰")
        self.gpa_summary_card = self.create_card("IPK Saat Ini", "🏆")
        self.grade_chart_card = self.create_card("Distribusi Nilai", "📊")
        grid_layout.addWidget(self.urgent_tasks_card, 0, 0)
        grid_layout.addWidget(self.gpa_summary_card, 0, 1)
        grid_layout.addWidget(self.grade_chart_card, 1, 0, 1, 2)
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)
        main_layout.addLayout(grid_layout)
        main_layout.addStretch()
    def create_card(self, title, icon):
        card = ModernCard()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 15, 20, 15)
        header_layout = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setProperty("class", "cardTitle")
        icon_label = QLabel(icon)
        icon_label.setProperty("class", "cardIcon")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(icon_label)
        content_widget = QWidget()
        content_widget.setObjectName("cardContent")
        card_layout.addLayout(header_layout)
        card_layout.addWidget(content_widget, 1)
        return card
    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
    def get_or_create_layout(self, widget):
        if widget is None: return None
        layout = widget.layout()
        if layout:
            self.clear_layout(layout)
        else:
            layout = QVBoxLayout(widget)
            layout.setContentsMargins(0, 10, 0, 0)
        return layout
    
    # Perbaikan: Sekarang mengambil nama pengguna terbaru dari main_window saat dipanggil
    def refresh_dashboard(self):
        user_name = self.main_window.settings.get("user_name", "Mahasiswa")
        self.greeting_label.setText(f"Halo, {user_name}!")
        
        self.update_tasks_preview(self.main_window.task_tab)
        self.update_gpa_preview(self.main_window.gpa_tab)
        self.update_chart_preview(self.main_window.gpa_tab)
        
    def update_tasks_preview(self, task_tab):
        content_widget = self.urgent_tasks_card.findChild(QWidget, "cardContent")
        layout = self.get_or_create_layout(content_widget)
        if layout is None: return
        tasks = [t for t in task_tab.to_dict() if not t['is_done']]
        tasks.sort(key=lambda x: QDateTime.fromString(x['deadline'], "yyyy-MM-dd HH:mm"))
        if not tasks:
            label = QLabel("Tidak ada tugas aktif. ✨")
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)
        else:
            for task in tasks[:2]:
                task_label = QLabel(f"<b>{task['name']}</b>")
                layout.addWidget(task_label)
        layout.addStretch()
    def update_gpa_preview(self, gpa_tab):
        content_widget = self.gpa_summary_card.findChild(QWidget, "cardContent")
        layout = self.get_or_create_layout(content_widget)
        if layout is None: return
        if gpa_tab.total_sks == 0:
            label = QLabel("Belum ada nilai.")
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)
        else:
            ipk_label = QLabel(f"<p style='font-size: 32px; font-weight: 800; color: #1e293b;'>{gpa_tab.ipk:.2f}</p>")
            sks_label = QLabel(f"Total SKS ditempuh: {gpa_tab.total_sks}")
            layout.addWidget(ipk_label)
            layout.addWidget(sks_label)
        layout.addStretch()
    def update_chart_preview(self, gpa_tab):
        content_widget = self.grade_chart_card.findChild(QWidget, "cardContent")
        layout = self.get_or_create_layout(content_widget)
        if layout is None: return
        grades = [course['grade'] for course in gpa_tab.to_dict().get('courses', [])]
        chart = GradeChart()
        chart.set_data(grades)
        layout.addWidget(chart)

class TabPreviewCard(ModernCard):
    def __init__(self, title, description, icon, color, parent=None):
        super().__init__(parent)
        self.setFixedHeight(120)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        header_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(30, 30)
        icon_label.setStyleSheet(f"background-color: {color}; border-radius: 15px; color: white; font-weight: bold;")
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #1e293b;")
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        desc_label = QLabel(description)
        desc_label.setStyleSheet("color: #64748b; font-size: 13px;")
        desc_label.setWordWrap(True)
        layout.addLayout(header_layout)
        layout.addWidget(desc_label)
        layout.addStretch()
        self.setCursor(Qt.PointingHandCursor)