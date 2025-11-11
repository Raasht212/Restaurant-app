from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QStackedWidget, QToolBar, QStatusBar, QMessageBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon, QFont
from views.mesas import MesasView
from views.inventario.inventario import InventarioView
from views.usuarios import UsuariosView
from views.reportes.reportes import ReportesView
from PySide6.QtCore import QPropertyAnimation, QEasingCurve

def mostrar_mesas(self):
    self.animate_transition(self.mesas_view)
    
def animate_transition(self, widget):
    animation = QPropertyAnimation(self.stacked_widget, b"fade")
    animation.setDuration(300)
    animation.setStartValue(0)
    animation.setEndValue(1)
    animation.setEasingCurve(QEasingCurve.OutCubic)
    self.stacked_widget.setCurrentWidget(widget)
    animation.start()

try:
    from views.reportes.reportes import ReportesView
    tiene_reportes = True
except ImportError:
    tiene_reportes = False
    print("Advertencia: Módulo de reportes no encontrado")

class MainWindow(QMainWindow):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        print(f"Usuario logueado: {usuario}")  # Para depuración
        self.setWindowTitle("Sistema de Gestión de Restaurante")
        self.setMinimumSize(1200, 800)
        self.setup_ui()
        
    def setup_ui(self):
        # Widget central
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Barra de herramientas
        toolbar = QToolBar("Menú Principal")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(toolbar)
        
        # Botones del menú
        acciones = [
            ("Mesas", "mesa.png", self.mostrar_mesas),
            ("Inventario", "inventario.png", self.mostrar_inventario),
            ("Reportes", "reportes.png", self.mostrar_reportes) if tiene_reportes else None,
            ("Usuarios", "usuarios.png", self.mostrar_usuarios) if self.usuario[2] == "admin" else None
        ]
        
        for accion in acciones:
            if accion:
                nombre, icono, funcion = accion
                act = QAction(QIcon(f"resources/icons/{icono}"), nombre, self)
                act.triggered.connect(funcion)
                toolbar.addAction(act)
                toolbar.addSeparator()
        
        # Área de contenido
        self.stacked_widget = QStackedWidget()
        
        # Vistas - PASAR CORRECTAMENTE EL PARÁMETRO ES_ADMIN
        self.mesas_view = MesasView()
        self.inventario_view = InventarioView(es_admin=(self.usuario[2] == "admin"))
        self.usuarios_view = UsuariosView(es_admin=(self.usuario[2] == "admin"))
        
        if tiene_reportes:
            self.reportes_view = ReportesView()
            self.stacked_widget.addWidget(self.reportes_view)
        
        self.stacked_widget.addWidget(self.mesas_view)
        self.stacked_widget.addWidget(self.inventario_view)
        self.stacked_widget.addWidget(self.usuarios_view)
        
        # Barra de estado
        status_bar = QStatusBar()
        usuario_label = QLabel(f"Usuario: {self.usuario[1]} ({self.usuario[2]})")
        usuario_label.setStyleSheet("font-weight: bold; color: #800020;")
        status_bar.addPermanentWidget(usuario_label)
        
        # Botón para cerrar sesión
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
        
        # Diseño
        main_layout.addWidget(self.stacked_widget)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Mostrar mesas por defecto
        self.mostrar_mesas()
    
    def cerrar_sesion(self):
        from views.login.login import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()
        
    def mostrar_mesas(self):
        self.stacked_widget.setCurrentWidget(self.mesas_view)
        self.mesas_view.actualizar_mesas()
        
    def mostrar_inventario(self):
        self.stacked_widget.setCurrentWidget(self.inventario_view)
        self.inventario_view.cargar_productos()
        
    def mostrar_usuarios(self):
        self.stacked_widget.setCurrentWidget(self.usuarios_view)
        self.usuarios_view.cargar_usuarios()
        
    def mostrar_reportes(self):
        if tiene_reportes:
            self.stacked_widget.setCurrentWidget(self.reportes_view)
            self.reportes_view.cargar_datos()
        else:
            QMessageBox.information(self, "Información", "Módulo de reportes no disponible aún")