# src/app/views/orden/invoice_preview.py
from typing import List, Dict, Optional
import datetime

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QMessageBox
)
from PySide6.QtCore import Qt

from ...controllers import orden_controller as orden_controller_module

class InvoicePreviewDialog(QDialog):
    """
    Diálogo para mostrar la vista previa de la factura en formato 'ticket' y permitir confirmar
    antes de llamar al controller que inserta la factura en la BD.
    Constructor arguments:
      - orden_id: int
      - cliente: str
      - productos: List[Dict] each dict: {'nombre','precio','cantidad','subtotal'}
      - total: float
      - forma_pago: Optional[str] default 'Efectivo'
      - numero_factura: Optional[str] si None el diálogo generará un número temporal
    """
    def __init__(
        self,
        orden_id: int,
        cliente: str,
        productos: List[Dict],
        total: float,
        forma_pago: Optional[str] = "Efectivo",
        numero_factura: Optional[str] = None,
        parent=None
    ):
        super().__init__(parent)
        self.setWindowTitle("Vista previa de factura")
        self.setMinimumSize(520, 640)
        self.orden_id = orden_id
        self.cliente = cliente or "Consumidor final"
        self.productos = productos
        self.total = float(total)
        self.forma_pago = forma_pago or "Efectivo"
        self.numero_factura = numero_factura or self._generar_numero_temporal()
        self._build_ui()

    def _generar_numero_temporal(self) -> str:
        return f"TEMP-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Cabecera compacta (nombre negocio estático, puedes parametrizar)
        header = QLabel("<b>Piacere</b><br/>Calle 11 # 7c - 27<br/>Tel: 3006957308")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # Datos factura / cliente
        meta = QLabel(
            f"<b>Factura #</b> {self.numero_factura} &nbsp;&nbsp;&nbsp; <b>Fecha:</b> {datetime.datetime.now().strftime('%d/%m/%Y %I:%M:%S %p')}<br>"
            f"<b>Cliente:</b> {self.cliente}<br>"
        )
        meta.setTextFormat(Qt.RichText)
        layout.addWidget(meta)

        # Texto con tabla estilo ticket (usamos QTextEdit en read-only para facilitar HTML)
        lines_html = []
        lines_html.append("<table width='100%' style='border-collapse:collapse;font-family:monospace;'>")
        lines_html.append("<tr><th style='text-align:left'>Producto</th><th style='text-align:center'>Cant</th><th style='text-align:right'>Total</th></tr>")
        for p in self.productos:
            nombre = str(p.get("nombre",""))
            cantidad = int(p.get("cantidad",0))
            subtotal = float(p.get("subtotal",0.0))
            # mostrar nombre en una línea y descripción en una sublínea si existe
            lines_html.append(
                f"<tr>"
                f"<td style='padding:4px 0'>{nombre}</td>"
                f"<td style='text-align:center'>{cantidad}UND</td>"
                f"<td style='text-align:right'>${subtotal:.2f}</td>"
                f"</tr>"
            )
            descripcion = p.get("descripcion") or p.get("desc") or ""
            if descripcion:
                lines_html.append(
                    f"<tr><td style='font-size:11px;color:#666;padding-bottom:6px' colspan='3'>{descripcion}</td></tr>"
                )

        lines_html.append(
            f"<tr><td colspan='3'><hr/></td></tr>"
            f"<tr><td colspan='2' style='text-align:right'><b>Total:</b></td><td style='text-align:right'><b>${self.total:.2f}</b></td></tr>"
            f"<tr><td colspan='2' style='text-align:right'>Forma de Pago:</td><td style='text-align:right'>{self.forma_pago}</td></tr>"
        )
        lines_html.append("</table>")

        text = QTextEdit()
        text.setReadOnly(True)
        text.setHtml("".join(lines_html))
        layout.addWidget(text, stretch=1)

        # Botones
        footer = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar")
        btn_confirm = QPushButton("Confirmar factura")
        btn_confirm.setStyleSheet("background-color:#27ae60;color:white;font-weight:bold")
        btn_cancel.clicked.connect(self.reject)
        btn_confirm.clicked.connect(self._on_confirm_clicked)
        footer.addStretch()
        footer.addWidget(btn_cancel)
        footer.addWidget(btn_confirm)
        layout.addLayout(footer)

    def _on_confirm_clicked(self):
        """
        Llama al controller para insertar la factura. Muestra mensajes de éxito/fallo.
        """
        numero = self.numero_factura
        cliente = self.cliente
        total = float(self.total)

        ok, err = orden_controller_module.generar_factura_flow(self.orden_id, cliente, total, numero)
        if not ok:
            QMessageBox.critical(self, "Error generando factura", err or "No se pudo crear la factura")
            return

        QMessageBox.information(self, "Factura creada", f"Factura {numero} creada correctamente")
        # Confirmar y cerrar
        self.accept()