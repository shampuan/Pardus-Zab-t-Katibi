import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QAction, QFileDialog,
    QWidget, QToolBar, QStatusBar, QMessageBox, QColorDialog,
    QFontComboBox, QSpinBox, QLabel, QDialog,
    QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit
)
from PyQt5.QtGui import QIcon, QTextCharFormat, QFont, QColor, QTextCursor, QTextDocument
from PyQt5.QtCore import Qt
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter

class FindDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bul")
        self.parent = parent
        
        layout = QVBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Aranacak metin...")
        layout.addWidget(self.search_input)
        
        button_layout = QHBoxLayout()
        
        self.find_next_button = QPushButton("Sıradakini Bul")
        self.find_next_button.clicked.connect(self.find_next)
        button_layout.addWidget(self.find_next_button)

        self.find_prev_button = QPushButton("Öncekini Bul")
        self.find_prev_button.clicked.connect(self.find_previous)
        button_layout.addWidget(self.find_prev_button)
        
        self.close_button = QPushButton("Kapat")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def find_next(self):
        search_text = self.search_input.text()
        if search_text:
            found = self.parent.editor.find(search_text)
            if not found:
                self.parent.statusBar().showMessage(f"'{search_text}' bulunamadı.")
                cursor = self.parent.editor.textCursor()
                cursor.movePosition(QTextCursor.Start)
                self.parent.editor.setTextCursor(cursor)
                # Başa dönüp tekrar dene
                self.parent.editor.find(search_text)

    def find_previous(self):
        search_text = self.search_input.text()
        if search_text:
            # Geriye doğru arama yapmak için FindBackward bayrağını kullan
            found = self.parent.editor.find(search_text, QTextDocument.FindFlag.FindBackward)
            if not found:
                self.parent.statusBar().showMessage(f"'{search_text}' bulunamadı.")
                cursor = self.parent.editor.textCursor()
                cursor.movePosition(QTextCursor.End)
                self.parent.editor.setTextCursor(cursor)
                # Sona dönüp tekrar geriye doğru dene
                self.parent.editor.find(search_text, QTextDocument.FindFlag.FindBackward)

class PardusZabitKatibi(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pardus Zabıt Katibi")
        self.setGeometry(100, 100, 800, 600)
        
        self.icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
        if not os.path.exists(self.icon_path):
            self.icon_path = "/home/serhat/Pardus_Zabıt_Katibi/icons/"
        
        self.editor = QTextEdit()
        self.setCentralWidget(self.editor)
        self.current_file = None
        
        self.default_font = QFont("Liberation Serif", 12)
        self.editor.setFont(self.default_font)

        self.font_family_combo = None
        self.font_size_spin = None

        self.create_actions()
        self.create_menus()
        self.create_toolbars()
        self.create_status_bar()

        self.editor.selectionChanged.connect(self.update_format_actions)
        self.editor.currentCharFormatChanged.connect(self.update_format_actions)
        
        self.new_document()

    def get_icon(self, icon_name):
        icon_mapping = {
            "document-new": "yeni.png", "document-open": "aç.png",
            "document-save": "kaydet.png", "document-save-as": "farklıkaydet.png",
            "document-export": "pdf.png", "document-print": "yazdır.png",
            "application-exit": "kapat.png", "edit-undo": "gerial.png",
            "edit-redo": "yinele.png", "edit-cut": "kes.png",
            "edit-copy": "kopyala.png", "edit-paste": "yapıştır.png",
            "edit-find": "bul.png", "format-text-color": "metinrengi.png",
            "format-fill-color": "vurgula.png", "format-text-bold": "kalın.png",
            "format-text-italic": "yatık.png", "format-text-underline": "altıçizili.png",
            "format-justify-left": "solayasla.png", "format-justify-center": "ortala.png",
            "format-justify-right": "sağayasla.png", "format-justify-fill": "ikiyanayasla.png"
        }
        
        file_name = icon_mapping.get(icon_name, "")
        if file_name:
            icon_file = os.path.join(self.icon_path, file_name)
            if os.path.exists(icon_file):
                return QIcon(icon_file)
        
        return QIcon.fromTheme(icon_name)

    def create_actions(self):
        self.new_action = QAction(self.get_icon("document-new"), "Yeni", self, shortcut="Ctrl+N", statusTip="Yeni boş belge oluştur", triggered=self.new_document)
        self.open_action = QAction(self.get_icon("document-open"), "Aç...", self, shortcut="Ctrl+O", statusTip="Mevcut belgeyi aç", triggered=self.open_document)
        self.save_action = QAction(self.get_icon("document-save"), "Kaydet", self, shortcut="Ctrl+S", statusTip="Belgeyi kaydet", triggered=self.save_document)
        self.save_as_action = QAction(self.get_icon("document-save-as"), "Farklı Kaydet...", self, shortcut="Ctrl+Shift+S", statusTip="Belgeyi farklı bir isimle (.zbt, .html veya .txt) kaydet", triggered=self.save_document_as)
        self.save_pdf_action = QAction(self.get_icon("document-export"), "PDF Olarak Kaydet...", self, statusTip="Belgeyi PDF olarak kaydet", triggered=self.save_document_as_pdf)
        self.print_action = QAction(self.get_icon("document-print"), "Yazdır...", self, shortcut="Ctrl+P", statusTip="Belgeyi yazdır", triggered=self.print_document)
        self.exit_action = QAction(self.get_icon("application-exit"), "Çıkış", self, shortcut="Ctrl+Q", statusTip="Uygulamadan çık", triggered=self.close)

        self.undo_action = QAction(self.get_icon("edit-undo"), "Geri Al", self, shortcut="Ctrl+Z", statusTip="Son eylemi geri al", triggered=self.editor.undo)
        self.redo_action = QAction(self.get_icon("edit-redo"), "Yinele", self, shortcut="Ctrl+Y", statusTip="Geri alınan eylemi yinele", triggered=self.editor.redo)
        self.cut_action = QAction(self.get_icon("edit-cut"), "Kes", self, shortcut="Ctrl+X", statusTip="Seçili metni kes", triggered=self.editor.cut)
        self.copy_action = QAction(self.get_icon("edit-copy"), "Kopyala", self, shortcut="Ctrl+C", statusTip="Seçili metni kopyala", triggered=self.editor.copy)
        self.paste_action = QAction(self.get_icon("edit-paste"), "Yapıştır", self, shortcut="Ctrl+V", statusTip="Panodaki metni yapıştır", triggered=self.editor.paste)
        self.find_action = QAction(self.get_icon("edit-find"), "Bul...", self, shortcut="Ctrl+F", statusTip="Belgede metin ara", triggered=self.show_find_dialog)

        self.text_color_action = QAction(self.get_icon("format-text-color"), "Metin Rengi...", self, statusTip="Metin rengini seç", triggered=self.select_text_color)
        self.highlight_color_action = QAction(self.get_icon("format-fill-color"), "Vurgu Rengi...", self, statusTip="Metin vurgu (arka plan) rengini seç", triggered=self.select_highlight_color)
        self.bold_action = QAction(self.get_icon("format-text-bold"), "Kalın", self, shortcut="Ctrl+B", statusTip="Metni kalın yap", checkable=True, triggered=self.toggle_bold)
        self.italic_action = QAction(self.get_icon("format-text-italic"), "İtalik", self, shortcut="Ctrl+I", statusTip="Metni italik yap", checkable=True, triggered=self.toggle_italic)
        self.underline_action = QAction(self.get_icon("format-text-underline"), "Altı Çizili", self, shortcut="Ctrl+U", statusTip="Metnin altını çiz", checkable=True, triggered=self.toggle_underline)
        
        self.align_left_action = QAction(self.get_icon("format-justify-left"), "Sola Hizala", self, statusTip="Metni sola hizala", triggered=lambda: self.editor.setAlignment(Qt.AlignLeft))
        self.align_center_action = QAction(self.get_icon("format-justify-center"), "Ortala", self, statusTip="Metni ortala", triggered=lambda: self.editor.setAlignment(Qt.AlignCenter))
        self.align_right_action = QAction(self.get_icon("format-justify-right"), "Sağa Hizala", self, statusTip="Metni sağa hizala", triggered=lambda: self.editor.setAlignment(Qt.AlignRight))
        self.align_justify_action = QAction(self.get_icon("format-justify-fill"), "İki Yana Yasla", self, statusTip="Metni iki yana yasla", triggered=lambda: self.editor.setAlignment(Qt.AlignJustify))

        self.about_action = QAction("Hakkında", self, statusTip="Program hakkında bilgi", triggered=self.show_about_dialog)

    def create_menus(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("&Dosya")
        file_menu.addActions([self.new_action, self.open_action, self.save_action, self.save_as_action, self.save_pdf_action])
        file_menu.addSeparator()
        file_menu.addAction(self.print_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        edit_menu = menubar.addMenu("&Düzenle")
        edit_menu.addActions([self.undo_action, self.redo_action])
        edit_menu.addSeparator()
        edit_menu.addActions([self.cut_action, self.copy_action, self.paste_action])
        edit_menu.addSeparator()
        edit_menu.addAction(self.find_action)
        
        format_menu = menubar.addMenu("&Biçim")
        format_menu.addActions([self.bold_action, self.italic_action, self.underline_action])
        format_menu.addSeparator()
        format_menu.addActions([self.text_color_action, self.highlight_color_action])
        format_menu.addSeparator()
        format_menu.addActions([self.align_left_action, self.align_center_action, self.align_right_action, self.align_justify_action])
        
        help_menu = menubar.addMenu("&Yardım")
        help_menu.addAction(self.about_action)

    def create_toolbars(self):
        self.file_toolbar = self.addToolBar("Dosya")
        self.file_toolbar.setMovable(False)
        self.file_toolbar.addActions([self.new_action, self.open_action, self.save_action, self.save_as_action, self.save_pdf_action, self.print_action])
        self.file_toolbar.addSeparator()
        self.file_toolbar.addActions([self.undo_action, self.redo_action, self.cut_action, self.copy_action, self.paste_action, self.find_action])
        
        self.addToolBarBreak()

        self.format_toolbar = self.addToolBar("Biçimlendirme")
        self.format_toolbar.setMovable(False)
        
        self.font_family_combo = QFontComboBox(self)
        self.font_family_combo.setFixedWidth(150)
        
        self.font_size_spin = QSpinBox(self)
        self.font_size_spin.setFixedWidth(60)
        self.font_size_spin.setRange(8, 72)
        self.font_size_spin.setValue(12)

        self.format_toolbar.addWidget(QLabel("Yazıtipi:"))
        self.format_toolbar.addWidget(self.font_family_combo)
        self.format_toolbar.addSeparator()
        
        self.format_toolbar.addWidget(QLabel("Boyut:"))
        self.format_toolbar.addWidget(self.font_size_spin)
        self.format_toolbar.addSeparator()
        
        self.format_toolbar.addActions([self.bold_action, self.italic_action, self.underline_action])
        self.format_toolbar.addSeparator()
        self.format_toolbar.addActions([self.text_color_action, self.highlight_color_action])
        self.format_toolbar.addSeparator()
        self.format_toolbar.addActions([self.align_left_action, self.align_center_action, self.align_right_action, self.align_justify_action])
        
        self.font_family_combo.currentFontChanged.connect(self.editor.setCurrentFont)
        self.font_size_spin.valueChanged.connect(lambda size: self.editor.setFontPointSize(size))
        
    def create_status_bar(self):
        self.statusBar().showMessage("Hazır")

    def show_find_dialog(self):
        dialog = FindDialog(self)
        dialog.exec_()

    def show_about_dialog(self):
        about_text = """
        <h3>Pardus Zabıt Katibi</h3>
        <p>Versiyon: 1.0.2</p>
        <p>Lisans: GNU GPLv3</p>
        <p>Geliştirici: A. Serhat KILIÇOĞLU</p>
        <p>Github: <a href='https://www.github.com/shampuan'>www.github.com/shampuan</a></p>
        <hr>
        <p>Bu program, basit bir WYSIWYG (What You See Is What You Get) editörüdür ve .zbt uzantılı HTML metin dosyaları oluşturur.</p>
        <p>Bu program hiçbir garanti getirmez.</p>
        """
        QMessageBox.about(self, "Hakkında", about_text)
        
    def new_document(self):
        self.editor.clear()
        self.current_file = None
        self.setWindowTitle("Pardus Zabıt Katibi - Yeni Belge")
        self.statusBar().showMessage("Yeni boş belge oluşturuldu.")
        self.editor.setCurrentFont(self.default_font)

    def open_document(self):
        file_filters = "Pardus Zabıt Katibi Dosyaları (*.zbt);;HTML Dosyaları (*.html);;Metin Dosyaları (*.txt);;Tüm Dosyalar (*.*)"
        file_name, _ = QFileDialog.getOpenFileName(self, "Belge Aç", "", file_filters)
        if file_name:
            try:
                with open(file_name, "r", encoding="utf-8") as f:
                    if file_name.endswith(".html") or file_name.endswith(".zbt"):
                        self.editor.setHtml(f.read())
                    else:
                        self.editor.setPlainText(f.read())
                self.current_file = file_name
                self.setWindowTitle(f"Pardus Zabıt Katibi - {file_name}")
                self.statusBar().showMessage(f"'{file_name}' açıldı.")
                self.editor.setCurrentFont(self.default_font)
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dosya açılırken hata oluştu: {e}")
                self.statusBar().showMessage(f"Dosya açılırken hata oluştu: {e}")

    def save_document(self):
        if self.current_file:
            try:
                if not os.path.splitext(self.current_file)[1]:
                    self.current_file += ".zbt"

                if self.current_file.endswith(".html") or self.current_file.endswith(".zbt"):
                    with open(self.current_file, "w", encoding="utf-8") as f:
                        f.write(self.editor.toHtml())
                else:
                    with open(self.current_file, "w", encoding="utf-8") as f:
                        f.write(self.editor.toPlainText())
                self.statusBar().showMessage(f"'{self.current_file}' kaydedildi.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dosya kaydedilirken hata oluştu: {e}")
                self.statusBar().showMessage(f"Dosya kaydedilirken hata oluştu: {e}")
        else:
            self.save_document_as()

    def save_document_as(self):
        file_filters = "Pardus Zabıt Katibi Dosyaları (*.zbt);;HTML Dosyaları (*.html);;Metin Dosyaları (*.txt);;Tüm Dosyalar (*.*)"
        file_name, selected_filter = QFileDialog.getSaveFileName(self, "Belgeyi Farklı Kaydet", "", file_filters, "Pardus Zabıt Katibi Dosyaları (*.zbt)")
        
        if file_name:
            if not os.path.splitext(file_name)[1]:
                if "(*.zbt)" in selected_filter:
                    file_name += ".zbt"
                elif "(*.html)" in selected_filter:
                    file_name += ".html"
                elif "(*.txt)" in selected_filter:
                    file_name += ".txt"
            
            try:
                if file_name.endswith(".html") or file_name.endswith(".zbt"):
                    with open(file_name, "w", encoding="utf-8") as f:
                        f.write(self.editor.toHtml())
                else:
                    with open(file_name, "w", encoding="utf-8") as f:
                        f.write(self.editor.toPlainText())
                self.current_file = file_name
                self.setWindowTitle(f"Pardus Zabıt Katibi - {file_name}")
                self.statusBar().showMessage(f"'{file_name}' kaydedildi.")
            except Exception as e:
                QMessageBox.critical(self.editor, "Hata", f"Dosya kaydedilirken hata oluştu: {e}")
                self.statusBar().showMessage(f"Dosya kaydedilirken hata oluştu: {e}")
    
    def save_document_as_pdf(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "PDF Olarak Kaydet", "", "PDF Dosyaları (*.pdf)")
        if file_name:
            if not os.path.splitext(file_name)[1]:
                file_name += ".pdf"
            try:
                printer = QPrinter(QPrinter.HighResolution)
                printer.setOutputFormat(QPrinter.PdfFormat)
                printer.setOutputFileName(file_name)
                self.editor.document().setTextWidth(printer.pageRect().width())
                self.editor.document().print_(printer)
                self.statusBar().showMessage(f"'{file_name}' PDF olarak kaydedildi.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"PDF kaydederken hata oluştu: {e}")
                self.statusBar().showMessage(f"PDF kaydederken hata oluştu: {e}")

    def print_document(self):
        printer = QPrinter()
        print_dialog = QPrintDialog(printer, self)
        if print_dialog.exec_() == QPrintDialog.Accepted:
            self.editor.print_(printer)

    def select_text_color(self):
        color = QColorDialog.getColor(self.editor.textColor(), self)
        if color.isValid():
            self.editor.setTextColor(color)

    def select_highlight_color(self):
        color = QColorDialog.getColor(self.editor.textBackgroundColor(), self)
        if color.isValid():
            self.editor.setTextBackgroundColor(color)

    def toggle_bold(self):
        current_format = self.editor.currentCharFormat()
        new_format = QTextCharFormat(current_format)
        new_format.setFontWeight(QFont.Bold if self.bold_action.isChecked() else QFont.Normal)
        self.editor.setCurrentCharFormat(new_format)
        self.update_format_actions()

    def toggle_italic(self):
        current_format = self.editor.currentCharFormat()
        new_format = QTextCharFormat(current_format)
        new_format.setFontItalic(self.italic_action.isChecked())
        self.editor.setCurrentCharFormat(new_format)
        self.update_format_actions()

    def toggle_underline(self):
        current_format = self.editor.currentCharFormat()
        new_format = QTextCharFormat(current_format)
        new_format.setFontUnderline(self.underline_action.isChecked())
        self.editor.setCurrentCharFormat(new_format)
        self.update_format_actions()

    def update_format_actions(self):
        if self.font_family_combo and self.font_size_spin:
            current_format = self.editor.currentCharFormat()
            
            self.font_family_combo.blockSignals(True)
            self.font_family_combo.setCurrentFont(current_format.font())
            self.font_family_combo.blockSignals(False)
            
            self.font_size_spin.blockSignals(True)
            self.font_size_spin.setValue(int(current_format.fontPointSize()))
            self.font_size_spin.blockSignals(False)
            
            self.bold_action.setChecked(current_format.fontWeight() == QFont.Bold)
            self.italic_action.setChecked(current_format.fontItalic())
            self.underline_action.setChecked(current_format.fontUnderline())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = PardusZabitKatibi()
    editor.show()
    sys.exit(app.exec_())
