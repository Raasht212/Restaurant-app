# src/app/views/usuarios/usuarios_view.py
from functools import partial

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QHBoxLayout, QMessageBox,
    QDialog, QWidgetItem, QAbstractItemView
)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt, QSize

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
        # Columnas: ID, Nombre, Apellido, Usuario, Rol, Acciones
        self.tabla_usuarios.setColumnCount(5)
        self.tabla_usuarios.setHorizontalHeaderLabels(
            ["Nombre", "Apellido", "Usuario", "Rol", "Acciones"]
        )
        self.tabla_usuarios.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_usuarios.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_usuarios.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabla_usuarios)

        # Si es admin mostramos botones globales opcionales (ya no necesarios)
        if self.es_admin:
            # dejamos espacio para posibles acciones globales
            pass
        else:
            mensaje = QLabel("Solo los administradores pueden gestionar usuarios")
            mensaje.setFont(QFont("Arial", 12))
            mensaje.setAlignment(Qt.AlignCenter)
            mensaje.setStyleSheet("color: #e74c3c; font-weight: bold;")
            layout.addWidget(mensaje)

        self.setLayout(layout)
        self.cargar_usuarios()

    def _crear_widget_acciones(self, usuario_id):
        """Crea un QWidget con los botones Editar y Eliminar para insertar en la celda."""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        btn_editar = QPushButton("")
        btn_editar.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: #fff;
                border-radius: 4px;
                padding: 6px 8px;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        btn_editar.setFixedSize(QSize(45, 25))
        btn_editar.setCursor(Qt.PointingHandCursor)
        btn_editar.setIcon(QIcon("src/app/resources/icons/editar.png"))
        btn_editar.clicked.connect(partial(self._on_editar_click, usuario_id))

        btn_eliminar = QPushButton("")
        btn_eliminar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: #fff;
                border-radius: 4px;
                padding: 6px 8px;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        btn_eliminar.setFixedSize(QSize(45, 25))
        btn_eliminar.setCursor(Qt.PointingHandCursor)
        btn_eliminar.setIcon(QIcon("src/app/resources/icons/eliminar.png"))
        btn_eliminar.clicked.connect(partial(self._on_eliminar_click, usuario_id))

        layout.addWidget(btn_editar)
        layout.addWidget(btn_eliminar)

        return container

    def cargar_usuarios(self):
        usuarios = obtener_usuarios()
        # usuarios expected: list of tuples.
        # support multiple shapes:
        # (id, nombre, apellido, usuario, rol)
        # (id, nombre, usuario, rol)
        # (id, nombre, apellido, usuario, clave, rol)
        self.tabla_usuarios.setRowCount(len(usuarios))
        for row, usuario in enumerate(usuarios):
            uid = usuario[0]
            # defensively extract fields
            nombre = ""
            apellido = ""
            usuario_nombre = ""
            rol = ""
            if len(usuario) >= 5:
                # likely (id, nombre, apellido, usuario, rol) or (id,nombre,apellido,usuario,clave,rol)
                nombre = usuario[1]
                # if position 2 is apellido (string and not role)
                apellido = usuario[2] if isinstance(usuario[2], str) else ""
                # usuario (username) likely at pos 3
                usuario_nombre = usuario[3] if len(usuario) > 3 else ""
                # try to find rol at last position
                rol = usuario[-1] if isinstance(usuario[-1], str) else ""
            else:
                # fallback older shape (id, nombre, usuario, rol)
                nombre = usuario[1] if len(usuario) > 1 else ""
                usuario_nombre = usuario[2] if len(usuario) > 2 else ""
                rol = usuario[3] if len(usuario) > 3 else ""

            
            self.tabla_usuarios.setItem(row, 0, QTableWidgetItem(nombre))
            self.tabla_usuarios.setItem(row, 1, QTableWidgetItem(apellido))
            self.tabla_usuarios.setItem(row, 2, QTableWidgetItem(usuario_nombre))
            self.tabla_usuarios.setItem(row, 3, QTableWidgetItem(rol))

            # acciones: widget con botones
            acciones_widget = self._crear_widget_acciones(uid)
            self.tabla_usuarios.setCellWidget(row, 4, acciones_widget)

        # Ajustes de visualización adicionales
        self.tabla_usuarios.resizeRowsToContents()

    def agregar_usuario(self):
        dialog = NuevoUsuarioDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.cargar_usuarios()

    def _on_editar_click(self, usuario_id):
        usuario_data = obtener_usuario_por_id(usuario_id)
        if not usuario_data:
            QMessageBox.warning(self, "Error", "No se encontró el usuario")
            return
        dialog = EditarUsuarioDialog(usuario_data, self)
        if dialog.exec() == QDialog.Accepted:
            self.cargar_usuarios()

    def _on_eliminar_click(self, usuario_id):
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