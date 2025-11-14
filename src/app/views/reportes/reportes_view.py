# src/app/views/reportes/reportes_view.py
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont
from ...models.invoice import Invoice
from .invoice_detail_dialog import InvoiceDetailDialog


class ReportesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        hoy = QDate.currentDate()
        self.cargar_datos()

    def setup_ui(self):
        layout = QVBoxLayout()

        titulo = QLabel("REPORTES - Facturas")
        titulo.setFont(QFont("Segoe UI", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setObjectName("titulo")
        layout.addWidget(titulo)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["id", "numero", "fecha", "cliente", "total", "orden_id"]
        )
        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(QHeaderView.Stretch)

        # 🔒 Deshabilitar edición en toda la tabla
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.table)

        # Conectar doble clic
        self.table.itemDoubleClicked.connect(self.ver_detalles_factura)

        self.setLayout(layout)

    def cargar_datos(self):
        try:
            facturas = Invoice.obtener_por_rango_fechas("2024-01-01", "2025-12-31")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error consultando facturas: {e}")
            return

        self.table.setRowCount(0)
        for inv in facturas:
            ridx = self.table.rowCount()
            self.table.insertRow(ridx)

            # Cada celda como solo lectura
            id_item = QTableWidgetItem(str(inv.id))
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(ridx, 0, id_item)

            num_item = QTableWidgetItem(inv.numero_factura)
            num_item.setFlags(num_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(ridx, 1, num_item)

            fecha_item = QTableWidgetItem(inv.fecha)
            fecha_item.setFlags(fecha_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(ridx, 2, fecha_item)

            cliente_item = QTableWidgetItem(inv.cliente_nombre)
            cliente_item.setFlags(cliente_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(ridx, 3, cliente_item)

            total_item = QTableWidgetItem(f"{inv.total:.2f}")
            total_item.setFlags(total_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(ridx, 4, total_item)

            orden_item = QTableWidgetItem(str(inv.orden_id))
            orden_item.setFlags(orden_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(ridx, 5, orden_item)

    def ver_detalles_factura(self, item):
        row = item.row()
        factura_id = int(self.table.item(row, 0).text())
        dialog = InvoiceDetailDialog(factura_id, self)
        dialog.exec()