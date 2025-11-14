# src/app/views/usuarios/nuevo_usuario_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QHBoxLayout, QPushButton, QMessageBox, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ...services.usuarios_service import registrar_usuario

class NuevoUsuarioDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Nuevo Usuario")
        self.setFixedSize(500, 400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        titulo = QLabel("REGISTRAR NUEVO USUARIO")
        titulo.setFont(QFont("Arial", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("color: #800020;")
        layout.addWidget(titulo)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre completo")
        self.input_nombre.setMinimumHeight(45)
        self.input_nombre.setStyleSheet("padding: 10px;")

        self.input_usuario = QLineEdit()
        self.input_usuario.setPlaceholderText("Nombre de usuario")
        self.input_usuario.setMinimumHeight(45)
        self.input_usuario.setStyleSheet("padding: 10px;")

        self.input_clave = QLineEdit()
        self.input_clave.setPlaceholderText("Contraseña")
        self.input_clave.setEchoMode(QLineEdit.Password)
        self.input_clave.setMinimumHeight(45)
        self.input_clave.setStyleSheet("padding: 10px;")

        self.input_confirmar_clave = QLineEdit()
        self.input_confirmar_clave.setPlaceholderText("Confirmar contraseña")
        self.input_confirmar_clave.setEchoMode(QLineEdit.Password)
        self.input_confirmar_clave.setMinimumHeight(45)
        self.input_confirmar_clave.setStyleSheet("padding: 10px;")

        self.combo_rol = QComboBox()
        self.combo_rol.addItems(["admin", "cajero"])
        self.combo_rol.setMinimumHeight(45)
        self.combo_rol.setStyleSheet("padding: 10px;")

        form_layout.addRow("Nombre:", self.input_nombre)
        form_layout.addRow("Usuario:", self.input_usuario)
        form_layout.addRow("Contraseña:", self.input_clave)
        form_layout.addRow("Confirmar:", self.input_confirmar_clave)
        form_layout.addRow("Rol:", self.combo_rol)

        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        btn_guardar = QPushButton("Guardar Usuario")
        btn_guardar.setMinimumHeight(50)
        btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: #333333;
                font-weight: bold;
                border-radius: 5px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        btn_guardar.clicked.connect(self.validar_registro)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setMinimumHeight(50)
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: #333333;
                font-weight: bold;
                border-radius: 5px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_cancelar.clicked.connect(self.reject)

        btn_layout.addWidget(btn_cancelar)
        btn_layout.addWidget(btn_guardar)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def validar_registro(self):
        nombre = self.input_nombre.text().strip()
        usuario = self.input_usuario.text().strip()
        clave = self.input_clave.text()
        confirmar = self.input_confirmar_clave.text()
        rol = self.combo_rol.currentText()

        if not nombre or not usuario or not clave or not confirmar:
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return

        if clave != confirmar:
            QMessageBox.warning(self, "Error", "Las contraseñas no coinciden")
            return

        if len(clave) < 4:
            QMessageBox.warning(self, "Error", "La contraseña debe tener al menos 4 caracteres")
            return

        ok, err = registrar_usuario(nombre, usuario, clave, rol)
        if ok:
            QMessageBox.information(self, "Éxito", "Usuario registrado correctamente")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", err or "El nombre de usuario ya está en uso o hubo un error")