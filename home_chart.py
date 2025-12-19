from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QColor, QPainter, QBrush, QPen, QFont
from collections import Counter
import math

class GradeChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grade_counts = {}
        self.grade_map = {}
        self.setMinimumHeight(250)  # Tingkatkan tinggi untuk ruang lebih banyak
        self.setStyleSheet("background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px;")

    def set_data(self, grades, grade_map):
        self.grade_counts = Counter(grades)
        self.grade_map = grade_map
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if not self.grade_counts or not self.grade_map:
            painter.setPen(QColor("#94a3b8"))
            painter.setFont(QFont("Arial", 12))
            painter.drawText(self.rect(), Qt.AlignCenter, "Belum ada data nilai.")
            return

        color_map = {
            'A': "#22c55e", 'AB': "#84cc16", 'B': "#a3e635", 'BC': "#facc15",
            'C': "#fbbf24", 'D': "#f97316", 'E': "#ef4444", 'A+': "#22c55e",
            'A-': "#4ade80", 'B+': "#a3e635", 'B-': "#bef264", 'C+': "#fde047",
            'C-': "#fb923c", 'F': "#ef4444"
        }

        grade_order = sorted(self.grade_map.keys(), key=lambda g: self.grade_map[g], reverse=True)
        padding_top, padding_bottom, padding_sides = 40, 50, 40  # Tambah padding untuk ruang lebih rapi

        max_count = max(self.grade_counts.values()) if self.grade_counts else 1

        painter.setPen(QPen(QColor("#e2e8f0"), 1, Qt.SolidLine))
        grid_lines = min(math.ceil(max_count / 2), 5) if max_count > 0 else 1
        if grid_lines == 0:
            grid_lines = 1

        font = QFont("Arial", 10)
        painter.setFont(font)
        for i in range(grid_lines + 1):
            y_pos = self.height() - padding_bottom - (i * (self.height() - padding_bottom - padding_top) / grid_lines)
            painter.drawLine(padding_sides, int(y_pos), self.width() - padding_sides, int(y_pos))
            value = math.ceil(max_count * (i / grid_lines))
            painter.setPen(QColor("#64748b"))
            painter.drawText(padding_sides - 30, int(y_pos - 5), 25, 20, Qt.AlignRight, str(value))

        total_width = self.width() - 2 * padding_sides
        bar_width = min(40, total_width / (len(grade_order) * 1.5))  # Batang lebih besar tapi tidak berlebihan
        spacing = (total_width - (bar_width * len(grade_order))) / (len(grade_order) + 1)  # Jarak lebih merata
        x_pos = padding_sides + spacing

        font.setBold(True)
        painter.setFont(font)
        for grade in grade_order:
            count = self.grade_counts.get(grade, 0)
            bar_height = (self.height() - padding_bottom - padding_top) * (count / max_count) if max_count > 0 else 0

            if bar_height > 0:
                # Efek elevasi sederhana dengan warna latar
                painter.setBrush(QColor("#f1f5f9"))
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(QRect(int(x_pos + 2), int(self.height() - padding_bottom - bar_height + 2), int(bar_width - 4), int(bar_height)), 4, 4)

                painter.setBrush(QColor(color_map.get(grade, "#60a5fa")))
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(QRect(int(x_pos), int(self.height() - padding_bottom - bar_height), int(bar_width - 4), int(bar_height)), 4, 4)

            painter.setPen(QColor("#1e293b"))
            painter.drawText(int(x_pos), int(self.height() - padding_bottom - bar_height - 20), int(bar_width - 4), 20, Qt.AlignCenter, str(count))

            painter.setPen(QColor("#475569"))
            painter.drawText(int(x_pos), int(self.height() - padding_bottom + 5), int(bar_width - 4), 20, Qt.AlignCenter, grade)
            x_pos += bar_width + spacing