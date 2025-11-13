from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton
from ...services.factura_service import obtener_detalles_factura

class InvoiceDetailDialog(QDialog):
    def __init__(self, factura_id, parent=None):
        super().__init__(parent)
        self.factura_id = factura_id
        self.setWindowTitle("Detalles de Factura")
        self.resize(500, 400)

        layout = QVBoxLayout(self)

        # Encabezado
        layout.addWidget(QLabel(f"Factura #{factura_id}"))

        # Tabla de detalles
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Producto", "Cantidad", "Precio", "Subtotal"])
        layout.addWidget(self.table)

        # Botón cerrar
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.close)
        layout.addWidget(btn_cerrar)

        self.cargar_detalles()

    def cargar_detalles(self):
        detalles = obtener_detalles_factura(self.factura_id)
        self.table.setRowCount(len(detalles))
        for row, (producto, cantidad, precio, subtotal) in enumerate(detalles):
            self.table.setItem(row, 0, QTableWidgetItem(producto))
            self.table.setItem(row, 1, QTableWidgetItem(str(cantidad)))
            self.table.setItem(row, 2, QTableWidgetItem(f"{precio:.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{subtotal:.2f}"))