from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QHBoxLayout, QPushButton, QMessageBox, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from .controller import crear_mesa, obtener_secciones

class NuevoMesaDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Mesa")
        self.setFixedSize(360, 220)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        titulo = QLabel("CREAR MESA")
        titulo.setFont(QFont("Arial", 14, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        form = QFormLayout()
        self.input_numero = QLineEdit()
        self.input_numero.setPlaceholderText("Número de mesa")
        self.input_numero.setMinimumHeight(40)
        form.addRow("Número:", self.input_numero)

        self.combo_seccion = QComboBox()
        secciones = obtener_secciones()
        if secciones:
            self.combo_seccion.addItems(secciones)
        else:
            self.combo_seccion.addItems(["Principal", "Terraza", "Privada"])
        form.addRow("Sección:", self.combo_seccion)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btn_ok = QPushButton("Crear")
        btn_ok.clicked.connect(self.crear)
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_ok)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def crear(self):
        numero_text = self.input_numero.text().strip()
        seccion = self.combo_seccion.currentText()
        if not numero_text.isdigit():
            QMessageBox.warning(self, "Error", "Número inválido")
            return
        numero = int(numero_text)
        ok = crear_mesa(numero, seccion)
        if ok:
            QMessageBox.information(self, "Éxito", "Mesa creada")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "No se pudo crear la mesa (posible duplicado)")