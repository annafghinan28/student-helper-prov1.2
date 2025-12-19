from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QListWidget, QLabel, QLineEdit, QMessageBox, QListWidgetItem,
    QToolBar, QAction, QFileDialog, QStackedWidget, QInputDialog, QFrame, QCheckBox
)
from PyQt5.QtCore import Qt, QDateTime, QSize
from PyQt5.QtGui import QFont, QTextCursor, QTextImageFormat, QPixmap
import uuid
from datetime import datetime

class NoteListItem(QWidget):
    """Custom widget for each note item in the list."""
    def __init__(self, title, date, preview):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        
        title_label = QLabel(title or "Tanpa Judul")
        title_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #1e293b;")
        title_label.setWordWrap(True)
        title_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        date_label = QLabel(date or "Tidak Diketahui")
        date_label.setStyleSheet("font-size: 11px; color: #94a3b8;")
        date_label.setWordWrap(True)
        
        preview_label = QLabel(preview or "")
        preview_label.setStyleSheet("font-size: 12px; color: #64748b;")
        preview_label.setWordWrap(True)
        preview_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        layout.addWidget(title_label)
        layout.addWidget(preview_label)
        layout.addStretch()
        layout.addWidget(date_label)
        self.adjustSize()
        self.setMinimumHeight(self.sizeHint().height() + 10)

class AdvancedTextEdit(QTextEdit):
    """Enhanced QTextEdit with auto-list functionality."""
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            cursor = self.textCursor()
            text = cursor.block().text().lstrip()
            if text.startswith("• "):
                if text.strip() == "•":
                    cursor.select(QTextCursor.BlockUnderCursor)
                    cursor.removeSelectedText()
                    cursor.insertBlock()
                else:
                    super().keyPressEvent(event)
                    cursor.insertText("• ")
                return
        super().keyPressEvent(event)

class NotesTab(QWidget):
    def __init__(self, save_callback, refresh_callback):
        super().__init__()
        self.save_callback = save_callback
        self.refresh_callback = refresh_callback
        self.notes = []
        self.current_index = -1
        self.has_unsaved_changes = False
        self.is_edit_mode = False
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)
        
        # Left Panel
        left_panel = QWidget()
        left_panel.setObjectName("notesListPanel")
        left_layout = QVBoxLayout(left_panel)
        left_panel.setFixedWidth(320)
        
        # Header dan kartu ringkasan (dikembalikan karena penting)
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel("Catatan")
        title_label.setObjectName("tabTitle")
        header_layout.addWidget(title_label)
        summary_panel = QHBoxLayout()
        summary_panel.setSpacing(15)
        self.total_notes_card = self.create_summary_card("Total Catatan", "0")
        summary_panel.addWidget(self.total_notes_card)
        summary_panel.addStretch()
        header_layout.addLayout(summary_panel)
        left_layout.addWidget(header_widget)
        
        list_header = QHBoxLayout()
        list_header.setContentsMargins(15, 15, 15, 10)
        list_header.addWidget(QLabel("<b>Semua Catatan</b>"))
        list_header.addStretch()
        self.new_btn = QPushButton("➕ Baru")
        self.new_btn.clicked.connect(self.new_note)
        list_header.addWidget(self.new_btn)
        
        search_frame = QFrame()
        search_frame.setObjectName("notesSearchBar")
        search_layout = QHBoxLayout(search_frame)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari catatan...")
        self.search_input.textChanged.connect(self.search_notes)
        search_layout.addWidget(self.search_input)
        left_layout.addLayout(list_header)
        left_layout.addWidget(search_frame)
        
        self.notes_list = QListWidget()
        self.notes_list.setObjectName("notesListWidget")
        self.notes_list.currentRowChanged.connect(self.select_note)
        left_layout.addWidget(self.notes_list, 1)
        
        # Right Panel
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Judul Catatan...")
        self.title_input.setStyleSheet("font-size: 24px; font-weight: bold; padding: 20px; border: none; background: white;")
        
        self.last_edited_label = QLabel("Belum disimpan")
        self.last_edited_label.setStyleSheet("color: #94a3b8; padding-left: 20px; background: white; padding-bottom: 10px;")
        
        self.body_input = AdvancedTextEdit()
        self.body_input.setObjectName("notesTextEditor")
        self.body_input.setPlaceholderText("Mulai menulis...")
        
        self.title_input.textChanged.connect(self.set_dirty)
        self.body_input.textChanged.connect(self.set_dirty)
        toolbar = QToolBar()
        self.setup_toolbar(toolbar)
        
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(10, 10, 10, 10)
        footer_layout.setSpacing(10)
        
        self.edit_delete_stack = QStackedWidget()
        self.setup_edit_delete_buttons()
        
        self.save_btn = QPushButton("Simpan")
        self.save_btn.clicked.connect(self.save_note)
        footer_layout.addWidget(self.edit_delete_stack)
        footer_layout.addStretch()
        footer_layout.addWidget(self.save_btn)
        
        right_layout.addWidget(self.title_input)
        right_layout.addWidget(self.last_edited_label)
        right_layout.addWidget(toolbar)
        right_layout.addWidget(self.body_input, 1)
        right_layout.addLayout(footer_layout)
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, 1)
        
        self.body_input.currentCharFormatChanged.connect(self.update_toolbar_state)
        self.body_input.cursorPositionChanged.connect(self.check_image_at_cursor)
        self.title_input.setReadOnly(True)
        self.body_input.setReadOnly(True)
        self.update_editor_state(False, False)

    def create_summary_card(self, title, value):
        card = QFrame()
        card.setProperty("class", "card")  # Sesuai style.qss untuk efek kartu universal
        card_layout = QVBoxLayout(card)
        value_label = QLabel(value)
        value_label.setObjectName("valueLabel")
        value_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b;")
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 13px; color: #64748b;")
        card_layout.addWidget(value_label)
        card_layout.addWidget(title_label)
        return card

    def update_summary_cards(self):
        total_notes = len(self.notes)
        self.total_notes_card.findChild(QLabel, "valueLabel").setText(str(total_notes))

    def set_dirty(self):
        if self.is_edit_mode:
            self.has_unsaved_changes = True
            self.save_btn.setEnabled(True)

    def setup_toolbar(self, toolbar):
        self.bold_action = QAction("B", self, checkable=True)
        self.bold_action.triggered.connect(lambda: self.body_input.setFontWeight(QFont.Bold if self.bold_action.isChecked() else QFont.Normal))
        self.italic_action = QAction("I", self, checkable=True)
        self.italic_action.triggered.connect(lambda checked: self.body_input.setFontItalic(checked))
        self.underline_action = QAction("U", self, checkable=True)
        self.underline_action.triggered.connect(lambda checked: self.body_input.setFontUnderline(checked))
        self.list_action = QAction("• List", self, triggered=self.insert_list_item)
        
        self.align_left_action = QAction("☰", self, triggered=lambda: self.body_input.setAlignment(Qt.AlignLeft))
        self.align_center_action = QAction("═", self, triggered=lambda: self.body_input.setAlignment(Qt.AlignCenter))
        self.align_right_action = QAction("☰", self, triggered=lambda: self.body_input.setAlignment(Qt.AlignRight))
        self.insert_image_action = QAction("🖼️Sisipkan Gambar", self, triggered=self.insert_image)
        self.resize_image_action = QAction("📏Ubah Ukuran Gambar", self, triggered=self.resize_image)
        self.resize_image_action.setEnabled(False)
        
        toolbar.addActions([self.bold_action, self.italic_action, self.underline_action])
        toolbar.addSeparator()
        toolbar.addAction(self.list_action)
        toolbar.addSeparator()
        toolbar.addActions([self.align_left_action, self.align_center_action, self.align_right_action])
        toolbar.addSeparator()
        toolbar.addAction(self.insert_image_action)
        toolbar.addAction(self.resize_image_action)
        toolbar.setStyleSheet("QToolButton:disabled { color: #a0a0a0; }")

    def setup_edit_delete_buttons(self):
        edit_widget = QWidget()
        edit_layout = QHBoxLayout(edit_widget)
        edit_layout.setContentsMargins(0, 0, 0, 0)
        self.edit_btn = QPushButton("Edit Catatan")
        self.edit_btn.setObjectName("edit_btn")
        self.edit_btn.clicked.connect(self.enter_edit_mode)
        edit_layout.addWidget(self.edit_btn)
        
        confirm_widget = QWidget()
        confirm_layout = QHBoxLayout(confirm_widget)
        confirm_layout.setContentsMargins(0, 0, 0, 0)
        confirm_layout.addWidget(QLabel("Centang untuk konfirmasi:"))
        self.confirm_checkbox = QCheckBox()
        self.confirm_checkbox.stateChanged.connect(self.toggle_delete_button)
        self.delete_btn = QPushButton("Hapus Permanen")
        self.delete_btn.setObjectName("delete_btn")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.delete_note)
        self.cancel_btn = QPushButton("Batal")
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.clicked.connect(self.leave_edit_mode)
        
        confirm_layout.addWidget(self.confirm_checkbox)
        confirm_layout.addWidget(self.delete_btn)
        confirm_layout.addWidget(self.cancel_btn)
        
        self.edit_delete_stack.addWidget(edit_widget)
        self.edit_delete_stack.addWidget(confirm_widget)

    def update_toolbar_state(self, fmt):
        self.bold_action.setChecked(fmt.fontWeight() == QFont.Bold)
        self.italic_action.setChecked(fmt.fontItalic())
        self.underline_action.setChecked(fmt.fontUnderline())

    def check_image_at_cursor(self):
        cursor = self.body_input.textCursor()
        self.resize_image_action.setEnabled(self.is_edit_mode and cursor.charFormat().isImageFormat())

    def toggle_delete_button(self, state):
        self.delete_btn.setEnabled(state == Qt.Checked)

    def resize_image(self):
        if not self.is_edit_mode:
            return
        cursor = self.body_input.textCursor()
        fmt = cursor.charFormat()
        if fmt.isImageFormat():
            image_name = fmt.stringProperty(QTextImageFormat.ImageName)
            pixmap = QPixmap(image_name)
            if pixmap.isNull():
                QMessageBox.warning(self, "Kesalahan", "Tidak dapat memuat gambar untuk diubah ukurannya.")
                return
            current_width_cm = pixmap.width() / 96 * 2.54
            new_cm, ok = QInputDialog.getDouble(
                self, "Ubah Ukuran Gambar", "Masukkan lebar baru (cm):",
                round(current_width_cm, 2), 0.1, 100
            )
            if ok:
                new_width = int(new_cm / 2.54 * 96)
                new_height = int(new_width * pixmap.height() / pixmap.width())
                new_fmt = QTextImageFormat()
                new_fmt.setName(image_name)
                new_fmt.setWidth(new_width)
                new_fmt.setHeight(new_height)
                cursor.setCharFormat(new_fmt)
                self.set_dirty()

    def insert_list_item(self):
        if not self.is_edit_mode:
            return
        cursor = self.body_input.textCursor()
        if not cursor.atBlockStart():
            cursor.insertBlock()
        cursor.insertText("• ")
        self.set_dirty()

    def insert_image(self):
        if not self.is_edit_mode:
            return
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Pilih Gambar", "", "Gambar (*.png *.xpm *.jpg *.bmp *.gif)", options=options
        )
        if file_name:
            pixmap = QPixmap(file_name)
            if pixmap.isNull():
                QMessageBox.warning(self, "Kesalahan", "File gambar tidak valid.")
                return
            image_format = QTextImageFormat()
            image_format.setName(file_name)
            max_width = 500
            new_width = min(pixmap.width(), max_width)
            new_height = int(new_width * pixmap.height() / pixmap.width())
            image_format.setWidth(new_width)
            image_format.setHeight(new_height)
            cursor = self.body_input.textCursor()
            cursor.insertImage(image_format)
            self.set_dirty()

    def populate_notes_list(self):
        current_note_id = self.notes[self.current_index].get('id') if self.current_index != -1 and self.notes else None
        self.notes_list.clear()
        row_to_select = -1
        if not self.notes:
            item = QListWidgetItem(self.notes_list)
            motivation_widget = QLabel("<b>Belum ada catatan!</b><br>Mulai tulis ide, mimpi, atau cerita Anda sekarang! ✍️")
            motivation_widget.setStyleSheet("padding: 15px; color: #64748b;")
            motivation_widget.setWordWrap(True)
            motivation_widget.setAlignment(Qt.AlignCenter)
            item.setSizeHint(motivation_widget.sizeHint())
            self.notes_list.setItemWidget(item, motivation_widget)
            item.setFlags(Qt.NoItemFlags)
            self.current_index = -1
            self.update_editor_state(False, False)
            self.update_summary_cards()
            return
        for i, note in enumerate(self.notes):
            item = QListWidgetItem(self.notes_list)
            last_updated = note.get('last_updated', '')
            try:
                date = datetime.strptime(last_updated, "%Y-%m-%d %H:%M:%S")
                date_str = date.strftime("%d %b %Y, %H:%M")
            except (ValueError, TypeError):
                date_str = "Tidak Diketahui"
            preview_text = note.get('content', '')[:40].replace('\n', ' ') + ("..." if len(note.get('content', '')) > 40 else "")
            item_widget = NoteListItem(note.get('title', 'Tanpa Judul'), date_str, preview_text)
            item_widget.adjustSize()
            item.setSizeHint(QSize(item_widget.width(), item_widget.height()))
            self.notes_list.setItemWidget(item, item_widget)
            if note.get('id') == current_note_id:
                row_to_select = i
        if row_to_select != -1:
            self.notes_list.setCurrentRow(row_to_select)
            self.current_index = row_to_select
        else:
            self.current_index = -1
            self.update_editor_state(False, False)
        self.update_summary_cards()

    def search_notes(self):
        search_text = self.search_input.text().strip().lower()
        if not search_text:
            self.populate_notes_list()
            return
        self.notes_list.clear()
        visible_items = 0
        current_note_id = self.notes[self.current_index].get('id') if self.current_index != -1 and self.notes else None
        row_to_select = -1
        for i, note in enumerate(self.notes):
            title = note.get('title', '').lower()
            content = note.get('content', '').lower()
            if search_text in title or search_text in content:
                item = QListWidgetItem(self.notes_list)
                last_updated = note.get('last_updated', '')
                try:
                    date = datetime.strptime(last_updated, "%Y-%m-%d %H:%M:%S")
                    date_str = date.strftime("%d %b %Y, %H:%M")
                except (ValueError, TypeError):
                    date_str = "Tidak Diketahui"
                preview_text = note.get('content', '')[:40].replace('\n', ' ') + ("..." if len(note.get('content', '')) > 40 else "")
                item_widget = NoteListItem(note.get('title', 'Tanpa Judul'), date_str, preview_text)
                item_widget.adjustSize()
                item.setSizeHint(QSize(item_widget.width(), item_widget.height()))
                self.notes_list.setItemWidget(item, item_widget)
                visible_items += 1
                if note.get('id') == current_note_id:
                    row_to_select = visible_items - 1
        if visible_items == 0:
            item = QListWidgetItem(self.notes_list)
            no_result_widget = QLabel("Tidak ada catatan yang sesuai dengan pencarian Anda.")
            no_result_widget.setStyleSheet("padding: 15px; color: #64748b;")
            no_result_widget.setWordWrap(True)
            no_result_widget.setAlignment(Qt.AlignCenter)
            item.setSizeHint(no_result_widget.sizeHint())
            self.notes_list.setItemWidget(item, no_result_widget)
            item.setFlags(Qt.NoItemFlags)
            self.current_index = -1
            self.update_editor_state(False, False)
            self.update_summary_cards()  # Update summary meskipun hasil pencarian kosong
        else:
            if row_to_select != -1:
                self.notes_list.setCurrentRow(row_to_select)
                self.current_index = row_to_select
            else:
                self.current_index = -1
                self.update_editor_state(False, False)
            self.update_summary_cards()  # Update summary untuk total catatan keseluruhan

    def update_editor_state(self, has_selection, is_editing):
        self.is_edit_mode = is_editing
        is_enabled = has_selection or is_editing
        self.title_input.setEnabled(is_enabled)
        self.body_input.setEnabled(is_enabled)
        self.title_input.setReadOnly(not is_editing)
        self.body_input.setReadOnly(not is_editing)
        self.save_btn.setEnabled(is_editing and self.has_unsaved_changes)
        self.edit_btn.setEnabled(has_selection and not is_editing)
        self.edit_delete_stack.setCurrentIndex(1 if is_editing else 0)
        self.bold_action.setEnabled(is_editing)
        self.italic_action.setEnabled(is_editing)
        self.underline_action.setEnabled(is_editing)
        self.list_action.setEnabled(is_editing)
        self.align_left_action.setEnabled(is_editing)
        self.align_center_action.setEnabled(is_editing)
        self.align_right_action.setEnabled(is_editing)
        self.insert_image_action.setEnabled(is_editing)
        self.resize_image_action.setEnabled(is_editing and self.body_input.textCursor().charFormat().isImageFormat())
        self.delete_btn.setEnabled(is_editing and self.confirm_checkbox.isChecked())
        self.cancel_btn.setEnabled(is_editing)
        if not has_selection and not is_editing:
            self.title_input.setText("")
            self.title_input.setPlaceholderText("Pilih catatan atau buat baru")
            self.body_input.clear()
            self.last_edited_label.setText("")

    def new_note(self):
        if self.has_unsaved_changes and self.is_edit_mode:
            reply = QMessageBox.question(
                self, 'Simpan Perubahan?',
                "Anda memiliki perubahan yang belum disimpan. Simpan sekarang?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                self.save_note()
                if self.has_unsaved_changes:
                    return
            else:
                self.notes_list.blockSignals(True)
                if self.current_index != -1:
                    self.notes_list.setCurrentRow(self.current_index)
                else:
                    self.notes_list.setCurrentRow(-1)
                self.notes_list.blockSignals(False)
                self.update_editor_state(self.current_index != -1, True)
                return
        self.leave_edit_mode()
        self.current_index = -1
        self.notes_list.setCurrentRow(-1)
        self.title_input.setText("")
        self.title_input.setPlaceholderText("Judul Catatan Baru...")
        self.body_input.clear()
        self.body_input.setPlaceholderText("Mulai menulis...")
        self.last_edited_label.setText("Catatan belum disimpan")
        self.update_editor_state(False, True)
        self.title_input.setFocus()
        self.has_unsaved_changes = False
        self.save_btn.setEnabled(False)

    def save_note(self):
        if not self.is_edit_mode:
            return
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Peringatan", "Judul tidak boleh kosong.")
            self.has_unsaved_changes = True
            return
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        note_id = self.notes[self.current_index].get('id', str(uuid.uuid4())) if self.current_index != -1 else str(uuid.uuid4())
        note_data = {
            "id": note_id,
            "title": title,
            "content": self.body_input.toPlainText(),
            "html_content": self.body_input.toHtml(),
            "last_updated": timestamp
        }
        if self.current_index == -1:
            self.notes.append(note_data)
        else:
            self.notes[self.current_index] = note_data
        self.notes.sort(key=lambda x: x.get('last_updated', ''), reverse=True)
        self.current_index = next((i for i, n in enumerate(self.notes) if n.get('id') == note_id), -1)
        self.search_notes()
        try:
            self.save_callback()
        except Exception as e:
            QMessageBox.warning(self, "Kesalahan", f"Gagal menyimpan catatan: {str(e)}")
            self.has_unsaved_changes = True
            return
        try:
            self.refresh_callback()
        except Exception as e:
            QMessageBox.warning(self, "Kesalahan", f"Gagal memperbarui catatan: {str(e)}")
        self.update_editor_state(True, False)
        self.has_unsaved_changes = False
        self.save_btn.setEnabled(False)
        if self.current_index != -1 and self.current_index < len(self.notes):
            note = self.notes[self.current_index]
            self.last_edited_label.setText(
                f"Diubah: {QDateTime.fromString(note.get('last_updated', ''), 'yyyy-MM-dd HH:mm:ss').toString('dd MMM yyyy, hh:mm')}"
            )

    def select_note(self, index):
        if index < 0 or index >= self.notes_list.count():
            self.update_editor_state(False, False)
            return
        if self.has_unsaved_changes and self.is_edit_mode:
            reply = QMessageBox.question(
                self, 'Simpan Perubahan?',
                "Anda memiliki perubahan yang belum disimpan. Simpan sekarang?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                self.save_note()
                if self.has_unsaved_changes:
                    self.notes_list.blockSignals(True)
                    self.notes_list.setCurrentRow(self.current_index)
                    self.notes_list.blockSignals(False)
                    return
            else:
                self.notes_list.blockSignals(True)
                self.notes_list.setCurrentRow(self.current_index)
                self.notes_list.blockSignals(False)
                self.update_editor_state(True, True)
                return
        self.current_index = index
        note = self.notes[index]
        self.title_input.setText(note.get("title", ""))
        self.body_input.setHtml(note.get("html_content", ""))
        last_updated = note.get('last_updated', '')
        date_str = QDateTime.fromString(last_updated, "yyyy-MM-dd HH:mm:ss").toString("dd MMM yyyy, hh:mm") if last_updated else "Tidak Diketahui"
        self.last_edited_label.setText(f"Diubah: {date_str}")
        self.update_editor_state(True, False)
        self.has_unsaved_changes = False
        self.save_btn.setEnabled(False)

    def enter_edit_mode(self):
        if self.current_index == -1 or self.current_index >= len(self.notes):
            return
        self.update_editor_state(True, True)
        self.save_btn.setEnabled(self.has_unsaved_changes)

    def leave_edit_mode(self):
        if self.current_index != -1 and self.current_index < len(self.notes):
            note = self.notes[self.current_index]
            self.title_input.setText(note.get("title", ""))
            self.body_input.setHtml(note.get("html_content", ""))
            last_updated = note.get('last_updated', '')
            date_str = QDateTime.fromString(last_updated, "yyyy-MM-dd HH:mm:ss").toString("dd MMM yyyy, hh:mm") if last_updated else "Tidak Diketahui"
            self.last_edited_label.setText(f"Diubah: {date_str}")
        else:
            self.title_input.setText("")
            self.body_input.clear()
            self.last_edited_label.setText("")
        self.update_editor_state(self.current_index != -1, False)
        self.has_unsaved_changes = False
        self.save_btn.setEnabled(False)
        self.confirm_checkbox.setChecked(False)

    def delete_note(self):
        if self.current_index == -1 or self.current_index >= len(self.notes):
            return
        reply = QMessageBox.question(
            self, 'Konfirmasi Hapus',
            "Apakah Anda yakin ingin menghapus catatan ini?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.No:
            return
        self.notes.pop(self.current_index)
        self.new_note()
        self.search_notes()
        try:
            self.save_callback()
        except Exception as e:
            QMessageBox.warning(self, "Kesalahan", f"Gagal menyimpan setelah penghapusan: {str(e)}")
        try:
            self.refresh_callback()
        except Exception as e:
            QMessageBox.warning(self, "Kesalahan", f"Gagal memperbarui setelah penghapusan: {str(e)}")
        self.has_unsaved_changes = False
        self.save_btn.setEnabled(False)

    def to_dict(self):
        return self.notes

    def from_dict(self, data):
        self.notes = data or []
        for note in self.notes:
            if 'id' not in note:
                note['id'] = str(uuid.uuid4())
        self.notes.sort(key=lambda x: x.get('last_updated', ''), reverse=True)
        self.search_notes()
        self.new_note()