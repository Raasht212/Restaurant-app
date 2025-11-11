import sys
from PySide6.QtWidgets import QApplication, QColorDialog, QPlainTextDocumentLayout
from views.login import LoginWindow
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon, QFont, QColor, QPalette

def main():
    app = QApplication(sys.argv)
    # En main.py al iniciar la app
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#F5F5DC"))
    palette.setColor(QPalette.Base, QColor("#800020"))
    palette.setColor(QPalette.Text, QColor("#800020"))
    app.setPalette(palette)
    
    # Cargar estilos
    with open("styles.qss", "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())
    
    login_window = LoginWindow()
    login_window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()