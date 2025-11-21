import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import QTranslator, QLibraryInfo

from src.app.logging_config import configure_logging
from src.app.db.init_db import inicializar_base_datos
from src.app.views.login.login import LoginWindow
from src.app.config import resource_path
from pathlib import Path


def main():
    configure_logging()
    inicializar_base_datos()

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    translator = QTranslator(app)
    translator.load("qt_es", QLibraryInfo.path(QLibraryInfo.TranslationsPath))
    app.installTranslator(translator)



    # Paleta básica
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#303030"))
    palette.setColor(QPalette.Base, QColor("#FFFFFF"))
    palette.setColor(QPalette.Text, QColor("#000000"))
    app.setPalette(palette)

    # ✅ Cargar estilos desde resource_path (compatible con PyInstaller)
    qss_file = resource_path("src", "app", "resources", "qss", "styles.qss")
    print("Cargando estilos desde:", qss_file)
    print("Cargando estilos desde:", qss_file)
    try:
        with open(qss_file, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
            print("Estilos cargados desde:", qss_file)
    except Exception as e:
        print("No se pudo cargar styles.qss:", e)

    # Ventana inicial
    login_window = LoginWindow()
    login_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()