from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QComboBox, QFrame, QStyledItemDelegate, QStackedWidget
)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QColor, QPainter, QFont
from home_chart import GradeChart

class GradeDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        grade = index.model().data(index, Qt.DisplayRole).upper()
        color_map = {
            'A': "#22c55e", 'AB': "#84cc16", 'B': "#a3e635", 'BC': "#facc15", 
            'C': "#fbbf24", 'D': "#f97316", 'E': "#ef4444", 'A+': "#22c55e", 
            'A-': "#4ade80", 'B+': "#a3e635", 'B-': "#bef264", 'C+': "#fde047", 
            'C-': "#fb923c", 'F': "#ef4444"
        }
        super().paint(painter, option, index)
        if grade in color_map:
            color = QColor(color_map[grade])
            path = painter.clipPath()
            path.addRoundedRect(QRectF(option.rect.adjusted(4, 4, -4, -4)), 4, 4)
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawPath(path)
            painter.setPen(QColor("white"))
            font = QFont()
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(option.rect, Qt.AlignCenter, grade)

class GPATab(QWidget):
    def __init__(self, save_callback, refresh_callback):
        super().__init__()
        self.save_callback = save_callback
        self.refresh_callback = refresh_callback
        self.has_unsaved_changes = False
        self.total_sks = 0
        self.ipk = 0.0
        self.grade_systems = {
            "Sistem A, AB, B": {'A': 4.0, 'AB': 3.5, 'B': 3.0, 'BC': 2.5, 'C': 2.0, 'D': 1.0, 'E': 0.0},
            "Sistem A+, A, A-": {'A+': 4.0, 'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0, 'B-': 2.7, 'C+': 2.3, 'C': 2.0, 'C-': 1.7, 'D': 1.0, 'F': 0.0}
        }
        self.current_system_name = "Sistem A, AB, B"
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel("Analisis Indeks Prestasi")
        title_label.setObjectName("tabTitle")
        main_layout.addWidget(title_label)

        # Summary Panel
        summary_panel = QHBoxLayout()
        summary_panel.setSpacing(20)
        self.ipk_card = self.create_summary_card("IPK Saat Ini", "0.00", "ipkValueLabel")
        self.sks_card = self.create_summary_card("Total SKS", "0", "sksValueLabel")
        summary_panel.addWidget(self.ipk_card)
        summary_panel.addWidget(self.sks_card)
        summary_panel.addStretch()
        main_layout.addLayout(summary_panel)

        # Input Frame
        input_frame = QFrame()
        input_frame.setProperty("class", "modernCard")
        input_layout = QVBoxLayout(input_frame)
        input_layout.addWidget(QLabel("<b>Tambah Nilai Mata Kuliah Baru</b>"))
        form_layout = QHBoxLayout()
        self.course_input = QLineEdit()
        self.course_input.setPlaceholderText("Nama Mata Kuliah")
        self.sks_input = QLineEdit()
        self.sks_input.setPlaceholderText("SKS")
        self.grade_input = QLineEdit()
        self.grade_input.setPlaceholderText("Nilai")
        form_layout.addWidget(self.course_input, 2)
        form_layout.addWidget(self.sks_input, 1)
        form_layout.addWidget(self.grade_input, 1)
        action_layout = QHBoxLayout()
        self.system_selector = QComboBox()
        self.system_selector.addItems(self.grade_systems.keys())
        self.system_selector.currentTextChanged.connect(self.change_system)
        self.add_btn = QPushButton("➕ Tambah")
        self.add_btn.clicked.connect(self.add_course)
        action_layout.addWidget(QLabel("Sistem Nilai:"))
        action_layout.addWidget(self.system_selector)
        action_layout.addStretch()
        action_layout.addWidget(self.add_btn)
        input_layout.addLayout(form_layout)
        input_layout.addLayout(action_layout)
        main_layout.addWidget(input_frame)

        # AI Prediction Panel
        ai_frame = QFrame()
        ai_frame.setProperty("class", "modernCard")
        ai_layout = QVBoxLayout(ai_frame)
        ai_layout.addWidget(QLabel("<b>Prediksi IPK & Rekomendasi</b>"))
        ai_form_layout = QHBoxLayout()
        self.ai_sks_input = QLineEdit()
        self.ai_sks_input.setPlaceholderText("SKS Tambahan")
        self.ai_grade_input = QLineEdit()
        self.ai_grade_input.setPlaceholderText("Nilai Target")
        self.ai_target_ipk_input = QLineEdit()
        self.ai_target_ipk_input.setPlaceholderText("IPK Target")
        self.ai_predict_btn = QPushButton("🔍 Prediksi IPK")
        self.ai_predict_btn.clicked.connect(self.predict_ipk)
        ai_form_layout.addWidget(self.ai_sks_input, 1)
        ai_form_layout.addWidget(self.ai_grade_input, 1)
        ai_form_layout.addWidget(self.ai_target_ipk_input, 1)
        ai_form_layout.addWidget(self.ai_predict_btn)
        self.ai_result_label = QLabel("Masukkan data untuk melihat prediksi IPK atau rekomendasi.")
        self.ai_result_label.setStyleSheet("font-size: 14px; color: #64748b; padding: 10px;")
        ai_layout.addLayout(ai_form_layout)
        ai_layout.addWidget(self.ai_result_label)
        main_layout.addWidget(ai_frame)

        # Bottom Panel
        bottom_panel = QHBoxLayout()
        bottom_panel.setSpacing(20)
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)

        self.table_stack = QStackedWidget()

        # Table Page
        table_widget = QWidget()
        table_widget_layout = QVBoxLayout(table_widget)
        self.gpa_table = QTableWidget(0, 3)
        self.gpa_table.setHorizontalHeaderLabels(["Mata Kuliah", "SKS", "Nilai"])
        self.gpa_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.gpa_table.setItemDelegateForColumn(2, GradeDelegate())
        table_widget_layout.addWidget(self.gpa_table)

        # Info Page
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_label = QLabel("Belum ada nilai yang diinput.\nSilakan tambahkan mata kuliah dan nilai Anda di atas untuk memulai.")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("font-size: 16px; color: #64748b; padding: 50px;")
        info_layout.addWidget(info_label)

        self.table_stack.addWidget(table_widget)
        self.table_stack.addWidget(info_widget)

        table_footer_layout = QHBoxLayout()
        self.save_btn = QPushButton("💾 Simpan Perubahan")
        self.save_btn.clicked.connect(self.save_changes)
        self.save_btn.setEnabled(False)
        self.delete_btn = QPushButton("Hapus Terpilih")
        self.delete_btn.clicked.connect(self.delete_course)
        table_footer_layout.addStretch()
        table_footer_layout.addWidget(self.delete_btn)
        table_footer_layout.addWidget(self.save_btn)

        table_layout.addWidget(self.table_stack, 1)
        table_layout.addLayout(table_footer_layout)

        chart_container = QFrame()
        chart_container.setProperty("class", "modernCard")
        chart_layout = QVBoxLayout(chart_container)
        chart_layout.addWidget(QLabel("<b>Distribusi Nilai</b>"))
        self.chart = GradeChart()
        chart_layout.addWidget(self.chart)
        bottom_panel.addWidget(table_container, 2)
        bottom_panel.addWidget(chart_container, 1)
        main_layout.addLayout(bottom_panel, 1)

    def set_dirty(self, dirty):
        self.has_unsaved_changes = dirty
        self.save_btn.setEnabled(dirty)

    def save_changes(self):
        self.save_callback()
        self.set_dirty(False)
        self.refresh_callback()
        QMessageBox.information(self, "Sukses", "Perubahan nilai berhasil disimpan.")

    def create_summary_card(self, title, value, value_label_name):
        card = QFrame()
        card.setProperty("class", "modernCard")
        card_layout = QVBoxLayout(card)
        value_label = QLabel(value)
        value_label.setObjectName(value_label_name)
        value_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #1e293b;")
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; color: #64748b;")
        card_layout.addWidget(value_label)
        card_layout.addWidget(title_label)
        return card

    def change_system(self, system_name):
        self.current_system_name = system_name
        self.set_dirty(True)
        self.calculate_and_update_ui()

    def add_course(self):
        try:
            sks = int(self.sks_input.text())
            if sks <= 0:
                QMessageBox.warning(self, "Error", "SKS harus lebih dari 0.")
                return
        except ValueError:
            QMessageBox.warning(self, "Error", "SKS harus berupa angka.")
            return
        grade = self.grade_input.text().upper()
        if grade not in self.grade_systems[self.current_system_name]:
            QMessageBox.warning(self, "Error", f"Nilai harus salah satu dari: {', '.join(self.grade_systems[self.current_system_name].keys())}")
            return
        row = self.gpa_table.rowCount()
        self.gpa_table.insertRow(row)
        self.gpa_table.setItem(row, 0, QTableWidgetItem(self.course_input.text()))
        self.gpa_table.setItem(row, 1, QTableWidgetItem(str(sks)))
        self.gpa_table.setItem(row, 2, QTableWidgetItem(grade))
        for w in [self.course_input, self.sks_input, self.grade_input]:
            w.clear()
        self.set_dirty(True)
        self.calculate_and_update_ui()

    def delete_course(self):
        if self.gpa_table.currentRow() < 0:
            return
        self.gpa_table.removeRow(self.gpa_table.currentRow())
        self.set_dirty(True)
        self.calculate_and_update_ui()

    def calculate_and_update_ui(self):
        total_bobot, self.total_sks = 0, 0
        grade_map = self.grade_systems[self.current_system_name]
        grades_list = []
        for row in range(self.gpa_table.rowCount()):
            try:
                sks = int(self.gpa_table.item(row, 1).text())
                grade = self.gpa_table.item(row, 2).text().upper()
                grades_list.append(grade)
                if grade in grade_map:
                    self.total_sks += sks
                    total_bobot += grade_map.get(grade, 0) * sks
            except (ValueError, AttributeError):
                continue
        self.ipk = total_bobot / self.total_sks if self.total_sks > 0 else 0
        
        self.ipk_card.findChild(QLabel, "ipkValueLabel").setText(f"{self.ipk:.2f}")
        self.sks_card.findChild(QLabel, "sksValueLabel").setText(str(self.total_sks))
        self.chart.set_data(grades_list, grade_map)
        
        self.table_stack.setCurrentIndex(0 if self.gpa_table.rowCount() > 0 else 1)

    def predict_ipk(self):
        try:
            additional_sks = int(self.ai_sks_input.text())
            if additional_sks <= 0:
                QMessageBox.warning(self, "Error", "SKS tambahan harus lebih dari 0.")
                return
        except ValueError:
            additional_sks = 0
        target_grade = self.ai_grade_input.text().upper()
        grade_map = self.grade_systems[self.current_system_name]
        if target_grade and target_grade not in grade_map:
            QMessageBox.warning(self, "Error", f"Nilai target harus salah satu dari: {', '.join(grade_map.keys())}")
            return
        try:
            target_ipk = float(self.ai_target_ipk_input.text())
            if not 0 <= target_ipk <= 4.0:
                QMessageBox.warning(self, "Error", "IPK target harus antara 0.0 dan 4.0.")
                return
        except ValueError:
            target_ipk = None

        current_bobot = self.ipk * self.total_sks if self.total_sks > 0 else 0
        result_text = ""

        # Prediksi IPK dengan SKS dan nilai tambahan
        if additional_sks > 0 and target_grade:
            new_bobot = current_bobot + (grade_map[target_grade] * additional_sks)
            new_sks = self.total_sks + additional_sks
            predicted_ipk = new_bobot / new_sks if new_sks > 0 else 0
            result_text += f"Dengan tambahan {additional_sks} SKS dan nilai {target_grade}, IPK Anda akan menjadi: <b>{predicted_ipk:.2f}</b>."

        # Rekomendasi untuk mencapai IPK target
        if target_ipk is not None:
            if result_text:
                result_text += "<br>"
            current_ipk = self.ipk
            if current_ipk >= target_ipk:
                result_text += f"IPK Anda saat ini ({current_ipk:.2f}) sudah mencapai atau melebihi target ({target_ipk:.2f})."
            else:
                required_bobot = target_ipk * (self.total_sks + additional_sks) - current_bobot
                if additional_sks > 0:
                    required_grade_value = required_bobot / additional_sks
                    if required_grade_value > 4.0:
                        result_text += f"IPK target {target_ipk:.2f} tidak dapat dicapai dengan {additional_sks} SKS tambahan, karena nilai rata-rata yang dibutuhkan melebihi 4.0."
                    elif required_grade_value < 0:
                        result_text += f"IPK target {target_ipk:.2f} sudah terlampaui bahkan tanpa nilai tambahan."
                    else:
                        # Filter grades yang >= required_grade_value
                        candidates = {k: v for k, v in grade_map.items() if v >= required_grade_value}
                        if candidates:
                            # Pilih yang terkecil (minimal di atas atau sama dengan required)
                            closest_grade = min(candidates.items(), key=lambda x: x[1])
                            result_text += f"Untuk mencapai IPK {target_ipk:.2f} dengan {additional_sks} SKS tambahan, Anda perlu nilai rata-rata minimal setara <b>{closest_grade[0]}</b> ({closest_grade[1]:.2f}). "
                            # Tambahan info: IPK jika punya nilai tersebut dengan SKS tersebut
                            predicted_ipk_with_closest = (current_bobot + (closest_grade[1] * additional_sks)) / (self.total_sks + additional_sks)
                            result_text += f"IPK Anda akan menjadi <b>{predicted_ipk_with_closest:.2f}</b> jika Anda memiliki nilai {closest_grade[0]} dengan {additional_sks} SKS."
                            # Karena >= required, selalu bisa dicapai atau lebih baik
                            result_text += " (Bisa dicapai atau lebih baik)."
                        else:
                            result_text += f"IPK target {target_ipk:.2f} tidak dapat dicapai dengan {additional_sks} SKS tambahan, karena tidak ada nilai yang cukup tinggi."
                else:
                    result_text += "Masukkan jumlah SKS tambahan untuk mendapatkan rekomendasi nilai."

        if not result_text:
            result_text = "Masukkan SKS tambahan dan/atau nilai target untuk prediksi, atau IPK target untuk rekomendasi."

        self.ai_result_label.setText(result_text)

    def to_dict(self):
        courses = [
            {
                "course": self.gpa_table.item(r, 0).text(),
                "sks": self.gpa_table.item(r, 1).text(),
                "grade": self.gpa_table.item(r, 2).text()
            } for r in range(self.gpa_table.rowCount())
        ]
        return {"courses": courses, "system": self.current_system_name}

    def from_dict(self, data):
        self.gpa_table.setRowCount(0)
        system_name = data.get("system", "Sistem A, AB, B")
        if system_name in self.grade_systems:
            self.system_selector.setCurrentText(system_name)
        courses = data.get("courses", [])
        for course in courses:
            row = self.gpa_table.rowCount()
            self.gpa_table.insertRow(row)
            self.gpa_table.setItem(row, 0, QTableWidgetItem(course["course"]))
            self.gpa_table.setItem(row, 1, QTableWidgetItem(course["sks"]))
            self.gpa_table.setItem(row, 2, QTableWidgetItem(course["grade"]))
        self.calculate_and_update_ui()
        self.set_dirty(False)