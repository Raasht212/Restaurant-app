import datetime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit
)
from PySide6.QtCore import Qt
from ...services.factura_service import obtener_detalles_factura


class InvoiceDetailDialog(QDialog):
    def __init__(self, factura_id: int, parent=None):
        super().__init__(parent)
        self.factura_id = factura_id
        self.setWindowTitle("Detalles de Factura")
        self.setMinimumSize(520, 640)

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Cabecera negocio
        header = QLabel("<b>Piacere</b><br/>Calle 11 # 7c - 27<br/>Tel: 3006957308")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # Obtener detalles (incluye cliente)
        detalles = obtener_detalles_factura(self.factura_id)

        # Si no hay detalles, mostramos vacío
        if not detalles:
            layout.addWidget(QLabel("No se encontraron detalles para esta factura."))
            return

        # El cliente viene en cada fila, tomamos el primero
        cliente_nombre = detalles[0][5]

        fecha_actual = datetime.datetime.now().strftime('%d/%m/%Y %I:%M:%S %p')
        meta = QLabel(
            f"<b>Factura ID:</b> {self.factura_id}<br>"
            f"<b>Fecha:</b> {fecha_actual}<br>"
            f"<b>Cliente:</b> {cliente_nombre}<br>"
        )
        meta.setTextFormat(Qt.RichText)
        layout.addWidget(meta)

        # Construir HTML estilo ticket
        lines_html = []
        lines_html.append("<table width='100%' style='border-collapse:collapse;font-family:monospace;'>")
        lines_html.append("<tr><th style='text-align:left'>Producto</th><th style='text-align:center'>Cant</th><th style='text-align:right'>P.Unit</th><th style='text-align:right'>Total</th></tr>")

        total = 0.0
        for producto, variante, cantidad, precio_unitario, subtotal, _ in detalles:
            cantidad = int(cantidad)
            subtotal = float(subtotal)
            precio_unitario = float(precio_unitario)
            total += subtotal

            lines_html.append(
                f"<tr>"
                f"<td style='padding:4px 0'>{producto}</td>"
                f"<td style='text-align:center'>{cantidad}</td>"
                f"<td style='text-align:right'>${precio_unitario:.2f}</td>"
                f"<td style='text-align:right'>${subtotal:.2f}</td>"
                f"</tr>"
            )
            if variante:
                lines_html.append(
                    f"<tr><td style='font-size:11px;color:#666;padding-bottom:6px' colspan='4'>Variante: {variante}</td></tr>"
                )

        lines_html.append(
            f"<tr><td colspan='4'><hr/></td></tr>"
            f"<tr><td colspan='3' style='text-align:right'><b>Total:</b></td>"
            f"<td style='text-align:right'><b>${total:.2f}</b></td></tr>"
        )
        lines_html.append("</table>")

        text = QTextEdit()
        text.setReadOnly(True)
        text.setHtml("".join(lines_html))
        layout.addWidget(text, stretch=1)

        # Botón cerrar
        footer = QHBoxLayout()
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.close)
        footer.addStretch()
        footer.addWidget(btn_cerrar)
        layout.addLayout(footer)