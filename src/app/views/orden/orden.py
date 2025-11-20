# Reemplaza la clase OrdenDialog existente por esta (src/app/views/orden/orden_view.py)
from typing import List, Dict, Optional, Tuple
import datetime
import random
import logging

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QSpinBox,
    QMessageBox, QAbstractItemView, QGroupBox, QListWidget, QListWidgetItem,
    QSplitter, QWidget, QSizePolicy, QInputDialog
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QColor, QBrush

from ...services import orden_service as orden_service_module
from ...services import menu_service
from ...services import conversion_service
from ...services import stock_service
from ...controllers import orden_controller as orden_controller_module
from .invoice_preview import InvoicePreviewDialog

logger = logging.getLogger(__name__)


class OrdenDialog(QDialog):
    estado_mesa_cambiado = Signal()

    def __init__(self, mesa: Tuple[int, int, str, Optional[str]], parent=None):
        super().__init__(parent)
        self.mesa = mesa
        self.input_cliente: QLineEdit = None
        self.productos_seleccionados: List[Dict] = []
        self.orden_id: Optional[int] = None
        self.detalles_originales: Dict[int, Dict] = {}
        self._productos_map: Dict[Tuple[str, int], Dict] = {}
        self._productos_list_cache: List[Dict] = []  # lista de productos actualmente visibles (para búsqueda)
        self.setWindowTitle(f"Orden - Mesa {mesa[1]}")
        self.setMinimumSize(1200, 640)
        self.setup_ui()
        self.load_initial_state()

    # --------------------------
    # UI setup
    # --------------------------
    def setup_ui(self):
        self.setStyleSheet("""
            QWidget { background: #121217; color: #e8e8e8; font-family: "Segoe UI", Arial; }
            QGroupBox { border: 0; margin: 0; padding: 0; }
            QListWidget { background: #15151a; border: 1px solid #26262b; }
            QListWidget::item { padding: 10px; }
            QListWidget::item:selected { background: #2b2b31; color: #fff; }
            QTableWidget { background: #0f0f12; gridline-color: #232326; }
            QHeaderView::section { background: #3b1f25; color: white; padding: 6px; }
            QPushButton { padding: 8px 12px; border-radius: 6px; }
            QPushButton#addBtn { background: #2980b9; color: white; font-weight: bold; }
            QPushButton#confirmBtn { background: #27ae60; color: white; font-weight: bold; }
            QPushButton#factBtn { background: #9b59b6; color: white; }
            QPushButton#cancelBtn { background: #e74c3c; color: white; }
            QLabel.title { font-size: 16px; font-weight: bold; color: #fff; }
            .desc { color: #bdbdbd; font-size: 11.5px; }
        """)

        main_layout = QVBoxLayout(self)

        header = QHBoxLayout()
        self.label_mesa = QLabel(f"Mesa: {self.mesa[1]}")
        self.label_mesa.setObjectName("title")
        header.addWidget(self.label_mesa)
        estado_text = "Ocupada" if (len(self.mesa) > 2 and self.mesa[2] == "ocupada") else "Libre"
        self.label_estado = QLabel(f"Estado: {estado_text}")
        header.addWidget(self.label_estado)
        header.addStretch()
        main_layout.addLayout(header)

        self.input_cliente = QLineEdit()
        self.input_cliente.setPlaceholderText("Nombre del cliente")
        self.input_cliente.setMinimumHeight(28)
        self.input_cliente.setMaximumWidth(320)
        header.addWidget(QLabel("Cliente:"))
        header.addWidget(self.input_cliente)



        splitter = QSplitter(Qt.Horizontal)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Left: secciones, buscador y lista de productos con descripción
        self.list_secciones = QListWidget()
        self.list_secciones.setFixedWidth(180)
        self.list_secciones.itemClicked.connect(self.on_seccion_selected)

        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Buscar producto...")
        self.input_buscar.textChanged.connect(self.on_buscar_text_changed)

        # Productos visibles (tabla más detallada)
        self.table_productos_disponibles = QTableWidget()
        self.table_productos_disponibles.setColumnCount(3)
        self.table_productos_disponibles.setHorizontalHeaderLabels(["Producto", "Descripción", "Precio"])
        self.table_productos_disponibles.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_productos_disponibles.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_productos_disponibles.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_productos_disponibles.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_productos_disponibles.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_productos_disponibles.doubleClicked.connect(self.on_producto_double_clicked)

        # add controls
        add_row = QHBoxLayout()
        self.spin_cantidad = QSpinBox(); self.spin_cantidad.setRange(1, 1000); self.spin_cantidad.setValue(1)
        add_btn = QPushButton("Agregar seleccionado")
        add_btn.setObjectName("addBtn")
        add_btn.clicked.connect(self.agregar_producto_desde_lista)
        add_row.addWidget(QLabel("Cantidad:"))
        add_row.addWidget(self.spin_cantidad)
        add_row.addStretch()
        add_row.addWidget(add_btn)

        left_layout.addWidget(QLabel("Secciones"))
        left_layout.addWidget(self.list_secciones)
        left_layout.addWidget(self.input_buscar)
        left_layout.addWidget(self.table_productos_disponibles)
        left_layout.addLayout(add_row)

        # Right: tabla de la orden y controles
        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(5)
        self.tabla_productos.setHorizontalHeaderLabels(["Producto", "Precio", "Cantidad", "Subtotal", ""])
        self.tabla_productos.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabla_productos.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tabla_productos.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tabla_productos.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tabla_productos.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla_productos.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla_productos.cellDoubleClicked.connect(self.tabla_mouse_double_click)

        right_layout.addWidget(QLabel("Productos en la orden"))
        right_layout.addWidget(self.tabla_productos)

        # Totales y botones al pie
        footer = QHBoxLayout()
        self.label_total = QLabel("$0.00"); self.label_total.setFont(QFont("Arial", 14, QFont.Bold)); self.label_total.setStyleSheet("color:#00B03A")
        self.label_total_bolivares = QLabel(" - VES"); self.label_total_bolivares.setFont(QFont("Arial", 14, QFont.Bold)); self.label_total_bolivares.setStyleSheet("color:#4A5FFF")
        footer.addWidget(QLabel("Total:"))
        footer.addWidget(self.label_total)
        footer.addWidget(self.label_total_bolivares)
        footer.addStretch()

        self.btn_confirmar = QPushButton("Confirmar Orden"); self.btn_confirmar.setObjectName("confirmBtn")
        self.btn_confirmar.clicked.connect(self.confirmar_orden)
        self.btn_factura = QPushButton("Generar Factura"); self.btn_factura.setObjectName("factBtn"); self.btn_factura.clicked.connect(self.generar_factura); self.btn_factura.setVisible(False)
        self.btn_cancelar = QPushButton("Cancelar Orden"); self.btn_cancelar.setObjectName("cancelBtn"); self.btn_cancelar.clicked.connect(self.cancelar_orden); self.btn_cancelar.setVisible(False)
        btn_salir = QPushButton("Salir"); btn_salir.clicked.connect(self.reject)

        footer.addWidget(btn_salir)
        footer.addWidget(self.btn_confirmar)
        footer.addWidget(self.btn_factura)
        footer.addWidget(self.btn_cancelar)

        right_layout.addLayout(footer)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)







        main_layout.addWidget(splitter)

    # --------------------------
    # Inicializar estado (cargar secciones/productos/orden si aplica)
    # --------------------------
    def load_initial_state(self):
        self.cargar_secciones()
        self.cargar_todos_productos_cache()  # cache inicial
        self.mostrar_productos_en_tabla()     # todos por defecto
        orden_abierta = orden_service_module.obtener_orden_abierta_por_mesa(self.mesa[0])
        if orden_abierta:
            self.orden_id = orden_abierta[0]
            self.btn_factura.setVisible(True)
            self.btn_cancelar.setVisible(True)
            self.btn_confirmar.setVisible(False)
            self.input_buscar.setEnabled(False)
            # si el servicio devuelve cliente, lo colocamos
            try:
                self.input_cliente.setText(orden_abierta[1] or "")
            except Exception:
                pass
            self.cargar_detalles_orden()
        else:
            self.productos_seleccionados = []
            self.detalles_originales = {}
            self.actualizar_tabla_productos()
            self.input_cliente.clear()
            self.input_cliente.setEnabled(True)



    # --------------------------
    # Secciones y productos (caching y filtros)
    # --------------------------
    def cargar_secciones(self):
        self.list_secciones.clear()
        try:
            secciones = menu_service.listar_secciones(only_active=True)
        except Exception:
            secciones = []
        # primera opción: "Todos"
        item_all = QListWidgetItem("Todos")
        item_all.setData(Qt.UserRole, None)
        self.list_secciones.addItem(item_all)
        for s in secciones:
            # s: (id, nombre, descripcion, position, active)
            it = QListWidgetItem(str(s[1]))
            it.setData(Qt.UserRole, int(s[0]))
            self.list_secciones.addItem(it)
        # seleccionar "Todos"
        self.list_secciones.setCurrentRow(0)

    def cargar_todos_productos_cache(self):
        """
        Construye self._productos_list_cache: lista de dicts con keys:
        {'fuente','id','nombre','descripcion','precio','stock'}
        """
        cache: List[Dict] = []
        # menu items
        try:
            secciones = menu_service.listar_secciones(only_active=True)
            for s in secciones:
                items = menu_service.listar_items_por_seccion(s[0], only_disponible=True)
                for it in items:
                    # it: (id, section_id, nombre, descripcion, precio, disponible, position, created_at)
                    cache.append({
                        "fuente": "menu", "id": int(it[0]), "nombre": it[2] or "",
                        "descripcion": it[3] or "", "precio": float(it[4] or 0.0), "stock": None, "section_id": int(it[1])
                    })
        except Exception:
            logger.exception("Error cargando menu_items")

        # productos legacy
        try:
            filas = orden_service_module.obtener_productos_disponibles()
            for row in filas:
                cache.append({
                    "fuente": "producto", "id": int(row[0]), "nombre": row[1],
                    "descripcion": "", "precio": float(row[2]), "stock": int(row[3]) if row[3] is not None else None, "section_id": None
                })
        except Exception:
            logger.exception("Error cargando productos legacy")

        self._productos_list_cache = cache
        # construir map rápido (fuente,id) -> info
        self._productos_map.clear()
        for p in cache:
            self._productos_map[(p["fuente"], p["id"])] = p

    def mostrar_productos_en_tabla(self, section_id: Optional[int] = None, filtro_texto: str = ""):
        """
        Filtra self._productos_list_cache por sección y texto y lo muestra en table_productos_disponibles.
        """
        filtro = (filtro_texto or "").strip().lower()
        visibles = []
        for p in self._productos_list_cache:
            if section_id is not None and p.get("section_id") != section_id:
                continue
            if filtro:
                hay = filtro in p["nombre"].lower() or filtro in (p.get("descripcion","").lower())
                if not hay:
                    continue
            visibles.append(p)

        self.table_productos_disponibles.setRowCount(len(visibles))
        for r, prod in enumerate(visibles):
            name_item = QTableWidgetItem(prod["nombre"])
            desc_item = QTableWidgetItem(prod.get("descripcion",""))
            price_item = QTableWidgetItem(f"${prod['precio']:.2f}")
            # small visual hints
            if prod["fuente"] == "menu":
                name_item.setBackground(QBrush(QColor("#1b1b1f")))
            self.table_productos_disponibles.setItem(r, 0, name_item)
            self.table_productos_disponibles.setItem(r, 1, desc_item)
            self.table_productos_disponibles.setItem(r, 2, price_item)
        # mantener la lista filtrada para acciones directas
        self._productos_visible = visibles

    # --------------------------
    # Eventos UI: sección y búsqueda
    # --------------------------
    def on_seccion_selected(self, item: QListWidgetItem):
        section_id = item.data(Qt.UserRole)
        self.mostrar_productos_en_tabla(section_id=section_id, filtro_texto=self.input_buscar.text())

    def on_buscar_text_changed(self, text: str):
        cur_item = self.list_secciones.currentItem()
        section_id = cur_item.data(Qt.UserRole) if cur_item else None
        self.mostrar_productos_en_tabla(section_id=section_id, filtro_texto=text)

    # --------------------------
    # Agregar desde la lista visible (doble click o botón)
    # --------------------------
    def on_producto_double_clicked(self, index):
        row = index.row()
        if row < 0 or row >= len(getattr(self, "_productos_visible", [])):
            return
        prod = self._productos_visible[row]
        # añadimos usando la misma lógica que agregar_producto: construir línea con fuente/id
        self._agregar_linea_de_producto(prod, cantidad=self.spin_cantidad.value())

    def agregar_producto_desde_lista(self):
        sel = self.table_productos_disponibles.currentRow()
        if sel < 0:
            QMessageBox.warning(self, "Error", "Seleccione un producto de la lista")
            return
        prod = getattr(self, "_productos_visible", [])[sel]
        self._agregar_linea_de_producto(prod, cantidad=self.spin_cantidad.value())

    def _agregar_linea_de_producto(self, prod: Dict, cantidad: int = 1):
        fuente = prod["fuente"]
        pid = int(prod["id"])
        nombre = prod["nombre"]
        precio = float(prod["precio"])

        # validar stock solo para 'producto'
        if fuente == "producto":
            stock = stock_service.consultar_stock(pid)
            if stock is None:
                QMessageBox.warning(self, "Error", "No se pudo consultar stock")
                return
            # sumar con cantidades ya en orden y con detalles_originales
            existente = next((p for p in self.productos_seleccionados if p["fuente"]=="producto" and int(p["id"])==pid), None)
            cantidad_en_orden = existente["cantidad"] if existente else 0
            if pid in self.detalles_originales:
                cantidad_en_orden += int(self.detalles_originales[pid].get("cantidad_actual", self.detalles_originales[pid].get("cantidad_original", 0)))
            if cantidad + cantidad_en_orden > stock:
                QMessageBox.warning(self, "Stock insuficiente", f"No hay suficiente stock de {nombre}\nDisponible: {stock}")
                return

        # sumar o crear línea
        existente = next((p for p in self.productos_seleccionados if p["fuente"]==fuente and int(p["id"])==pid), None)
        if existente:
            existente["cantidad"] = int(existente.get("cantidad",0)) + int(cantidad)
            existente["subtotal"] = round(float(existente["precio"]) * existente["cantidad"], 2)
        else:
            line = {"fuente": fuente, "id": pid, "nombre": nombre, "descripcion": prod.get("descripcion",""), "precio": precio, "cantidad": int(cantidad), "subtotal": round(precio * cantidad, 2)}
            self.productos_seleccionados.append(line)

        self.actualizar_tabla_productos()
        self._marcar_orden_modificada_por_ui()

    # --------------------------
    # Tabla orden y edición
    # --------------------------
    def actualizar_tabla_productos(self):
        self.tabla_productos.clearContents()
        self.tabla_productos.setRowCount(len(self.productos_seleccionados))
        total = 0.0
        for r, p in enumerate(self.productos_seleccionados):
            self.tabla_productos.setItem(r, 0, QTableWidgetItem(str(p["nombre"])))
            self.tabla_productos.setItem(r, 1, QTableWidgetItem(f"${float(p['precio']):.2f}"))
            self.tabla_productos.setItem(r, 2, QTableWidgetItem(str(p["cantidad"])))
            self.tabla_productos.setItem(r, 3, QTableWidgetItem(f"${float(p['subtotal']):.2f}"))

            btn = QPushButton("Eliminar")
            btn.setStyleSheet("background-color:#e74c3c;color:white;border:none;padding:0px 0px;border-radius:4px;")
            pid = p["id"]
            btn.clicked.connect(lambda _, prod_id=pid: self.eliminar_producto_por_id(prod_id))
            self.tabla_productos.setCellWidget(r, 4, btn)

            total += float(p["subtotal"])

        self.label_total.setText(f"${total:.2f}")
        # conversión VES
        try:
            tasa = conversion_service.obtener_tasa(datetime.date.today().isoformat())
        except Exception:
            tasa = None
        if tasa:
            self.label_total_bolivares.setText(f"{round(total * tasa,2):.2f} VES (T: {tasa:.2f})")
        else:
            self.label_total_bolivares.setText(" - VES")

    def eliminar_producto_por_id(self, producto_id: int):
        antes = len(self.productos_seleccionados)
        self.productos_seleccionados = [p for p in self.productos_seleccionados if p["id"] != producto_id]
        if len(self.productos_seleccionados) != antes:
            self.actualizar_tabla_productos()
            self._marcar_orden_modificada_por_ui()


        #if self.orden_id:
        #    self.btn_factura.setVisible(False); self.btn_cancelar.setVisible(False); self.btn_confirmar.setVisible(True)

    def tabla_mouse_double_click(self, row: int, col: int):
        if row < 0 or row >= len(self.productos_seleccionados):
            return
        if col == 4:
            self.eliminar_producto_por_id(self.productos_seleccionados[row]["id"])
            return
        current = self.productos_seleccionados[row]
        cantidad, ok = QInputDialog.getInt(self, "Editar cantidad", f"Cantidad para {current['nombre']}:", current["cantidad"], 1, 1000, 1)
        if ok:
            current["cantidad"] = cantidad
            current["subtotal"] = round(current["precio"] * cantidad, 2)
            self.actualizar_tabla_productos()
            self._marcar_orden_modificada_por_ui()


            #if self.orden_id:
            #    self.btn_factura.setVisible(False); self.btn_cancelar.setVisible(False); self.btn_confirmar.setVisible(True)

    # --------------------------
    # Cargar/guardar orden y acciones (usa controller/service)
    # --------------------------
    def cargar_detalles_orden(self):
        if not self.orden_id:
            return
        detalles = orden_service_module.obtener_detalles_orden(self.orden_id)
        self.detalles_originales = {}
        self.productos_seleccionados = []
        # detalles: (detalle_id, item_id, nombre, cantidad, precio_unitario, subtotal, variant_id, fuente)
        for d in detalles:
            detalle_id = d[0]; item_id = d[1]; nombre = d[2]; cantidad = int(d[3]); precio_unitario = float(d[4] or 0.0); subtotal = float(d[5] or round(precio_unitario*cantidad,2)); fuente = d[7] or "producto"
            entry = {"fuente": fuente, "id": int(item_id), "nombre": nombre, "precio": precio_unitario, "cantidad": cantidad, "subtotal": subtotal, "detalle_id": detalle_id}
            self.productos_seleccionados.append(entry)
            if fuente == "producto":
                self.detalles_originales[int(item_id)] = {"cantidad_original": cantidad, "cantidad_actual": cantidad}
        self.actualizar_tabla_productos()

    def _calcular_total(self) -> float:
        return round(sum(float(p["subtotal"]) for p in self.productos_seleccionados), 2)

    def confirmar_orden(self):
        # montar payload para controller
        if not self.productos_seleccionados:
            QMessageBox.warning(self, "Error", "Debe agregar al menos un producto")
            return
        
        nombre_cliente = self.input_cliente.text().strip() if hasattr(self, "input_cliente") else ""
        if not nombre_cliente and not self.orden_id:
            QMessageBox.warning(self, "Error", "Ingrese nombre del cliente")
            return

        productos_payload = []
        for p in self.productos_seleccionados:
            entry = {"cantidad": int(p["cantidad"])}
            if p["fuente"] == "menu":
                entry["menu_item_id"] = int(p["id"])
            else:
                entry["producto_id"] = int(p["id"])
            entry["subtotal"] = float(p["subtotal"])
            productos_payload.append(entry)

        ok, nuevo_id, err = orden_controller_module.confirmar_orden_flow(self.mesa[0], nombre_cliente, productos_payload, self.detalles_originales, orden_id=self.orden_id)
        if not ok:
            QMessageBox.critical(self, "Error", err or "No se pudo confirmar orden")
            return

        self.orden_id = nuevo_id
        QMessageBox.information(self, "Éxito", "Orden guardada")
        # actualizar originales (solo productos físicos relevantes)
        self.detalles_originales = {p["id"]: {"cantidad_original": int(p["cantidad"]), "cantidad_actual": int(p["cantidad"])} for p in self.productos_seleccionados if p["fuente"]=="producto"}
        self.btn_confirmar.setVisible(False); self.btn_factura.setVisible(True); self.btn_cancelar.setVisible(True)
        try:
            self.estado_mesa_cambiado.emit()
        except Exception:
            pass

    def generar_factura(self):
        if not self.orden_id:
            QMessageBox.warning(self, "Error", "No hay una orden confirmada para facturar")
            return
        if not self.productos_seleccionados:
            QMessageBox.warning(self, "Error", "La orden no tiene productos")
            return

        # preparar datos legibles para la vista previa
        productos_display = []
        for p in self.productos_seleccionados:
            productos_display.append({
                "nombre": p.get("nombre",""),
                "descripcion": p.get("descripcion",""),
                "cantidad": int(p.get("cantidad",0)),
                "subtotal": float(p.get("subtotal",0.0))
            })

        # sugerir número (puede ser temporal; el controller puede validar/reemplazar si tú tienes lógica de numeración)
        numero_sugerido = f"FACT-{datetime.datetime.now().strftime('%Y%m%d')}-{random.randint(1000,9999)}"
        dlg = InvoicePreviewDialog(self.orden_id, self.input_cliente.text().strip() or "Consumidor final",
                                   productos_display, self._calcular_total(), forma_pago="Efectivo",
                                   numero_factura=numero_sugerido, parent=self)
        res = dlg.exec()
        if res == QDialog.Accepted:
            # la factura ya fue creada por el diálogo; informar y actualizar UI
            QMessageBox.information(self, "Confirmado", "La factura fue creada correctamente.")
            # refrescar estado: limpiar orden local si tu flujo lo requiere
            self.productos_seleccionados = []
            self.detalles_originales = {}
            self.orden_id = None
            self.actualizar_tabla_productos()
            self.input_cliente.clear()
            self.input_cliente.setEnabled(True)
            self.btn_factura.setVisible(False)
            self.btn_cancelar.setVisible(False)
            self.btn_confirmar.setVisible(True)
            try:
                self.estado_mesa_cambiado.emit()
            except Exception:
                pass

    def cancelar_orden(self):
        reply = QMessageBox.question(self, "Confirmar cancelación", "¿Cancelar la orden y devolver stock?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        if self.orden_id:
            ok, err = orden_controller_module.cancelar_orden_flow(self.orden_id)
            if not ok:
                QMessageBox.critical(self, "Error", err or "No se pudo cancelar orden")
                return
        self.productos_seleccionados = []; self.orden_id = None; self.detalles_originales = {}
        self.actualizar_tabla_productos(); self.reject()

    def _marcar_orden_modificada_por_ui(self):
        """
        Llamar cuando el usuario modifica la orden (agregar/quitar/editar líneas).
        - Muestra Confirmar (para que el usuario confirme la actualización).
        - Oculta Factura/Cancelar (solo aplicables cuando no hay cambios pendientes).
        """
        try:
            self.btn_confirmar.setVisible(True)
            self.btn_factura.setVisible(False)
            self.btn_cancelar.setVisible(False)
        except Exception:
            pass