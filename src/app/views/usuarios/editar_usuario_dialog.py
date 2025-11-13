# src/app/views/usuarios/editar_usuario_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QHBoxLayout, QPushButton, QMessageBox, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ...services.usuarios_service import actualizar_usuario

class EditarUsuarioDialog(QDialog):
    def __init__(self, usuario, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Usuario")
        # usuario esperado: (id, nombre, usuario, rol) ó (id, nombre, usuario, clave, rol)
        self.usuario = usuario
        self.setFixedSize(500, 400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        titulo = QLabel("EDITAR USUARIO")
        titulo.setFont(QFont("Arial", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("color: #800020;")
        layout.addWidget(titulo)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        # Algunas vistas pueden pasar tuplas con diferente orden; manejamos defensivamente
        # usuario puede ser (id, nombre, usuario, rol) o (id, nombre, usuario, clave, rol)
        nombre_val = self.usuario[1] if len(self.usuario) > 1 else ""
        usuario_val = self.usuario[2] if len(self.usuario) > 2 else ""
        rol_val = self.usuario[4] if len(self.usuario) > 4 else (self.usuario[3] if len(self.usuario) > 3 else "cajero")

        self.input_nombre = QLineEdit(nombre_val)
        self.input_nombre.setMinimumHeight(45)
        self.input_nombre.setStyleSheet("padding: 10px;")

        self.input_usuario = QLineEdit(usuario_val)
        self.input_usuario.setMinimumHeight(45)
        self.input_usuario.setStyleSheet("padding: 10px;")

        self.input_clave = QLineEdit()
        self.input_clave.setPlaceholderText("Dejar vacío para no cambiar")
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
        self.combo_rol.setCurrentText(rol_val)
        self.combo_rol.setMinimumHeight(45)
        self.combo_rol.setStyleSheet("padding: 10px;")

        form_layout.addRow("Nombre:", self.input_nombre)
        form_layout.addRow("Usuario:", self.input_usuario)
        form_layout.addRow("Nueva Contraseña:", self.input_clave)
        form_layout.addRow("Confirmar:", self.input_confirmar_clave)
        form_layout.addRow("Rol:", self.combo_rol)

        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        btn_guardar = QPushButton("Guardar Cambios")
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
        btn_guardar.clicked.connect(self.validar_edicion)

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

    def validar_edicion(self):
        nombre = self.input_nombre.text().strip()
        usuario = self.input_usuario.text().strip()
        clave = self.input_clave.text()
        confirmar = self.input_confirmar_clave.text()
        rol = self.combo_rol.currentText()

        if not nombre or not usuario:
            QMessageBox.warning(self, "Error", "Nombre y usuario son obligatorios")
            return

        if clave and clave != confirmar:
            QMessageBox.warning(self, "Error", "Las contraseñas no coinciden")
            return

        if clave and len(clave) < 4:
            QMessageBox.warning(self, "Error", "La contraseña debe tener al menos 4 caracteres")
            return

        # actualizar_usuario ahora devuelve (ok, err)
        ok, err = actualizar_usuario(self.usuario[0], nombre, usuario, clave or None, rol)
        if ok:
            QMessageBox.information(self, "Éxito", "Usuario actualizado correctamente")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", err or "El nombre de usuario ya está en uso o hubo un error")