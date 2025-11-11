from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QDialog, QFormLayout,
    QLineEdit, QComboBox, QDialogButtonBox, QMessageBox, 
    QLabel, QHBoxLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon, QPixmap
from database import crear_conexion, sqlite3

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
        
        # Título
        titulo = QLabel("REGISTRAR NUEVO USUARIO")
        titulo.setFont(QFont("Arial", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("color: #800020;")
        layout.addWidget(titulo)
        
        # Campos de entrada
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
        
        # Botones
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
            
        conexion = crear_conexion()
        if conexion:
            try:
                cursor = conexion.cursor()
                
                # Verificar si el usuario ya existe
                cursor.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = ?", (usuario,))
                if cursor.fetchone()[0] > 0:
                    QMessageBox.warning(self, "Error", "El nombre de usuario ya está en uso")
                    return
                
                # Insertar nuevo usuario
                cursor.execute(
                    "INSERT INTO usuarios (nombre, usuario, clave, rol) VALUES (?, ?, ?, ?)",
                    (nombre, usuario, clave, rol)
                )
                conexion.commit()
                
                QMessageBox.information(self, "Éxito", "Usuario registrado correctamente")
                self.accept()
                
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Error", "El nombre de usuario ya está en uso")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al registrar usuario: {str(e)}")
            finally:
                conexion.close()

class EditarUsuarioDialog(QDialog):
    def __init__(self, usuario, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Usuario")
        self.usuario = usuario  # (id, nombre, usuario, clave, rol)
        self.setFixedSize(500, 400)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        titulo = QLabel("EDITAR USUARIO")
        titulo.setFont(QFont("Arial", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("color: #800020;")
        layout.addWidget(titulo)
        
        # Campos de entrada
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        self.input_nombre = QLineEdit(self.usuario[1])
        self.input_nombre.setMinimumHeight(45)
        self.input_nombre.setStyleSheet("padding: 10px;")
        
        self.input_usuario = QLineEdit(self.usuario[2])
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
        self.combo_rol.setCurrentText(self.usuario[4])
        self.combo_rol.setMinimumHeight(45)
        self.combo_rol.setStyleSheet("padding: 10px;")
        
        form_layout.addRow("Nombre:", self.input_nombre)
        form_layout.addRow("Usuario:", self.input_usuario)
        form_layout.addRow("Nueva Contraseña:", self.input_clave)
        form_layout.addRow("Confirmar:", self.input_confirmar_clave)
        form_layout.addRow("Rol:", self.combo_rol)
        
        layout.addLayout(form_layout)
        
        # Botones
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
            
        conexion = crear_conexion()
        if conexion:
            try:
                cursor = conexion.cursor()
                
                # Verificar si el usuario ya existe (excluyendo el actual)
                cursor.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = ? AND id != ?", 
                              (usuario, self.usuario[0]))
                if cursor.fetchone()[0] > 0:
                    QMessageBox.warning(self, "Error", "El nombre de usuario ya está en uso")
                    return
                
                # Actualizar usuario
                if clave:
                    cursor.execute(
                        "UPDATE usuarios SET nombre=?, usuario=?, clave=?, rol=? WHERE id=?",
                        (nombre, usuario, clave, rol, self.usuario[0]))
                else:
                    cursor.execute(
                        "UPDATE usuarios SET nombre=?, usuario=?, rol=? WHERE id=?",
                        (nombre, usuario, rol, self.usuario[0]))
                
                conexion.commit()
                
                QMessageBox.information(self, "Éxito", "Usuario actualizado correctamente")
                self.accept()
                
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Error", "El nombre de usuario ya está en uso")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al actualizar usuario: {str(e)}")
            finally:
                conexion.close()

class UsuariosView(QWidget):
    def __init__(self, es_admin=True):  # Cambiado a True por defecto para pruebas
        super().__init__()
        self.es_admin = es_admin
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Título
        titulo = QLabel("GESTIÓN DE USUARIOS")
        titulo.setFont(QFont("Segoe UI", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setObjectName("titulo")
        layout.addWidget(titulo)
        
        # Botón para agregar usuario - siempre visible para admin
        if self.es_admin:
            btn_agregar = QPushButton("Registrar Nuevo Usuario")
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
            btn_agregar.clicked.connect(self.agregar_usuario)
            layout.addWidget(btn_agregar)
        
        # Tabla de usuarios
        self.tabla_usuarios = QTableWidget()
        self.tabla_usuarios.setColumnCount(4)
        self.tabla_usuarios.setHorizontalHeaderLabels(["ID", "Usuario", "Clave", "Rol"])
        self.tabla_usuarios.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_usuarios.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.tabla_usuarios)
        
        # Botones de acción - siempre visibles para admin
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
            # Mensaje para usuarios no administradores
            mensaje = QLabel("Solo los administradores pueden gestionar usuarios")
            mensaje.setFont(QFont("Arial", 12))
            mensaje.setAlignment(Qt.AlignCenter)
            mensaje.setStyleSheet("color: #e74c3c; font-weight: bold;")
            layout.addWidget(mensaje)
        
        self.setLayout(layout)
        self.cargar_usuarios()
    
    def cargar_usuarios(self):
        conexion = crear_conexion()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute("SELECT id, usuario, clave, rol FROM usuarios")
                usuarios = cursor.fetchall()
                
                self.tabla_usuarios.setRowCount(len(usuarios))
                
                for row, usuario in enumerate(usuarios):
                    self.tabla_usuarios.setItem(row, 0, QTableWidgetItem(str(usuario[0])))
                    self.tabla_usuarios.setItem(row, 1, QTableWidgetItem(usuario[1]))
                    self.tabla_usuarios.setItem(row, 2, QTableWidgetItem(usuario[2]))
                    self.tabla_usuarios.setItem(row, 3, QTableWidgetItem(usuario[3]))
                    
            except Exception as e:
                print(f"Error cargando usuarios: {e}")
            finally:
                conexion.close()
    
    def agregar_usuario(self):
        dialog = NuevoUsuarioDialog(self)
        if dialog.exec():
            self.cargar_usuarios()
    
    def editar_usuario(self):
        fila = self.tabla_usuarios.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Seleccione un usuario para editar")
            return
            
        usuario_id = int(self.tabla_usuarios.item(fila, 0).text())
        nombre = self.tabla_usuarios.item(fila, 1).text()
        usuario = self.tabla_usuarios.item(fila, 2).text()
        rol = self.tabla_usuarios.item(fila, 3).text()
        
        # Obtener datos completos del usuario
        conexion = crear_conexion()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute("SELECT id, nombre, usuario, clave, rol FROM usuarios WHERE id = ?", (usuario_id,))
                usuario_data = cursor.fetchone()
                
                if usuario_data:
                    dialog = EditarUsuarioDialog(usuario_data, self)
                    if dialog.exec():
                        self.cargar_usuarios()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al obtener datos del usuario: {str(e)}")
            finally:
                conexion.close()
    
    def eliminar_usuario(self):
        fila = self.tabla_usuarios.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Seleccione un usuario para eliminar")
            return
            
        usuario_id = int(self.tabla_usuarios.item(fila, 0).text())
        nombre = self.tabla_usuarios.item(fila, 1).text()
        
        # No permitir eliminar al administrador principal
        if usuario_id == 1:
            QMessageBox.warning(self, "Error", "No se puede eliminar al administrador principal")
            return
            
        respuesta = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro de eliminar al usuario '{nombre}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if respuesta == QMessageBox.Yes:
            conexion = crear_conexion()
            if conexion:
                try:
                    cursor = conexion.cursor()
                    cursor.execute("DELETE FROM usuarios WHERE id=?", (usuario_id,))
                    conexion.commit()
                    self.cargar_usuarios()
                    QMessageBox.information(self, "Éxito", "Usuario eliminado correctamente")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error al eliminar usuario: {str(e)}")
                finally:
                    conexion.close()