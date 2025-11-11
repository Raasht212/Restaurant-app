from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QSpinBox, QMessageBox, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from .controller import (
    obtener_productos_disponibles,
    consultar_stock,
    obtener_orden_abierta_por_mesa,
    obtener_detalles_orden,
    crear_o_actualizar_orden,
    aplicar_cambios_stock,
    insertar_factura
)
import datetime
import random

class OrdenDialog(QDialog):
    estado_mesa_cambiado = Signal()

    def __init__(self, mesa, parent=None):
        super().__init__(parent)
        # mesa expected: tuple (id, numero, estado, seccion) — adaptar si tu esquema difiere
        self.mesa = mesa
        self.productos_seleccionados = []   # [{'id', 'nombre', 'precio', 'cantidad', 'subtotal'}, ...]
        self.orden_id = None
        self.detalles_originales = {}       # {producto_id: {'cantidad_original': X, 'cantidad_actual': Y}}
        self._productos_map = {}            # product_id -> {nombre, precio, stock}
        self.setWindowTitle(f"Orden - Mesa {mesa[1]}")
        self.setMinimumSize(900, 600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Cabecera: Mesa y Estado
        mesa_layout = QHBoxLayout()
        self.label_mesa = QLabel(f"Mesa: {self.mesa[1]}")
        mesa_layout.addWidget(self.label_mesa)

        estado_text = "Ocupada" if (len(self.mesa) > 2 and self.mesa[2] == "ocupada") else "Libre"
        self.label_estado = QLabel(f"Estado: {estado_text}")
        mesa_layout.addWidget(self.label_estado)
        mesa_layout.addStretch()
        layout.addLayout(mesa_layout)

        # Cliente
        cliente_layout = QHBoxLayout()
        cliente_layout.addWidget(QLabel("Nombre del Cliente:"))
        self.input_cliente = QLineEdit()
        self.input_cliente.setPlaceholderText("Ingrese nombre del cliente")
        self.input_cliente.setMinimumHeight(32)
        cliente_layout.addWidget(self.input_cliente)
        layout.addLayout(cliente_layout)

        # Productos / selector
        productos_layout = QHBoxLayout()

        left = QVBoxLayout()
        left.addWidget(QLabel("Productos Disponibles:"))
        self.combo_productos = QComboBox()
        self.combo_productos.setMinimumHeight(32)
        left.addWidget(self.combo_productos)

        cantidad_layout = QHBoxLayout()
        self.spin_cantidad = QSpinBox()
        self.spin_cantidad.setMinimum(1)
        self.spin_cantidad.setMaximum(1000)
        self.spin_cantidad.setValue(1)
        cantidad_layout.addWidget(QLabel("Cantidad:"))
        cantidad_layout.addWidget(self.spin_cantidad)
        left.addLayout(cantidad_layout)

        btn_agregar = QPushButton("Agregar")
        btn_agregar.clicked.connect(self.agregar_producto)
        left.addWidget(btn_agregar)
        productos_layout.addLayout(left, 3)

        # Tabla de la orden
        right = QVBoxLayout()
        right.addWidget(QLabel("Productos en la orden:"))
        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(5)
        self.tabla_productos.setHorizontalHeaderLabels(["Producto", "Precio", "Cantidad", "Subtotal", ""])
        self.tabla_productos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_productos.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla_productos.setEditTriggers(QAbstractItemView.NoEditTriggers)
        right.addWidget(self.tabla_productos)
        productos_layout.addLayout(right, 5)

        layout.addLayout(productos_layout)

        # Total y botones
        total_layout = QHBoxLayout()
        total_layout.addWidget(QLabel("Total:"))
        self.label_total = QLabel("$0.00")
        self.label_total.setFont(QFont("Arial", 14, QFont.Bold))
        self.label_total.setStyleSheet("color: #e74c3c;")
        total_layout.addWidget(self.label_total)
        total_layout.addStretch()

        self.btn_confirmar = QPushButton("Confirmar Orden")
        self.btn_confirmar.setStyleSheet("background-color: #27ae60; color: #fff; font-weight: bold;")
        self.btn_confirmar.clicked.connect(self.confirmar_orden)

        self.btn_factura = QPushButton("Generar Factura")
        self.btn_factura.setStyleSheet("background-color: #9b59b6; color: #fff; font-weight: bold;")
        self.btn_factura.clicked.connect(self.generar_factura)
        self.btn_factura.setVisible(False)

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet("background-color: #e74c3c; color: #fff;")
        btn_cancel.clicked.connect(self.reject)

        total_layout.addWidget(btn_cancel)
        total_layout.addWidget(self.btn_confirmar)
        total_layout.addWidget(self.btn_factura)
        layout.addLayout(total_layout)

        # Inicializar datos
        self.cargar_productos()
        orden_abierta = obtener_orden_abierta_por_mesa(self.mesa[0])
        if orden_abierta:
            # orden_abierta: (id, cliente_nombre, total)
            self.orden_id = orden_abierta[0]
            self.input_cliente.setText(orden_abierta[1] or "")
            self.cargar_detalles_orden()
            self.input_cliente.setEnabled(False)
            self.btn_factura.setVisible(True)
        else:
            self.productos_seleccionados = []
            self.detalles_originales = {}
            self.actualizar_tabla_productos()

    # -----------------------
    # Carga y selección de productos
    # -----------------------
    def cargar_productos(self):
        self.combo_productos.clear()
        filas = obtener_productos_disponibles()
        self._productos_map = {}
        for pid, nombre, precio, stock in filas:
            display = f"{nombre} - ${float(precio):.2f}"
            self.combo_productos.addItem(display, pid)
            self._productos_map[pid] = {"nombre": nombre, "precio": float(precio), "stock": int(stock)}

    def agregar_producto(self):
        producto_id = self.combo_productos.currentData()
        if producto_id is None:
            QMessageBox.warning(self, "Error", "Seleccione un producto")
            return

        prod_info = self._productos_map.get(producto_id)
        if not prod_info:
            QMessageBox.warning(self, "Error", "Producto no encontrado")
            return

        cantidad = int(self.spin_cantidad.value())
        nombre = prod_info["nombre"]
        precio = float(prod_info["precio"])

        stock_disponible = consultar_stock(producto_id)
        if stock_disponible is None:
            return

        existente = next((p for p in self.productos_seleccionados if p["id"] == producto_id), None)
        cantidad_en_orden = existente["cantidad"] if existente else 0
        if producto_id in self.detalles_originales:
            cantidad_en_orden += int(self.detalles_originales[producto_id].get("cantidad_actual", 0))

        cantidad_total_solicitada = cantidad + cantidad_en_orden
        if cantidad_total_solicitada > stock_disponible:
            QMessageBox.warning(
                self,
                "Stock insuficiente",
                f"No hay suficiente stock de {nombre}\nStock disponible: {stock_disponible}"
            )
            return

        if existente:
            existente["cantidad"] += cantidad
            existente["subtotal"] = round(existente["cantidad"] * precio, 2)
        else:
            self.productos_seleccionados.append({
                "id": producto_id,
                "nombre": nombre,
                "precio": precio,
                "cantidad": cantidad,
                "subtotal": round(precio * cantidad, 2)
            })

        self.actualizar_tabla_productos()

    def actualizar_tabla_productos(self):
        self.tabla_productos.clearContents()
        self.tabla_productos.setRowCount(len(self.productos_seleccionados))
        total = 0.0

        for fila, producto in enumerate(self.productos_seleccionados):
            nombre_item = QTableWidgetItem(producto["nombre"])
            precio_item = QTableWidgetItem(f"${producto['precio']:.2f}")
            cantidad_item = QTableWidgetItem(str(producto["cantidad"]))
            subtotal_item = QTableWidgetItem(f"${producto['subtotal']:.2f}")

            self.tabla_productos.setItem(fila, 0, nombre_item)
            self.tabla_productos.setItem(fila, 1, precio_item)
            self.tabla_productos.setItem(fila, 2, cantidad_item)
            self.tabla_productos.setItem(fila, 3, subtotal_item)

            btn_eliminar = QPushButton("Eliminar")
            btn_eliminar.setStyleSheet("background-color: #e74c3c; color: white;")
            pid = producto["id"]
            btn_eliminar.clicked.connect(lambda _, prod_id=pid: self.eliminar_producto_por_id(prod_id))
            self.tabla_productos.setCellWidget(fila, 4, btn_eliminar)

            total += float(producto["subtotal"])

        self.label_total.setText(f"${total:.2f}")

    def eliminar_producto_por_id(self, producto_id):
        antes = len(self.productos_seleccionados)
        self.productos_seleccionados = [p for p in self.productos_seleccionados if p["id"] != producto_id]
        if len(self.productos_seleccionados) != antes:
            self.actualizar_tabla_productos()

    # -----------------------
    # Cargar / guardar orden en BD (usa controller)
    # -----------------------
    def cargar_detalles_orden(self):
        if not self.orden_id:
            return
        detalles = obtener_detalles_orden(self.orden_id)
        self.detalles_originales = {}
        self.productos_seleccionados = []
        for pid, nombre, precio, cantidad, subtotal in detalles:
            self.detalles_originales[pid] = {
                "cantidad_original": int(cantidad),
                "cantidad_actual": int(cantidad)
            }
            self.productos_seleccionados.append({
                "id": pid,
                "nombre": nombre,
                "precio": float(precio),
                "cantidad": int(cantidad),
                "subtotal": float(subtotal)
            })
        self.actualizar_tabla_productos()

    def confirmar_orden(self):
        cliente = self.input_cliente.text().strip()
        if not cliente:
            QMessageBox.warning(self, "Error", "Debe ingresar el nombre del cliente")
            return
        if not self.productos_seleccionados:
            QMessageBox.warning(self, "Error", "Debe agregar al menos un producto a la orden")
            return

        # Preparar lista de productos para el controller
        productos_payload = [
            {"id": p["id"], "cantidad": int(p["cantidad"]), "subtotal": float(p["subtotal"])}
            for p in self.productos_seleccionados
        ]

        # Calcular cambios de stock necesarios (diferencias)
        cambios_stock = {}
        for p in productos_payload:
            pid = p["id"]
            cantidad_actual = p["cantidad"]
            if pid in self.detalles_originales:
                cantidad_original = int(self.detalles_originales[pid]["cantidad_original"])
                diferencia = cantidad_actual - cantidad_original
            else:
                diferencia = cantidad_actual
            cambios_stock[pid] = cambios_stock.get(pid, 0) + diferencia

        # Productos eliminados
        for pid, detalle in self.detalles_originales.items():
            if pid not in [p["id"] for p in productos_payload]:
                cambios_stock[pid] = cambios_stock.get(pid, 0) - int(detalle["cantidad_original"])

        # Verificar stock antes de persistir
        ok, msg = aplicar_cambios_stock({k: v for k, v in cambios_stock.items() if v > 0})
        if not ok:
            QMessageBox.warning(self, "Stock insuficiente", msg or "Stock insuficiente")
            return

        # Crear o actualizar orden (persistir detalles)
        success, orden_id, err = crear_o_actualizar_orden(self.mesa[0], cliente, productos_payload, orden_id=self.orden_id)
        if not success:
            QMessageBox.critical(self, "Error", err or "No se pudo guardar la orden")
            return

        self.orden_id = orden_id
        # Aplicar cambios de stock (incluye decrementos positivos ya verificados; negativos también aplicados)
        ok2, msg2 = aplicar_cambios_stock(cambios_stock)
        if not ok2:
            QMessageBox.critical(self, "Error", msg2 or "Error aplicando cambios de stock")
            return

        QMessageBox.information(self, "Éxito", "Orden registrada correctamente")
        # Actualizar estructura original
        self.detalles_originales = {p["id"]: {"cantidad_original": int(p["cantidad"]), "cantidad_actual": int(p["cantidad"])} for p in self.productos_seleccionados}
        self.input_cliente.setEnabled(False)
        self.btn_factura.setVisible(True)
        try:
            self.estado_mesa_cambiado.emit()
        except Exception:
            pass

    # -----------------------
    # Facturación
    # -----------------------
    def generar_factura(self):
        if not self.orden_id:
            QMessageBox.warning(self, "Error", "No hay una orden confirmada para facturar")
            return
        if not self.productos_seleccionados:
            QMessageBox.warning(self, "Error", "La orden no tiene productos")
            return

        total = sum(float(p["subtotal"]) for p in self.productos_seleccionados)
        numero_factura = f"FACT-{datetime.datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        ok, err = insertar_factura(self.orden_id, numero_factura, self.input_cliente.text().strip(), float(total))
        if not ok:
            QMessageBox.critical(self, "Error", err or "No se pudo generar la factura")
            return

        self.mostrar_resumen_factura(numero_factura, total)
        try:
            self.estado_mesa_cambiado.emit()
        except Exception:
            pass

        # Limpiar estado local para nueva orden
        self.productos_seleccionados = []
        self.orden_id = None
        self.detalles_originales = {}
        self.actualizar_tabla_productos()
        self.input_cliente.clear()
        self.input_cliente.setEnabled(True)
        self.btn_factura.setVisible(False)

    def mostrar_resumen_factura(self, numero_factura, total):
        def esc(text):
            return (str(text)
                    .replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                    .replace('"', "&quot;")
                    .replace("'", "&#39;"))

        mensaje = f"<b>FACTURA GENERADA</b><br><br>"
        mensaje += f"<b>Número:</b> {esc(numero_factura)}<br>"
        mensaje += f"<b>Fecha:</b> {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}<br>"
        mensaje += f"<b>Mesa:</b> {esc(self.mesa[1])}<br>"
        mensaje += f"<b>Cliente:</b> {esc(self.input_cliente.text().strip())}<br><br>"

        mensaje += "<b>Detalle de productos:</b><br>"
        mensaje += "<table border='1' style='border-collapse: collapse; width: 100%;'>"
        mensaje += "<tr><th>Producto</th><th>Precio</th><th>Cantidad</th><th>Subtotal</th></tr>"

        for producto in self.productos_seleccionados:
            nombre = esc(producto.get("nombre", ""))
            precio = float(producto.get("precio", 0.0))
            cantidad = int(producto.get("cantidad", 0))
            subtotal = float(producto.get("subtotal", 0.0))
            mensaje += (
                f"<tr>"
                f"<td>{nombre}</td>"
                f"<td style='text-align:right'>${precio:.2f}</td>"
                f"<td style='text-align:center'>{cantidad}</td>"
                f"<td style='text-align:right'>${subtotal:.2f}</td>"
                f"</tr>"
            )

        mensaje += (
            f"<tr>"
            f"<td colspan='3' align='right'><b>Total:</b></td>"
            f"<td style='text-align:right'><b>${float(total):.2f}</b></td>"
            f"</tr>"
        )
        mensaje += "</table>"

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Factura Generada")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(mensaje)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()