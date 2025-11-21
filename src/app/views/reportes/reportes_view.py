from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QLineEdit, QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ...services.factura_service import (
    obtener_facturas_rango,
    obtener_facturas_por_cliente,
    eliminar_factura
)
from .invoice_detail_dialog import InvoiceDetailDialog


class ReportesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.cargar_datos()

    def setup_ui(self):
        layout = QVBoxLayout()

        titulo = QLabel("REPORTES - Facturas")
        titulo.setFont(QFont("Segoe UI", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        # 🔎 Barra de búsqueda por cliente
        search_layout = QHBoxLayout()
        self.input_cliente = QLineEdit()
        self.input_cliente.setPlaceholderText("Buscar por cliente...")
        btn_buscar = QPushButton("Buscar")
        btn_buscar.clicked.connect(self.buscar_por_cliente)
        btn_refrescar = QPushButton("Refrescar")
        btn_refrescar.clicked.connect(self.cargar_datos)
        btn_eliminar = QPushButton("Eliminar factura seleccionada")
        btn_eliminar.clicked.connect(self.eliminar_factura_seleccionada)

        search_layout.addWidget(self.input_cliente)
        search_layout.addWidget(btn_buscar)
        search_layout.addWidget(btn_refrescar)
        search_layout.addWidget(btn_eliminar)
        layout.addLayout(search_layout)

        # Tabla de facturas
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["id", "numero", "fecha", "cliente", "total", "orden_id"]
        )
        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.itemDoubleClicked.connect(self.ver_detalles_factura)

        layout.addWidget(self.table)
        self.setLayout(layout)

    def cargar_datos(self):
        try:
            facturas = obtener_facturas_rango("2024-01-01", "2025-12-31")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error consultando facturas: {e}")
            return

        self._llenar_tabla(facturas)

    def buscar_por_cliente(self):
        cliente = self.input_cliente.text().strip()
        if not cliente:
            QMessageBox.warning(self, "Aviso", "Ingrese un nombre de cliente para buscar")
            return
        try:
            facturas = obtener_facturas_por_cliente(cliente)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error buscando facturas: {e}")
            return
        self._llenar_tabla(facturas)

    def eliminar_factura_seleccionada(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Seleccione una factura para eliminar")
            return
        factura_id = int(self.table.item(row, 0).text())
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Eliminar la factura #{factura_id}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        ok, err = eliminar_factura(factura_id)
        if not ok:
            QMessageBox.critical(self, "Error", err or "No se pudo eliminar factura")
        else:
            QMessageBox.information(self, "Éxito", "Factura eliminada correctamente")
            self.cargar_datos()

    def ver_detalles_factura(self, item):
        row = item.row()
        factura_id = int(self.table.item(row, 0).text())
        dialog = InvoiceDetailDialog(factura_id, self)
        dialog.exec()

    def _llenar_tabla(self, facturas):
        self.table.setRowCount(0)
        for inv in facturas:
            ridx = self.table.rowCount()
            self.table.insertRow(ridx)
            for col, val in enumerate(inv):
                item = QTableWidgetItem(str(val))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(ridx, col, item)