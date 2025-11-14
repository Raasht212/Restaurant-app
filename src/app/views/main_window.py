# src/app/views/main_window.py
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel,
    QStackedWidget, QToolBar, QStatusBar, QMessageBox, 
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont, QAction

# Vistas (imports relativos dentro del paquete)
from src.app.views.mesas.mesas_view import MesasView
from src.app.views.inventario.inventario import InventarioView
from src.app.views.usuarios.usuarios_view import UsuariosView


# Intentamos importar ReportesView; si no existe, seguir sin él
try:
    from .reportes.reportes_view import ReportesView
    _HAS_REPORTES = True
except Exception:
    _HAS_REPORTES = False

class MainWindow(QMainWindow):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle("Sistema de Gestión de Restaurante")
        self.setMinimumSize(1200, 800)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Toolbar
        toolbar = QToolBar("Menú Principal")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(toolbar)

        # Stacked widget para vistas
        self.stacked_widget = QStackedWidget()

        # Instanciar vistas
        self.mesas_view = MesasView()
        self.inventario_view = InventarioView(es_admin=(self.usuario[2] == "admin"))
        self.usuarios_view = UsuariosView(es_admin=(self.usuario[2] == "admin"))

        # Añadir reportes solo si está disponible
        if _HAS_REPORTES:
            self.reportes_view = ReportesView()
            self.stacked_widget.addWidget(self.reportes_view)

        # Añadir las demás vistas
        self.stacked_widget.addWidget(self.mesas_view)
        self.stacked_widget.addWidget(self.inventario_view)
        self.stacked_widget.addWidget(self.usuarios_view)

        # Acciones del toolbar (añadir solo las que correspondan)
        acciones = [
            ("Mesas", "mesa.png", self.mostrar_mesas),
            ("Inventario", "inventario.png", self.mostrar_inventario),
        ]
        if _HAS_REPORTES:
            acciones.append(("Reportes", "reportes.png", self.mostrar_reportes))
        if self.usuario and len(self.usuario) > 2 and self.usuario[2] == "admin":
            acciones.append(("Usuarios", "usuarios.png", self.mostrar_usuarios))

        for nombre, icono, funcion in acciones:
            act = QAction(QIcon(f"resources/icons/{icono}"), nombre, self)
            act.triggered.connect(funcion)
            toolbar.addAction(act)
            toolbar.addSeparator()

        # Status bar con info de usuario y botón cerrar sesión
        status_bar = QStatusBar()
        usuario_label = QLabel(f"Usuario: {self.usuario[1]} ({self.usuario[2]})")
        usuario_label.setStyleSheet("font-weight: bold; color: #800020;")
        status_bar.addPermanentWidget(usuario_label)

        btn_cerrar_sesion = QPushButton("Cerrar Sesión")
        btn_cerrar_sesion.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_cerrar_sesion.clicked.connect(self.cerrar_sesion)
        status_bar.addPermanentWidget(btn_cerrar_sesion)
        self.setStatusBar(status_bar)

        # Montar layout central
        main_layout.addWidget(self.stacked_widget)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Mostrar vista por defecto
        self.mostrar_mesas()

    # Métodos para cambiar vistas
    def mostrar_mesas(self):
        self.stacked_widget.setCurrentWidget(self.mesas_view)
        if hasattr(self.mesas_view, "actualizar_mesas"):
            try:
                self.mesas_view.actualizar_mesas()
            except Exception:
                pass

    def mostrar_inventario(self):
        self.stacked_widget.setCurrentWidget(self.inventario_view)
        if hasattr(self.inventario_view, "cargar_productos"):
            try:
                self.inventario_view.cargar_productos()
            except Exception:
                pass

    def mostrar_usuarios(self):
        self.stacked_widget.setCurrentWidget(self.usuarios_view)
        if hasattr(self.usuarios_view, "cargar_usuarios"):
            try:
                self.usuarios_view.cargar_usuarios()
            except Exception:
                pass

    def mostrar_reportes(self):
        if not _HAS_REPORTES:
            QMessageBox.information(self, "Reportes", "El módulo de reportes no está disponible")
            return
        self.stacked_widget.setCurrentWidget(self.reportes_view)
        if hasattr(self.reportes_view, "cargar_datos"):
            try:
                self.reportes_view.cargar_datos()
            except Exception:
                pass

    # Import local para romper import circular con login
    def cerrar_sesion(self):
        from .login.login import LoginWindow  # import relativo dentro del método
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()