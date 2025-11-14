# src/app/views/usuarios/usuarios_view.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout, QMessageBox, QDialog
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from .nuevo_usuario_dialog import NuevoUsuarioDialog
from .editar_usuario_dialog import EditarUsuarioDialog
from ...services.usuarios_service import (
    obtener_usuarios,
    obtener_usuario_por_id,
    eliminar_usuario_por_id
)

class UsuariosView(QWidget):
    def __init__(self, es_admin=True):
        super().__init__()
        self.es_admin = es_admin
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        titulo = QLabel("GESTIÓN DE USUARIOS")
        titulo.setFont(QFont("Segoe UI", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        if self.es_admin:
            btn_agregar = QPushButton("Registrar Nuevo Usuario")
            btn_agregar.clicked.connect(self.agregar_usuario)
            btn_agregar.setMinimumHeight(50)
            btn_agregar.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: #333333;
                    font-weight: bold;
                    border-radius: 5px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #219653;
                }
            """)
            layout.addWidget(btn_agregar)

        self.tabla_usuarios = QTableWidget()
        self.tabla_usuarios.setColumnCount(4)
        self.tabla_usuarios.setHorizontalHeaderLabels(["ID", "Usuario", "Clave", "Rol"])
        self.tabla_usuarios.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_usuarios.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_usuarios.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabla_usuarios)

        if self.es_admin:
            btn_layout = QHBoxLayout()
            btn_layout.setAlignment(Qt.AlignCenter)
            btn_layout.setSpacing(30)

            btn_editar = QPushButton("Editar Usuario")
            btn_editar.setMinimumHeight(50)
            btn_editar.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: #333333;
                    font-weight: bold;
                    border-radius: 5px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            btn_editar.clicked.connect(self.editar_usuario)

            btn_eliminar = QPushButton("Eliminar Usuario")
            btn_eliminar.setMinimumHeight(50)
            btn_eliminar.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: #333333;
                    font-weight: bold;
                    border-radius: 5px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            btn_eliminar.clicked.connect(self.eliminar_usuario)

            btn_layout.addWidget(btn_editar)
            btn_layout.addWidget(btn_eliminar)
            layout.addLayout(btn_layout)
        else:
            mensaje = QLabel("Solo los administradores pueden gestionar usuarios")
            mensaje.setFont(QFont("Arial", 12))
            mensaje.setAlignment(Qt.AlignCenter)
            mensaje.setStyleSheet("color: #e74c3c; font-weight: bold;")
            layout.addWidget(mensaje)

        self.setLayout(layout)
        self.cargar_usuarios()

    def cargar_usuarios(self):
        usuarios = obtener_usuarios()
        self.tabla_usuarios.setRowCount(len(usuarios))
        for row, usuario in enumerate(usuarios):
            # usuarios_service devuelve (id, usuario, rol)
            uid = usuario[0]
            usuario_nombre = usuario[1]
            rol = usuario[2] if len(usuario) > 2 else ""
            self.tabla_usuarios.setItem(row, 0, QTableWidgetItem(str(uid)))
            self.tabla_usuarios.setItem(row, 1, QTableWidgetItem(usuario_nombre))
            # Mostrar placeholder por seguridad, no la clave real
            self.tabla_usuarios.setItem(row, 2, QTableWidgetItem("••••••"))
            self.tabla_usuarios.setItem(row, 3, QTableWidgetItem(rol))

    def agregar_usuario(self):
        dialog = NuevoUsuarioDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.cargar_usuarios()

    def editar_usuario(self):
        fila = self.tabla_usuarios.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Seleccione un usuario para editar")
            return
        usuario_id = int(self.tabla_usuarios.item(fila, 0).text())
        usuario_data = obtener_usuario_por_id(usuario_id)
        if usuario_data:
            dialog = EditarUsuarioDialog(usuario_data, self)
            if dialog.exec() == QDialog.Accepted:
                self.cargar_usuarios()

    def eliminar_usuario(self):
        fila = self.tabla_usuarios.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Seleccione un usuario para eliminar")
            return
        usuario_id = int(self.tabla_usuarios.item(fila, 0).text())
        if usuario_id == 1:
            QMessageBox.warning(self, "Error", "No se puede eliminar al administrador principal")
            return
        respuesta = QMessageBox.question(self, "Confirmar", "¿Eliminar usuario?", QMessageBox.Yes | QMessageBox.No)
        if respuesta == QMessageBox.Yes:
            ok, err = eliminar_usuario_por_id(usuario_id)
            if not ok:
                QMessageBox.critical(self, "Error", err or "No se pudo eliminar el usuario")
                return
            self.cargar_usuarios()
            QMessageBox.information(self, "Éxito", "Usuario eliminado correctamente")