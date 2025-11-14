# src/app/main.py
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor

from src.app.logging_config import configure_logging
from src.app.config import BASE_DIR
from src.app.db.init_db import inicializar_base_datos
from src.app.views.login.login import LoginWindow

from PySide6.QtCore import QFileSystemWatcher

def load_styles(app: QApplication):
    qss_path = BASE_DIR.joinpath("src", "app", "resources", "qss", "styles.qss")
    if qss_path.exists():
        with qss_path.open("r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
        print("Estilos recargados desde:", qss_path)

def main():
    configure_logging()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#303030"))
    palette.setColor(QPalette.Base, QColor("#FFFFFF"))
    palette.setColor(QPalette.Text, QColor("#000000"))
    app.setPalette(palette)

    # Cargar QSS inicial
    load_styles(app)

    # Configurar watcher con ruta absoluta
    qss_path = BASE_DIR.joinpath("src", "app", "resources", "qss", "styles.qss")
    watcher = QFileSystemWatcher([str(qss_path)])
    watcher.fileChanged.connect(lambda: load_styles(app))


    login_window = LoginWindow()
    login_window.show()

    sys.exit(app.exec())


inicializar_base_datos()

if __name__ == "__main__":
    main()