from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, 
    QHeaderView, QDateTimeEdit, QFrame, QCheckBox, QStackedWidget,
    QDateEdit, QTimeEdit
)
from PyQt5.QtCore import Qt, QDateTime, QDate, QTime
from PyQt5.QtGui import QColor, QFont

class TaskTab(QWidget):
    def __init__(self, save_callback, refresh_callback):
        super().__init__()
        self.save_callback = save_callback
        self.refresh_callback = refresh_callback
        self.original_deadlines = {}
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel("Manajemen Tugas")
        title_label.setObjectName("tabTitle")
        main_layout.addWidget(title_label)
        
        summary_panel = QHBoxLayout()
        summary_panel.setSpacing(15)
        self.active_card = self.create_summary_card("Tugas Aktif", "0")
        self.completed_card = self.create_summary_card("Tugas Selesai", "0")
        self.overdue_card = self.create_summary_card("Tugas Terlambat", "0")
        summary_panel.addWidget(self.active_card)
        summary_panel.addWidget(self.completed_card)
        summary_panel.addWidget(self.overdue_card)
        main_layout.addLayout(summary_panel)

        # Kolom pencarian
        search_frame = QFrame()
        search_frame.setStyleSheet("background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px;")
        search_layout = QHBoxLayout(search_frame)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari tugas...")
        self.search_input.textChanged.connect(self.search_tasks)
        search_layout.addWidget(self.search_input)
        main_layout.addWidget(search_frame)

        input_frame = QFrame()
        input_frame.setStyleSheet("background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px;")
        input_layout = QHBoxLayout(input_frame)
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Ketik tugas baru di sini...")
        
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setMinimumDate(QDate.currentDate())
        
        self.time_input = QTimeEdit(QTime.currentTime().addSecs(3600))
        
        self.add_btn = QPushButton("➕ Tambah Tugas")
        self.add_btn.clicked.connect(self.add_task)
        
        input_layout.addWidget(self.task_input, 3)
        input_layout.addWidget(QLabel("Tanggal:"))
        input_layout.addWidget(self.date_input, 1)
        input_layout.addWidget(QLabel("Waktu:"))
        input_layout.addWidget(self.time_input, 1)
        input_layout.addWidget(self.add_btn)
        main_layout.addWidget(input_frame)

        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack, 1)

        tasks_view_widget = QWidget()
        tasks_view_layout = QVBoxLayout(tasks_view_widget)
        tasks_view_layout.setContentsMargins(0, 15, 0, 0)
        
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(5)
        self.task_table.setHorizontalHeaderLabels(["Tugas", "Tanggal", "Waktu", "Selesai", "Aksi"])
        self.task_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.task_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        tasks_view_layout.addWidget(self.task_table)
        self.stack.addWidget(tasks_view_widget)

        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_icon = QLabel("🧘‍♂️")
        empty_icon.setStyleSheet("font-size: 60px;")
        empty_icon.setAlignment(Qt.AlignCenter)
        self.empty_text = QLabel("Anda belum memiliki tugas.\nSaatnya menambahkan tugas baru atau bersantai!")
        self.empty_text.setAlignment(Qt.AlignCenter)
        self.empty_text.setStyleSheet("font-size: 16px; color: #64748b;")
        empty_layout.addStretch()
        empty_layout.addWidget(empty_icon)
        empty_layout.addWidget(self.empty_text)
        empty_layout.addStretch()
        self.stack.addWidget(empty_widget)

    def create_summary_card(self, title, value):
        card = QFrame()
        card.setProperty("class", "taskSummaryCard")
        card_layout = QVBoxLayout(card)
        value_label = QLabel(value)
        value_label.setObjectName("valueLabel")
        value_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b;")
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 13px; color: #64748b;")
        card_layout.addWidget(value_label)
        card_layout.addWidget(title_label)
        return card

    def add_task(self):
        task_name = self.task_input.text().strip()
        if not task_name:
            QMessageBox.warning(self, "Input Tidak Valid", "Nama tugas tidak boleh kosong.")
            return

        dt = QDateTime(self.date_input.date(), self.time_input.time())
        if dt <= QDateTime.currentDateTime():
            QMessageBox.warning(self, "Waktu Tidak Valid", "Tanggal dan waktu tugas tidak boleh diatur ke waktu yang sudah berlalu.")
            return

        self.add_task_to_table(task_name, dt.toString("yyyy-MM-dd HH:mm"), False)
        self.task_input.clear()
        self.save_and_refresh()

    def add_task_to_table(self, name, deadline_str, is_done):
        row = self.task_table.rowCount()
        self.task_table.insertRow(row)

        task_item = QTableWidgetItem(name)
        task_item.setFlags(task_item.flags() & ~Qt.ItemIsEditable)
        self.task_table.setItem(row, 0, task_item)
        
        deadline = QDateTime.fromString(deadline_str, "yyyy-MM-dd HH:mm")

        date_widget = QDateEdit(deadline.date())
        date_widget.setCalendarPopup(True)
        date_widget.setDisplayFormat("dd MMM yyyy")
        date_widget.setEnabled(False)
        self.task_table.setCellWidget(row, 1, date_widget)

        time_widget = QTimeEdit(deadline.time())
        time_widget.setDisplayFormat("HH:mm")
        time_widget.setEnabled(False)
        self.task_table.setCellWidget(row, 2, time_widget)

        checkbox = QCheckBox()
        checkbox.setChecked(is_done)
        checkbox.stateChanged.connect(self.save_and_refresh)
        cell_widget = QWidget()
        cell_layout = QHBoxLayout(cell_widget)
        cell_layout.addWidget(checkbox)
        cell_layout.setAlignment(Qt.AlignCenter)
        cell_layout.setContentsMargins(0,0,0,0)
        self.task_table.setCellWidget(row, 3, cell_widget)
        
        self.create_action_buttons(row)

    def create_action_buttons(self, row):
        action_widget = QWidget()
        action_layout = QHBoxLayout(action_widget)
        action_layout.setContentsMargins(5, 0, 5, 0)
        action_layout.setSpacing(5)

        button_style = """
            QPushButton {
                padding: 5px;
                border-radius: 5px;
                color: white;
                font-size: 12px;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
        """

        edit_btn = QPushButton("Edit")
        edit_btn.setStyleSheet(f"{button_style} QPushButton {{ background-color: #3b82f6; }} QPushButton:hover {{ background-color: #2563eb; }}")
        edit_btn.setFixedSize(60, 28)
        edit_btn.clicked.connect(lambda: self.toggle_edit_mode(row, True))

        save_btn = QPushButton("Simpan")
        save_btn.setStyleSheet(f"{button_style} QPushButton {{ background-color: #10b981; }} QPushButton:hover {{ background-color: #059669; }}")
        save_btn.setFixedSize(60, 28)
        save_btn.clicked.connect(lambda: self.toggle_edit_mode(row, False))

        delete_btn = QPushButton("Hapus")
        delete_btn.setStyleSheet(f"{button_style} QPushButton {{ background-color: #ef4444; }} QPushButton:hover {{ background-color: #dc2626; }}")
        delete_btn.setFixedSize(60, 28)
        delete_btn.clicked.connect(lambda: self.delete_task(row))

        button_stack = QStackedWidget()
        button_stack.addWidget(edit_btn)
        button_stack.addWidget(save_btn)
        button_stack.setFixedSize(60, 28)
        
        action_layout.addWidget(button_stack)
        action_layout.addWidget(delete_btn)
        self.task_table.setCellWidget(row, 4, action_widget)

    def search_tasks(self):
        search_text = self.search_input.text().strip().lower()
        visible_rows = 0
        for row in range(self.task_table.rowCount()):
            task_name = self.task_table.item(row, 0).text().lower()
            is_visible = search_text in task_name
            self.task_table.setRowHidden(row, not is_visible)
            if is_visible:
                visible_rows += 1

        # Jika tidak ada tugas atau tidak ada hasil pencarian, tampilkan halaman kosong
        if self.task_table.rowCount() == 0:
            self.empty_text.setText("Anda belum memiliki tugas.\nSaatnya menambahkan tugas baru atau bersantai!")
            self.stack.setCurrentIndex(1)
        elif visible_rows == 0:
            self.empty_text.setText("Tidak ada tugas yang sesuai dengan pencarian Anda.")
            self.stack.setCurrentIndex(1)
        else:
            self.stack.setCurrentIndex(0)
        
        self.update_ui_state()

    def toggle_edit_mode(self, row, is_editing):
        task_item = self.task_table.item(row, 0)
        date_widget = self.task_table.cellWidget(row, 1)
        time_widget = self.task_table.cellWidget(row, 2)
        button_stack = self.task_table.cellWidget(row, 4).findChild(QStackedWidget)

        if is_editing:
            task_item.setFlags(task_item.flags() | Qt.ItemIsEditable)
            date_widget.setEnabled(True)
            time_widget.setEnabled(True)
            date_widget.setMinimumDate(QDate.currentDate())
            self.original_deadlines[row] = QDateTime(date_widget.date(), time_widget.time())
            button_stack.setCurrentIndex(1)
        else:
            if not task_item.text().strip():
                QMessageBox.warning(self, "Input Tidak Valid", "Nama tugas tidak boleh kosong.")
                return

            new_dt = QDateTime(date_widget.date(), time_widget.time())
            if new_dt <= QDateTime.currentDateTime():
                QMessageBox.warning(self, "Waktu Tidak Valid", "Tanggal dan waktu tugas tidak boleh diatur ke waktu yang sudah berlalu.")
                original_dt = self.original_deadlines.get(row)
                if original_dt:
                    date_widget.setDate(original_dt.date())
                    time_widget.setTime(original_dt.time())
                return

            task_item.setFlags(task_item.flags() & ~Qt.ItemIsEditable)
            date_widget.setEnabled(False)
            time_widget.setEnabled(False)
            button_stack.setCurrentIndex(0)
            self.save_and_refresh()

    def delete_task(self, row):
        task_name = self.task_table.item(row, 0).text()
        reply = QMessageBox.question(self, "Konfirmasi Hapus", f"Anda yakin ingin menghapus tugas '{task_name}'?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.task_table.removeRow(row)
            if row in self.original_deadlines:
                del self.original_deadlines[row]
            self.save_and_refresh()

    def save_and_refresh(self):
        self.save_callback()
        self.refresh_callback()
        self.search_tasks()
        self.update_ui_state()

    def update_ui_state(self):
        tasks = self.to_dict()
        # Stack sudah diatur di search_tasks, jadi tidak perlu diatur lagi di sini kecuali tidak ada tugas
        if not tasks:
            self.empty_text.setText("Anda belum memiliki tugas.\nSaatnya menambahkan tugas baru atau bersantai!")
            self.stack.setCurrentIndex(1)

        completed_count = 0
        overdue_count = 0
        now = QDateTime.currentDateTime()
        
        for row in range(self.task_table.rowCount()):
            deadline_dt = QDateTime(
                self.task_table.cellWidget(row, 1).date(),
                self.task_table.cellWidget(row, 2).time()
            )
            is_done = self.task_table.cellWidget(row, 3).findChild(QCheckBox).isChecked()

            font = QFont()
            task_color = QColor("#334155")
            date_time_color = QColor("#64748b")

            if is_done:
                font.setStrikeOut(True)
                task_color = QColor("#94a3b8")
                date_time_color = QColor("#bdc3c7")
                if not self.task_table.isRowHidden(row):
                    completed_count += 1
            elif now > deadline_dt:
                task_color = QColor("#ef4444")
                date_time_color = QColor("#ef4444")
                if not self.task_table.isRowHidden(row) and not is_done:
                    overdue_count += 1
            elif now.daysTo(deadline_dt) < 2:
                task_color = QColor("#f59e0b")
                date_time_color = QColor("#f59e0b")
            
            self.task_table.item(row, 0).setFont(font)
            self.task_table.item(row, 0).setForeground(task_color)
            
            for col in [1, 2]:
                widget = self.task_table.cellWidget(row, col)
                widget_type = "QDateEdit" if col == 1 else "QTimeEdit"
                if deadline_dt < now and not is_done:
                    widget.setStyleSheet(f"{widget_type} {{ color: {date_time_color.name()}; background-color: #f1f5f9; }}")
                else:
                    widget.setStyleSheet(f"{widget_type} {{ color: {date_time_color.name()}; background-color: transparent; }}")

        total_visible_tasks = sum(1 for row in range(self.task_table.rowCount()) if not self.task_table.isRowHidden(row))
        self.active_card.findChild(QLabel, "valueLabel").setText(str(total_visible_tasks - completed_count))
        self.completed_card.findChild(QLabel, "valueLabel").setText(str(completed_count))
        self.overdue_card.findChild(QLabel, "valueLabel").setText(str(overdue_count))
            
    def to_dict(self):
        tasks = []
        for r in range(self.task_table.rowCount()):
            date_val = self.task_table.cellWidget(r, 1).date()
            time_val = self.task_table.cellWidget(r, 2).time()
            deadline = QDateTime(date_val, time_val).toString("yyyy-MM-dd HH:mm")
            
            tasks.append({
                "name": self.task_table.item(r, 0).text(), 
                "deadline": deadline, 
                "is_done": self.task_table.cellWidget(r, 3).findChild(QCheckBox).isChecked()
            })
        return tasks

    def from_dict(self, data):
        self.task_table.setRowCount(0)
        for task in data:
            self.add_task_to_table(task["name"], task["deadline"], task["is_done"])
        self.search_tasks()
        self.update_ui_state()