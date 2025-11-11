from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class ReportesView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        titulo = QLabel("REPORTES")
        titulo.setFont(QFont("Segoe UI", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setObjectName("titulo")
        layout.addWidget(titulo)
        
        mensaje = QLabel("Módulo en construcción")
        mensaje.setAlignment(Qt.AlignCenter)
        layout.addWidget(mensaje)
        
        self.setLayout(layout)
    
    def cargar_datos(self):
        pass  # Implementaremos esto más adelante