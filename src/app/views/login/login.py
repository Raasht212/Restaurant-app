from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from ..main_window import MainWindow
from src.app.config import BASE_DIR
from ...db.connection import crear_conexion


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Restaurante - Login")
        self.setFixedSize(900, 500)
        self.setup_ui()

    def setup_ui(self):
        from PySide6.QtWidgets import QHBoxLayout, QSizePolicy

        # Layout principal horizontal
        layout_principal = QHBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        # --- Lado izquierdo: imagen a pantalla completa ---
        frame_izquierdo = QFrame()
        frame_izquierdo.setObjectName("frame_izquierdo")
        frame_izquierdo.setMinimumWidth(500)
        frame_izquierdo.setStyleSheet("QFrame#frame_izquierdo { border-top-left-radius: 10px; border-bottom-left-radius: 10px; overflow: hidden; }")

        layout_izquierdo = QVBoxLayout(frame_izquierdo)
        layout_izquierdo.setContentsMargins(0, 0, 0, 0)
        layout_izquierdo.setSpacing(0)

        imagen_path = BASE_DIR / "src" / "app" / "resources" / "images" / "login_image.jpg"
        imagen_label = QLabel()
        imagen_label.setObjectName("imagen_label")
        pix = QPixmap(str(imagen_path))
        imagen_label.setPixmap(pix)
        imagen_label.setScaledContents(True)                # fuerza a llenar el widget
        imagen_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        imagen_label.setAlignment(Qt.AlignCenter)

        layout_izquierdo.addWidget(imagen_label)

        # --- Lado derecho: formulario en modo oscuro ---
        frame_derecho = QFrame()
        frame_derecho.setObjectName("frame_derecho")
        frame_derecho.setStyleSheet("""
            QFrame#frame_derecho {
                background-color: #1e2b3a;                /* color oscuro de fondo */
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
                
            }
            QLabel { color: #e6eef7; }
            QLineEdit {
                background-color: #2b3946;
                color: #e6eef7;
                border: 1px solid #34495e;
                border-radius: 6px;
                padding: 8px;
            }
            QPushButton#btn_login {
                background-color: #800020;
                color: #F5F5DC;
                font-weight: bold;
                border-radius: 6px;
                padding: 12px;
            }
            QPushButton#btn_login:hover { background-color: #900028; }
        """)
        layout_derecho = QVBoxLayout(frame_derecho)
        layout_derecho.setContentsMargins(36, 36, 36, 36)
        layout_derecho.setSpacing(18)
        layout_derecho.setAlignment(Qt.AlignCenter)
        #centrar verticalmente
        layout_derecho.addStretch(1)

        titulo = QLabel("Inicia sesión")
        titulo.setFont(QFont("Arial", 18, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)

        self.input_usuario = QLineEdit()
        self.input_usuario.setPlaceholderText("Usuario")
        self.input_usuario.setMinimumHeight(44)

        self.input_clave = QLineEdit()
        self.input_clave.setPlaceholderText("Contraseña")
        self.input_clave.setEchoMode(QLineEdit.Password)
        self.input_clave.setMinimumHeight(44)

        btn_login = QPushButton("INGRESAR")
        btn_login.setObjectName("btn_login")
        btn_login.setMinimumHeight(48)
        btn_login.clicked.connect(self.validar_login)

        # Opcional: enlace de "olvidé mi contraseña"
        link_forgot = QLabel("<a style='color:#9fb7d6' href='#'>¿Olvidaste tu contraseña?</a>")
        link_forgot.setTextFormat(Qt.RichText)
        link_forgot.setTextInteractionFlags(Qt.TextBrowserInteraction)
        link_forgot.setAlignment(Qt.AlignCenter)

        # Agregar widgets al layout derecho
        layout_derecho.addWidget(titulo)
        layout_derecho.addWidget(self.input_usuario)
        layout_derecho.addWidget(self.input_clave)
        layout_derecho.addWidget(btn_login)
        layout_derecho.addWidget(link_forgot)
        layout_derecho.addStretch(1)

        # Añadir ambos frames al layout principal (izq: imagen, der: formulario)
        layout_principal.addWidget(frame_izquierdo, 1)   # peso 1
        layout_principal.addWidget(frame_derecho, 1)     # peso 1 (ajusta si quieres proporciones distintas)

        # Forzar redraw y tamaño correcto
        imagen_label.update()
        frame_izquierdo.update()
        frame_derecho.update()

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