from PySide6.QtWidgets import QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
import datetime
from ...services import conversion_service

class TasaView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tasa del Día USD ↔ VES")
        self.resize(400, 300)

        layout = QVBoxLayout(self)

        # Entrada de tasa
        hlayout = QHBoxLayout()
        self.input_tasa = QLineEdit()
        self.input_tasa.setPlaceholderText("Ingrese tasa del día (ej: 45.50)")
        btn_guardar = QPushButton("Guardar Tasa")
        btn_guardar.clicked.connect(self.guardar_tasa)
        hlayout.addWidget(QLabel("Tasa:"))
        hlayout.addWidget(self.input_tasa)
        hlayout.addWidget(btn_guardar)
        layout.addLayout(hlayout)

        # Conversión rápida
        conv_layout = QHBoxLayout()
        self.input_usd = QLineEdit()
        self.input_usd.setPlaceholderText("Monto en USD")
        btn_convertir = QPushButton("Convertir a VES")
        btn_convertir.clicked.connect(self.convertir)
        self.label_resultado = QLabel("Resultado: -")
        conv_layout.addWidget(self.input_usd)
        conv_layout.addWidget(btn_convertir)
        conv_layout.addWidget(self.label_resultado)
        layout.addLayout(conv_layout)

        # Historial
        self.tabla = QTableWidget(0, 2)
        self.tabla.setHorizontalHeaderLabels(["Fecha", "Tasa"])
        layout.addWidget(QLabel("Historial de tasas:"))
        layout.addWidget(self.tabla)

        self.cargar_historial()

    def guardar_tasa(self):
        try:
            tasa = float(self.input_tasa.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Ingrese un número válido")
            return
        fecha = datetime.date.today().isoformat()
        conversion_service.guardar_tasa(fecha, tasa)
        QMessageBox.information(self, "Éxito", f"Tasa guardada para {fecha}")
        self.cargar_historial()

    def convertir(self):
        try:
            monto = float(self.input_usd.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Ingrese un monto válido en USD")
            return
        fecha = datetime.date.today().isoformat()
        resultado = conversion_service.usd_a_ves(monto, fecha)
        if resultado is None:
            QMessageBox.warning(self, "Error", "No hay tasa registrada para hoy")
        else:
            self.label_resultado.setText(f"Resultado: {resultado} VES")

    def cargar_historial(self):
        tasas = conversion_service.listar_tasas()
        self.tabla.setRowCount(0)
        for i, (fecha, tasa) in enumerate(tasas):
            self.tabla.insertRow(i)
            self.tabla.setItem(i, 0, QTableWidgetItem(fecha))
            self.tabla.setItem(i, 1, QTableWidgetItem(str(tasa)))