import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QAction, QFileDialog,
    QWidget, QToolBar, QStatusBar, QFontDialog, QMessageBox, QColorDialog,
    QFontComboBox, QComboBox, QSpinBox, QWidgetAction, QLabel, QInputDialog,
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit
)
from PyQt5.QtGui import QIcon, QTextCharFormat, QTextCursor, QFont, QColor, QTextDocument
from PyQt5.QtCore import Qt, QDir
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
        
        self.find_button = QPushButton("Bul")
        self.find_button.clicked.connect(self.find_text)
        button_layout.addWidget(self.find_button)
        
        self.close_button = QPushButton("Kapat")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def find_text(self):
        search_text = self.search_input.text()
        if search_text:
            found = self.parent.editor.find(search_text)
            if not found:
                self.parent.statusBar().showMessage(f"'{search_text}' bulunamadı.")
                # Başa sar
                cursor = self.parent.editor.textCursor()
                cursor.movePosition(QTextCursor.Start)
                self.parent.editor.setTextCursor(cursor)
                self.parent.editor.find(search_text)

class PardusZabitKatibi(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pardus Zabıt Katibi (beta)")
        self.setGeometry(100, 100, 800, 600)
        
        # Varsayılan simge yolu
        self.icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
        if not os.path.exists(self.icon_path):
            self.icon_path = "/home/serhat/Pardus_Zabıt_Katibi/icons/"
        
        # Merkez widget oluştur
        self.editor = QTextEdit()
        self.setCentralWidget(self.editor)
        self.current_file = None

        # Widget'ları oluştur ve boyutlandır
        self.font_family_combo = QFontComboBox(self)
        self.font_family_combo.setFixedWidth(150)
        
        self.font_size_spin = QSpinBox(self)
        self.font_size_spin.setFixedWidth(60)
        self.font_size_spin.setRange(8, 72)
        self.font_size_spin.setValue(12)

        self.create_actions()
        self.create_menus()
        self.create_toolbars()
        self.create_status_bar()

        # Sinyal bağlantıları
        self.editor.selectionChanged.connect(self.update_format_actions)
        self.editor.currentCharFormatChanged.connect(self.update_format_actions)

        self.new_document()

    def get_icon(self, icon_name):
        # İkon dosya adlarını eşle
        icon_mapping = {
            "document-new": "yeni.png",
            "document-open": "aç.png",
            "document-save": "kaydet.png",
            "document-save-as": "farklıkaydet.png",
            "document-export": "pdf.png",
            "document-print": "yazdır.png",
            "application-exit": "kapat.png",
            "edit-undo": "gerial.png",
            "edit-redo": "yinele.png",
            "edit-cut": "kes.png",
            "edit-copy": "kopyala.png",
            "edit-paste": "yapıştır.png",
            "edit-find": "bul.png",
            "format-text-color": "metinrengi.png",
            "format-fill-color": "vurgula.png",
            "format-text-bold": "kalın.png",
            "format-text-italic": "yatık.png",
            "format-text-underline": "altıçizili.png",
            "format-justify-left": "solayasla.png",
            "format-justify-center": "ortala.png",
            "format-justify-right": "sağayasla.png",
            "format-justify-fill": "ikiyanayasla.png"
        }
        
        file_name = icon_mapping.get(icon_name, "")
        if file_name:
            icon_file = os.path.join(self.icon_path, file_name)
            if os.path.exists(icon_file):
                return QIcon(icon_file)
        
        # Fallback: Sistem ikonları
        return QIcon.fromTheme(icon_name)

    def create_actions(self):
        # Dosya Menüsü Eylemleri
        self.new_action = QAction(self.get_icon("document-new"), "Yeni", self)
        self.new_action.setShortcut("Ctrl+N")
        self.new_action.setStatusTip("Yeni boş belge oluştur")
        self.new_action.triggered.connect(self.new_document)

        self.open_action = QAction(self.get_icon("document-open"), "Aç...", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.setStatusTip("Mevcut belgeyi aç")
        self.open_action.triggered.connect(self.open_document)

        self.save_action = QAction(self.get_icon("document-save"), "Kaydet", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.setStatusTip("Belgeyi kaydet")
        self.save_action.triggered.connect(self.save_document)

        self.save_as_action = QAction(self.get_icon("document-save-as"), "Farklı Kaydet...", self)
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        self.save_as_action.setStatusTip("Belgeyi farklı bir isimle kaydet")
        self.save_as_action.triggered.connect(self.save_document_as)
        
        self.save_pdf_action = QAction(self.get_icon("document-export"), "PDF Olarak Kaydet...", self)
        self.save_pdf_action.setStatusTip("Belgeyi PDF olarak kaydet")
        self.save_pdf_action.triggered.connect(self.save_document_as_pdf)

        self.print_action = QAction(self.get_icon("document-print"), "Yazdır...", self)
        self.print_action.setShortcut("Ctrl+P")
        self.print_action.setStatusTip("Belgeyi yazdır")
        self.print_action.triggered.connect(self.print_document)

        self.exit_action = QAction(self.get_icon("application-exit"), "Çıkış", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.setStatusTip("Uygulamadan çık")
        self.exit_action.triggered.connect(self.close)

        # Düzenle Menüsü Eylemleri
        self.undo_action = QAction(self.get_icon("edit-undo"), "Geri Al", self)
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.setStatusTip("Son eylemi geri al")
        self.undo_action.triggered.connect(self.editor.undo)

        self.redo_action = QAction(self.get_icon("edit-redo"), "Yinele", self)
        self.redo_action.setShortcut("Ctrl+Y")
        self.redo_action.setStatusTip("Geri alınan eylemi yinele")
        self.redo_action.triggered.connect(self.editor.redo)

        self.cut_action = QAction(self.get_icon("edit-cut"), "Kes", self)
        self.cut_action.setShortcut("Ctrl+X")
        self.cut_action.setStatusTip("Seçili metni kes")
        self.cut_action.triggered.connect(self.editor.cut)

        self.copy_action = QAction(self.get_icon("edit-copy"), "Kopyala", self)
        self.copy_action.setShortcut("Ctrl+C")
        self.copy_action.setStatusTip("Seçili metni kopyala")
        self.copy_action.triggered.connect(self.editor.copy)

        self.paste_action = QAction(self.get_icon("edit-paste"), "Yapıştır", self)
        self.paste_action.setShortcut("Ctrl+V")
        self.paste_action.setStatusTip("Panodaki metni yapıştır")
        self.paste_action.triggered.connect(self.editor.paste)

        self.find_action = QAction(self.get_icon("edit-find"), "Bul...", self)
        self.find_action.setShortcut("Ctrl+F")
        self.find_action.setStatusTip("Belgede metin ara")
        self.find_action.triggered.connect(self.show_find_dialog)

        # Biçimlendirme Eylemleri
        self.font_family_combo.currentFontChanged.connect(self.editor.setCurrentFont)
        self.font_family_combo.setStatusTip("Yazı tipi ailesini seç")

        self.font_size_spin.valueChanged.connect(lambda size: self.editor.setFontPointSize(size))
        self.font_size_spin.setStatusTip("Yazı tipi boyutunu ayarla")

        self.text_color_action = QAction(self.get_icon("format-text-color"), "Metin Rengi...", self)
        self.text_color_action.setStatusTip("Metin rengini seç")
        self.text_color_action.triggered.connect(self.select_text_color)
        
        self.highlight_color_action = QAction(self.get_icon("format-fill-color"), "Vurgu Rengi...", self)
        self.highlight_color_action.setStatusTip("Metin vurgu (arka plan) rengini seç")
        self.highlight_color_action.triggered.connect(self.select_highlight_color)

        self.bold_action = QAction(self.get_icon("format-text-bold"), "Kalın", self)
        self.bold_action.setShortcut("Ctrl+B")
        self.bold_action.setStatusTip("Metni kalın yap")
        self.bold_action.setCheckable(True)
        self.bold_action.triggered.connect(self.toggle_bold)

        self.italic_action = QAction(self.get_icon("format-text-italic"), "İtalik", self)
        self.italic_action.setShortcut("Ctrl+I")
        self.italic_action.setStatusTip("Metni italik yap")
        self.italic_action.setCheckable(True)
        self.italic_action.triggered.connect(self.toggle_italic)

        self.underline_action = QAction(self.get_icon("format-text-underline"), "Altı Çizili", self)
        self.underline_action.setShortcut("Ctrl+U")
        self.underline_action.setStatusTip("Metnin altını çiz")
        self.underline_action.setCheckable(True)
        self.underline_action.triggered.connect(self.toggle_underline)

        # Hizalama Eylemleri
        self.align_left_action = QAction(self.get_icon("format-justify-left"), "Sola Hizala", self)
        self.align_left_action.setStatusTip("Metni sola hizala")
        self.align_left_action.triggered.connect(lambda: self.editor.setAlignment(Qt.AlignLeft))

        self.align_center_action = QAction(self.get_icon("format-justify-center"), "Ortala", self)
        self.align_center_action.setStatusTip("Metni ortala")
        self.align_center_action.triggered.connect(lambda: self.editor.setAlignment(Qt.AlignCenter))

        self.align_right_action = QAction(self.get_icon("format-justify-right"), "Sağa Hizala", self)
        self.align_right_action.setStatusTip("Metni sağa hizala")
        self.align_right_action.triggered.connect(lambda: self.editor.setAlignment(Qt.AlignRight))

        self.align_justify_action = QAction(self.get_icon("format-justify-fill"), "İki Yana Yasla", self)
        self.align_justify_action.setStatusTip("Metni iki yana yasla")
        self.align_justify_action.triggered.connect(lambda: self.editor.setAlignment(Qt.AlignJustify))

    def create_menus(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("&Dosya")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addAction(self.save_pdf_action)
        file_menu.addSeparator()
        file_menu.addAction(self.print_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        edit_menu = menubar.addMenu("&Düzenle")
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.cut_action)
        edit_menu.addAction(self.copy_action)
        edit_menu.addAction(self.paste_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.find_action)

        format_menu = menubar.addMenu("&Biçim")
        font_combo_action = QWidgetAction(self)
        font_combo_action.setDefaultWidget(self.font_family_combo)
        format_menu.addAction(font_combo_action)

        font_size_action = QWidgetAction(self)
        font_size_action.setDefaultWidget(self.font_size_spin)
        format_menu.addAction(font_size_action)
        
        format_menu.addSeparator()
        format_menu.addAction(self.text_color_action)
        format_menu.addAction(self.highlight_color_action)
        format_menu.addSeparator()
        format_menu.addAction(self.bold_action)
        format_menu.addAction(self.italic_action)
        format_menu.addAction(self.underline_action)
        format_menu.addSeparator()
        format_menu.addAction(self.align_left_action)
        format_menu.addAction(self.align_center_action)
        format_menu.addAction(self.align_right_action)
        format_menu.addAction(self.align_justify_action)

    def create_toolbars(self):
        # 1. Araç Çubuğu - Dosya İşlemleri
        self.file_toolbar = self.addToolBar("Dosya")
        self.file_toolbar.addAction(self.new_action)
        self.file_toolbar.addAction(self.open_action)
        self.file_toolbar.addAction(self.save_action)
        self.file_toolbar.addAction(self.save_as_action)
        self.file_toolbar.addAction(self.save_pdf_action)
        self.file_toolbar.addAction(self.print_action)
        self.file_toolbar.addSeparator()
        self.file_toolbar.addAction(self.undo_action)
        self.file_toolbar.addAction(self.redo_action)
        self.file_toolbar.addAction(self.cut_action)
        self.file_toolbar.addAction(self.copy_action)
        self.file_toolbar.addAction(self.paste_action)
        self.file_toolbar.addAction(self.find_action)

        # 2. Araç Çubuğu - Biçimlendirme
        self.addToolBarBreak()
        self.format_toolbar = self.addToolBar("Biçimlendirme")
        
        # Yazı Tipi Kontrolleri
        font_label = QLabel("Yazı Tipi:")
        self.format_toolbar.addWidget(font_label)
        self.format_toolbar.addWidget(self.font_family_combo)
        
        size_label = QLabel("Boyut:")
        self.format_toolbar.addWidget(size_label)
        self.format_toolbar.addWidget(self.font_size_spin)
        
        # Biçimlendirme Butonları
        self.format_toolbar.addSeparator()
        self.format_toolbar.addAction(self.bold_action)
        self.format_toolbar.addAction(self.italic_action)
        self.format_toolbar.addAction(self.underline_action)
        self.format_toolbar.addSeparator()
        self.format_toolbar.addAction(self.text_color_action)
        self.format_toolbar.addAction(self.highlight_color_action)
        self.format_toolbar.addSeparator()
        self.format_toolbar.addAction(self.align_left_action)
        self.format_toolbar.addAction(self.align_center_action)
        self.format_toolbar.addAction(self.align_right_action)
        self.format_toolbar.addAction(self.align_justify_action)

    def create_status_bar(self):
        self.statusBar().showMessage("Hazır")

    def show_find_dialog(self):
        dialog = FindDialog(self)
        dialog.exec_()

    def new_document(self):
        self.editor.clear()
        self.current_file = None
        self.setWindowTitle("Pardus Zabıt Katibi (beta) - Yeni Belge")
        self.statusBar().showMessage("Yeni boş belge oluşturuldu.")

    def open_document(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Belge Aç", "", "HTML Dosyaları (*.html);;Metin Dosyaları (*.txt);;Tüm Dosyalar (*.*)")
        if file_name:
            try:
                with open(file_name, "r", encoding="utf-8") as f:
                    if file_name.endswith(".html"):
                        self.editor.setHtml(f.read())
                    else:
                        self.editor.setPlainText(f.read()) 
                self.current_file = file_name
                self.setWindowTitle(f"Pardus Zabıt Katibi (beta) - {file_name}")
                self.statusBar().showMessage(f"'{file_name}' açıldı.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dosya açılırken hata oluştu: {e}")
                self.statusBar().showMessage(f"Dosya açılırken hata oluştu: {e}")

    def save_document(self):
        if self.current_file:
            try:
                with open(self.current_file, "w", encoding="utf-8") as f:
                    if self.current_file.endswith(".html"):
                        f.write(self.editor.toHtml())
                    else:
                        f.write(self.editor.toPlainText())
                self.statusBar().showMessage(f"'{self.current_file}' kaydedildi.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dosya kaydedilirken hata oluştu: {e}")
                self.statusBar().showMessage(f"Dosya kaydedilirken hata oluştu: {e}")
        else:
            self.save_document_as()

    def save_document_as(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Belgeyi Farklı Kaydet", "", "HTML Dosyaları (*.html);;Metin Dosyaları (*.txt);;Tüm Dosyalar (*.*)")
        if file_name:
            try:
                with open(file_name, "w", encoding="utf-8") as f:
                    if file_name.endswith(".html"):
                        f.write(self.editor.toHtml())
                    else:
                        f.write(self.editor.toPlainText())
                self.current_file = file_name
                self.setWindowTitle(f"Pardus Zabıt Katibi (beta) - {file_name}")
                self.statusBar().showMessage(f"'{file_name}' kaydedildi.")
            except Exception as e:
                QMessageBox.critical(self.editor, "Hata", f"Dosya kaydedilirken hata oluştu: {e}")
                self.statusBar().showMessage(f"Dosya kaydedilirken hata oluştu: {e}")
    
    def save_document_as_pdf(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "PDF Olarak Kaydet", "", "PDF Dosyaları (*.pdf)")
        if file_name:
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
        current_format = self.editor.currentCharFormat()
        
        # Font ayarları
        self.font_family_combo.blockSignals(True)
        self.font_family_combo.setCurrentFont(current_format.font())
        self.font_family_combo.blockSignals(False)
        
        self.font_size_spin.blockSignals(True)
        self.font_size_spin.setValue(int(current_format.fontPointSize()))
        self.font_size_spin.blockSignals(False)
        
        # Diğer biçimlendirmeler
        self.bold_action.setChecked(current_format.fontWeight() == QFont.Bold)
        self.italic_action.setChecked(current_format.fontItalic())
        self.underline_action.setChecked(current_format.fontUnderline())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = PardusZabitKatibi()
    editor.show()
    sys.exit(app.exec_())
