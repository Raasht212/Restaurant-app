from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QHBoxLayout, QPushButton, QMessageBox, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from .controller import actualizar_mesa, obtener_secciones

class EditarMesaDialog(QDialog):
    def __init__(self, mesa, parent=None):
        super().__init__(parent)
        # mesa: (id, numero, estado, seccion)
        self.mesa = mesa
        self.setWindowTitle("Editar Mesa")
        self.setFixedSize(360, 260)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        titulo = QLabel("EDITAR MESA")
        titulo.setFont(QFont("Arial", 14, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        form = QFormLayout()
        self.input_numero = QLineEdit(str(self.mesa[1]))
        form.addRow("Número:", self.input_numero)

        self.combo_estado = QComboBox()
        self.combo_estado.addItems(["libre", "ocupada", "reservada"])
        self.combo_estado.setCurrentText(self.mesa[2])
        form.addRow("Estado:", self.combo_estado)

        self.combo_seccion = QComboBox()
        secciones = obtener_secciones()
        if secciones:
            self.combo_seccion.addItems(secciones)
        else:
            self.combo_seccion.addItems(["Principal", "Terraza", "Privada"])
        self.combo_seccion.setCurrentText(self.mesa[3])
        form.addRow("Sección:", self.combo_seccion)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btn_ok = QPushButton("Guardar")
        btn_ok.clicked.connect(self.guardar)
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_ok)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def guardar(self):
        numero_text = self.input_numero.text().strip()
        estado = self.combo_estado.currentText()
        seccion = self.combo_seccion.currentText()
        if not numero_text.isdigit():
            QMessageBox.warning(self, "Error", "Número inválido")
            return
        numero = int(numero_text)
        ok = actualizar_mesa(self.mesa[0], numero, estado, seccion)
        if ok:
            QMessageBox.information(self, "Éxito", "Mesa actualizada")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "No se pudo actualizar la mesa (posible número duplicado)")