from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from .ui_dashboard import Ui_Dashboard

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import numpy as np


class DashboardView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dashboard()
        self.ui.setupUi(self)

        # Ajustes visuales de la tabla
        self._setup_table()

        # Insertar gráficas
        self._insertar_grafica_ventas_mensuales(self.ui.frame_11)
        self._insertar_grafica_top_productos(self.ui.frame_6)

        # Datos de ejemplo iniciales (puedes reemplazar por tus services)
        self.set_metrics(
            tasa_dia="240 VEZ",
            mesas_disponibles=20,
            ordenes_dia=23,
            variacion_ordenes="+15% Respecto a ayer",
            ventas_dia="$8,541",
            variacion_ventas="+30% Respecto a ayer"
        )
        self.load_monthly_sales(
            meses=["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov"],
            ventas=[1200, 1500, 1800, 1600, 2000, 2200, 2100, 2500, 2700, 3000, 3200]
        )
        self.load_top_products(
            productos=["Pepperoni", "Margarita", "Jugo Natural", "Tiramisú", "Coca-Cola"],
            ventas=[120, 100, 90, 80, 75]
        )
        self.load_open_orders([
            {"cliente": "Carlos", "mesa": "Mesa 3", "monto": 45.00, "orden_id": 101},
            {"cliente": "Ana", "mesa": "Mesa 5", "monto": 32.00, "orden_id": 102},
            {"cliente": "Luis", "mesa": "Mesa 1", "monto": 58.00, "orden_id": 103},
        ])

    # --- Tabla de órdenes abiertas ---

    def _setup_table(self):
        self.ui.tableWidget.setRowCount(0)
        self.ui.tableWidget.setColumnCount(4)
        self.ui.tableWidget.setHorizontalHeaderLabels(["Cliente", "Mesa", "Monto", "Ver Orden"])
        header = self.ui.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        # Corrección: usar QAbstractItemView.NoEditTriggers
        self.ui.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Fondo celda claro para contraste con tema oscuro del frame
        self.ui.tableWidget.setStyleSheet("QTableWidget { color: white; }")

    def load_open_orders(self, ordenes):
        """
        ordenes: lista de dicts con {cliente, mesa, monto, orden_id}
        """
        self.ui.tableWidget.setRowCount(0)
        for row_idx, item in enumerate(ordenes):
            self.ui.tableWidget.insertRow(row_idx)

            cliente = QTableWidgetItem(item["cliente"])
            mesa = QTableWidgetItem(item["mesa"])
            monto = QTableWidgetItem(f"${item['monto']:.2f}")

            for it in (cliente, mesa, monto):
                it.setFlags(it.flags() & ~Qt.ItemIsEditable)

            self.ui.tableWidget.setItem(row_idx, 0, cliente)
            self.ui.tableWidget.setItem(row_idx, 1, mesa)
            self.ui.tableWidget.setItem(row_idx, 2, monto)

            btn = QPushButton("Ver")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("QPushButton { background-color: #2ecc71; color: white; font-weight: bold; padding: 1; }")
            orden_id = item["orden_id"]
            btn.clicked.connect(lambda _, oid=orden_id: self.on_ver_orden_clicked(oid))
            self.ui.tableWidget.setCellWidget(row_idx, 3, btn)

    def on_ver_orden_clicked(self, orden_id: int):
        print(f"[Dashboard] Ver detalles de la orden #{orden_id}")
        # TODO: abrir tu diálogo de orden
        # dialog = OrdenDialog(orden_id, self)
        # dialog.exec()

    # --- Tarjetas de métricas ---

    def set_metrics(self,
                    tasa_dia: str,
                    mesas_disponibles: int,
                    ordenes_dia: int,
                    variacion_ordenes: str,
                    ventas_dia: str,
                    variacion_ventas: str):
        self.ui.label_11.setText(str(tasa_dia))
        self.ui.label_20.setText(str(mesas_disponibles))
        self.ui.label_13.setText(str(ordenes_dia))
        self.ui.label_14.setText(variacion_ordenes)
        self.ui.label_17.setText(str(ventas_dia))
        self.ui.label_18.setText(variacion_ventas)

        self._color_variacion(self.ui.label_14, variacion_ordenes)
        self._color_variacion(self.ui.label_18, variacion_ventas)

    def _color_variacion(self, label, text):
        color = "#27ae60" if "+" in text else ("#e74c3c" if "-" in text else "white")
        label.setStyleSheet(f"color: {color};")

    # --- Gráfica: Ventas mensuales (línea) ---

    def _insertar_grafica_ventas_mensuales(self, frame):
        from PySide6.QtWidgets import QSizePolicy

        self._fig_mensual = Figure(figsize=(5, 3), facecolor='none')  # fondo transparente
        self._ax_mensual = self._fig_mensual.add_subplot(111)
        self._ax_mensual.set_facecolor('none')  # fondo del eje transparente
        self._ax_mensual.tick_params(colors="white")
        self._ax_mensual.set_title("Ventas Mensuales", color="white", fontsize=12)
        self._ax_mensual.grid(True, linestyle="--", alpha=0.3)

        self._canvas_mensual = FigureCanvas(self._fig_mensual)
        self._canvas_mensual.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._canvas_mensual.setMinimumSize(300, 200)
        self._canvas_mensual.setMaximumHeight(300)
        self._canvas_mensual.setStyleSheet("background: transparent;")
        self._canvas_mensual.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        layout.addWidget(self._canvas_mensual)

    def load_monthly_sales(self, meses, ventas):
        self._ax_mensual.clear()
        self._ax_mensual.set_facecolor("none")
        self._ax_mensual.tick_params(colors="white")
        self._ax_mensual.set_title("Ventas Mensuales", color="white", fontsize=12)
        self._ax_mensual.grid(True, linestyle="--", alpha=0.3)

        x = np.arange(len(meses))
        self._ax_mensual.plot(x, ventas, color="#00bfff", linewidth=2.5, marker='o')
        self._ax_mensual.set_xticks(x)
        self._ax_mensual.set_xticklabels(meses, color="white")
        for label in self._ax_mensual.get_yticklabels():
            label.set_color("white")

        self._fig_mensual.tight_layout()
        self._canvas_mensual.draw_idle()

    # --- Gráfica: Top productos (barra horizontal) ---

    def _insertar_grafica_top_productos(self, frame):
        from PySide6.QtWidgets import QSizePolicy

        self._fig_top = Figure(figsize=(5, 3), facecolor='none')  # fondo transparente
        self._ax_top = self._fig_top.add_subplot(111)
        self._ax_top.set_facecolor('none')  # fondo del eje transparente
        self._ax_top.tick_params(colors="white")
        self._ax_top.set_title("Productos Más Vendidos", color="white", fontsize=12)

        self._canvas_top = FigureCanvas(self._fig_top)
        self._canvas_top.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._canvas_top.setMinimumSize(300, 200)
        self._canvas_top.setMaximumHeight(300)
        self._canvas_top.setStyleSheet("background: transparent;")
        self._canvas_top.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        layout.addWidget(self._canvas_top)

    def load_top_products(self, productos, ventas):
        self._ax_top.clear()
        self._ax_top.set_facecolor("none")
        self._ax_top.tick_params(colors="white")
        self._ax_top.set_title("Productos Más Vendidos", color="white", fontsize=12)

        y = np.arange(len(productos))
        self._ax_top.barh(y, ventas, color="#00bfff")
        self._ax_top.set_yticks(y)
        self._ax_top.set_yticklabels(productos, color="white")
        for label in self._ax_top.get_xticklabels():
            label.set_color("white")

        self._fig_top.tight_layout()
        self._canvas_top.draw_idle()