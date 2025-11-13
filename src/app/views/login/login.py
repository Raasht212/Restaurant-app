# src/app/views/login/login.py
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from ..main_window import MainWindow  # si main_window.py está en src/app/views/main_window.py
from pathlib import Path
from src.app.config import BASE_DIR

from ...db.connection import crear_conexion

from ...db.connection import ConnectionManager
with ConnectionManager() as conn:
    cur = conn.cursor()
    ...

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Restaurante - Login")
        self.setFixedSize(500, 400)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(25)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Logo
        logo_label = QLabel()
        icon_path = BASE_DIR.joinpath("src","app","resources", "icons", "logo3.png")
        pixmap = QPixmap(str(icon_path))
        if not pixmap.isNull():
            pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)
        
        # Título
        titulo = QLabel("SISTEMA RESTAURANTE")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        #titulo.setStyleSheet("color: #800020;")
        layout.addWidget(titulo)
        
        # Campos de entrada
        campos_layout = QVBoxLayout()
        campos_layout.setSpacing(15)
        
        self.input_usuario = QLineEdit()
        self.input_usuario.setPlaceholderText("Usuario")
        self.input_usuario.setMinimumHeight(45)
        self.input_usuario.setStyleSheet("padding: 10px;")
        
        self.input_clave = QLineEdit()
        self.input_clave.setPlaceholderText("Contraseña")
        self.input_clave.setEchoMode(QLineEdit.Password)
        self.input_clave.setMinimumHeight(45)
        self.input_clave.setStyleSheet("padding: 10px;")
        
        campos_layout.addWidget(self.input_usuario)
        campos_layout.addWidget(self.input_clave)
        
        layout.addLayout(campos_layout)
        
        # Botón
        btn_login = QPushButton("INGRESAR")
        btn_login.setMinimumHeight(50)
        btn_login.setStyleSheet("""
            QPushButton {
                background-color: #800020;
                color: #F5F5DC;
                font-weight: bold;
                border-radius: 5px;
                font-size: 14pt;
            }
            QPushButton:hover {
                background-color: #900028;
            }
        """)
        btn_login.clicked.connect(self.validar_login)
        
        layout.addWidget(btn_login)
        
        self.setLayout(layout)
    
    def validar_login(self):
        usuario = self.input_usuario.text()
        clave = self.input_clave.text()
        
        if not usuario or not clave:
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return
        
        conexion = crear_conexion()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute(
                    "SELECT id, nombre, rol FROM usuarios WHERE usuario = ? AND clave = ?",
                    (usuario, clave)
                )
                usuario_data = cursor.fetchone()
                
                if usuario_data:
                    self.main_window = MainWindow(usuario_data)
                    self.main_window.show()
                    self.close()
                else:
                    QMessageBox.critical(self, "Error", "Credenciales incorrectas")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error de base de datos: {str(e)}")
            finally:
                conexion.close()