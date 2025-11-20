# src/app/views/mesas/mesas_view.py
from typing import Optional, List, Tuple
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QScrollArea, QPushButton,
    QLineEdit, QMessageBox, QGridLayout, QGroupBox, QInputDialog, QMenu, QSizePolicy, QSplitter
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon

from ...services.mesas_service import (
    obtener_mesas, obtener_secciones, crear_mesa,
    eliminar_mesa, cambiar_estado_mesa, obtener_mesa_por_id, crear_seccion, eliminar_seccion
)
from ...services import orden_service as orden_service_module

from ...config import resource_path
from .mesas_widget import MesaWidget
from .nuevo_mesa_dialog import NuevoMesaDialog
from .editar_mesa_dialog import EditarMesaDialog
from ..orden.orden import OrdenDialog

class MesasView(QWidget):
    mesa_seleccionada = Signal(int)
    estado_mesa_cambiado = Signal()

    def __init__(self):
        super().__init__()
        self._widgets_mesa: List[MesaWidget] = []
        self._all_mesas_cache = []
        self._all_ordenes_cache = []
        self.setup_ui()
        self.cargar_secciones()
        self.actualizar_mesas()

    def setup_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        # Left: main area (titulo + scroll grid)
        main_area = QWidget()
        main_v = QVBoxLayout(main_area)
        main_v.setContentsMargins(0,0,0,0)
        main_v.setSpacing(8)

        titulo = QLabel("CONTROL DE MESAS")
        titulo.setFont(QFont("Segoe UI", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        main_v.addWidget(titulo)

        # Scroll area with grid
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.grid = QGridLayout(self.scroll_content)
        self.grid.setContentsMargins(8, 8, 8, 8)
        self.grid.setSpacing(16)
        self.scroll.setWidget(self.scroll_content)
        main_v.addWidget(self.scroll, stretch=1)

        root.addWidget(main_area, stretch=3)

        # Right: sidebar (fixed width) with controls and buscadores
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(240)
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(8, 8, 8, 8)
        sb_layout.setSpacing(10)

        # Section filter
        sb_layout.addWidget(QLabel("Sección"))
        self.combo_secciones = QComboBox()
        self.combo_secciones.setMinimumHeight(32)
        self.combo_secciones.currentIndexChanged.connect(self.actualizar_mesas)
        sb_layout.addWidget(self.combo_secciones)

        # Buscador de mesas
        sb_layout.addWidget(QLabel("Buscar mesas"))
        self.input_buscar_mesa = QLineEdit()
        self.input_buscar_mesa.setPlaceholderText("Número, estado o sección...")
        self.input_buscar_mesa.textChanged.connect(self.actualizar_mesas)
        sb_layout.addWidget(self.input_buscar_mesa)

        # Buscador de órdenes por cliente
        sb_layout.addWidget(QLabel("Buscar órdenes (cliente)"))
        self.input_buscar_orden = QLineEdit()
        self.input_buscar_orden.setPlaceholderText("Nombre del cliente...")
        self.input_buscar_orden.textChanged.connect(self.filtrar_ordenes_por_cliente)
        sb_layout.addWidget(self.input_buscar_orden)

        # Acciones principales (grupo)
        sb_layout.addWidget(QLabel("Acciones"))
        btn_group = QWidget()
        btn_group_layout = QVBoxLayout(btn_group)
        btn_group_layout.setContentsMargins(0,0,0,0)
        btn_group_layout.setSpacing(8)

        self.btn_agregar_mesa = QPushButton("Agregar Mesa")
        try:
            self.btn_agregar_mesa.setIcon(QIcon(str(resource_path("icons","add.png"))))
        except Exception:
            pass
        self.btn_agregar_mesa.clicked.connect(self.agregar_mesa)
        btn_group_layout.addWidget(self.btn_agregar_mesa)

        self.btn_eliminar_mesa = QPushButton("Eliminar Mesa")
        try:
            self.btn_eliminar_mesa.setIcon(QIcon(str(resource_path("icons","delete.png"))))
        except Exception:
            pass
        self.btn_eliminar_mesa.clicked.connect(self.eliminar_mesa)
        btn_group_layout.addWidget(self.btn_eliminar_mesa)

        self.btn_agregar_seccion = QPushButton("Agregar Sección")
        self.btn_agregar_seccion.clicked.connect(self.agregar_seccion)
        btn_group_layout.addWidget(self.btn_agregar_seccion)

        self.btn_eliminar_seccion = QPushButton("Eliminar Sección")
        self.btn_eliminar_seccion.clicked.connect(self.eliminar_seccion)
        btn_group_layout.addWidget(self.btn_eliminar_seccion)

        btn_group_layout.addSpacing(6)

        self.btn_nueva_orden = QPushButton("Crear nueva orden")
        self.btn_nueva_orden.clicked.connect(self.crear_nueva_orden)
        btn_group_layout.addWidget(self.btn_nueva_orden)

        # Spacer dentro del grupo para empujar botones al top si hay scroll
        btn_group_layout.addStretch()
        sb_layout.addWidget(btn_group)

        # Listado rápido de órdenes abiertas
        sb_layout.addWidget(QLabel("Órdenes abiertas"))
        self.combo_ordenes = QComboBox()
        self.combo_ordenes.currentIndexChanged.connect(self.on_orden_seleccionada)
        sb_layout.addWidget(self.combo_ordenes)

        # Footer del sidebar (info)
        sb_layout.addStretch()
        lbl_info = QLabel("Panel de control\nAcciones rápidas y búsqueda")
        lbl_info.setAlignment(Qt.AlignCenter)
        sb_layout.addWidget(lbl_info)

        root.addWidget(sidebar, stretch=0)

        stylesheet = """
        QComboBox {
            background-color: #1b1b1f;       /* fondo de la caja */
            color: #e8e8e8;                 /* texto */
            border: 1px solid #333;         /* borde */
            padding: 6px 10px;
            border-radius: 6px;
            outline: none;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: right center;
            width: 24px;
            border-left: 1px solid #333;
        }
        QComboBox QAbstractItemView {       /* estilo del listado desplegable */
            background-color: #15151a;     /* fondo del popup */
            color: #e8e8e8;                /* color de texto de los items */
            selection-background-color: #2b2b31;
            selection-color: #ffffff;
            outline: none;
        }
        QComboBox::item {                   /* estilos (según plataforma) */
            height: 28px;
            padding: 4px 8px;
        }
        """
        self.combo_ordenes.setStyleSheet(stylesheet)
        



    # -------------------------
    # Carga y filtro
    # -------------------------
    def cargar_secciones(self):
        self.combo_secciones.blockSignals(True)
        try:
            self.combo_secciones.clear()
            self.combo_secciones.addItem("Todas", None)
            for sid, nombre in obtener_secciones():
                self.combo_secciones.addItem(nombre, sid)
            self.combo_secciones.setCurrentIndex(0)
        finally:
            self.combo_secciones.blockSignals(False)

    def cargar_cache_mesas_y_ordenes(self):
        self._all_mesas_cache = obtener_mesas()
        try:
            rows = orden_service_module.listar_ordenes_abiertas()
        except Exception:
            rows = []
        self._all_ordenes_cache = rows

        self.combo_ordenes.blockSignals(True)
        self.combo_ordenes.clear()
        self.combo_ordenes.addItem("Seleccionar orden...", None)
        for oid, mesa_id, cliente, total, fecha in rows:
            label = f"{cliente} — Mesa {mesa_id} — ${float(total):.2f}"
            self.combo_ordenes.addItem(label, oid)
        self.combo_ordenes.blockSignals(False)

    def actualizar_mesas(self):
        self.cargar_cache_mesas_y_ordenes()
        # limpiar grid
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()
        seccion_filtrar = self.combo_secciones.currentData()
        busca = (self.input_buscar_mesa.text() or "").strip().lower()

        mesas_por_seccion = {}
        nombres_seccion = {}
        for mid, numero, estado, sec_id, sec_nombre in self._all_mesas_cache:
            mesas_por_seccion.setdefault(sec_id, []).append((mid, numero, estado, sec_id, sec_nombre))
            nombres_seccion[sec_id] = sec_nombre or "Sin sección"

        if not mesas_por_seccion:
            placeholder = QLabel("No hay mesas registradas")
            placeholder.setAlignment(Qt.AlignCenter)
            self.grid.addWidget(placeholder, 0, 0)
            return

        cols = 3
        row_block = 0
        for sec_id, lista in sorted(mesas_por_seccion.items(), key=lambda t: (t[0] or 0)):
            if seccion_filtrar is not None and sec_id != seccion_filtrar:
                continue
            group = QGroupBox(nombres_seccion.get(sec_id, "Sin sección"))
            inner = QGridLayout()
            inner.setSpacing(12)
            r = 0; c = 0
            for mid, numero, estado, sid, sec_nombre in sorted(lista, key=lambda x: x[1]):
                if busca:
                    if busca not in str(numero).lower() and busca not in (estado or "").lower() and busca not in (sec_nombre or "").lower():
                        continue
                widget = MesaWidget((mid, numero, estado, sid, sec_nombre), parent=self)
                widget.abrir_orden.connect(self._on_widget_abrir_orden)
                widget.ver_orden.connect(self._on_widget_ver_orden)
                widget.setContextMenuPolicy(Qt.CustomContextMenu)
                widget.customContextMenuRequested.connect(lambda pos, w=widget: self.mostrar_menu_contextual(w, pos))
                inner.addWidget(widget, r, c)
                self._widgets_mesa.append(widget)
                c += 1
                if c >= cols:
                    c = 0; r += 1
            group.setLayout(inner)
            self.grid.addWidget(group, row_block, 0)
            row_block += 1

    # -------------------------
    # Eventos y handlers
    # -------------------------
    def _on_widget_abrir_orden(self, mesa_id: int):
        self.abrir_orden(mesa_id)

    def _on_widget_ver_orden(self, mesa_id: int):
        self.abrir_orden(mesa_id)

    def abrir_orden(self, mesa):
        mesa_id = mesa if isinstance(mesa, int) else (mesa[0] if mesa else None)
        if mesa_id is None:
            QMessageBox.critical(self, "Error", "ID de mesa inválido")
            return
        mesa_actualizada = obtener_mesa_por_id(mesa_id)
        if not mesa_actualizada:
            QMessageBox.critical(self, "Error", "Mesa no encontrada")
            return
        try:
            dialog = OrdenDialog(mesa_actualizada, parent=self)
            try:
                dialog.estado_mesa_cambiado.connect(self.actualizar_mesas)
            except Exception:
                pass
            dialog.exec()
            self.actualizar_mesas()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir orden: {e}")

    def filtrar_ordenes_por_cliente(self, texto: str):
        """
        Buscar órdenes abiertas por nombre de cliente.
        Recarga la lista de órdenes antes de buscar para evitar desincronía con la cache.
        Si encuentra coincidencia abre la primera orden encontrada.
        """
        t = (texto or "").strip().lower()
        if not t:
            return

        # recargar cache de órdenes abiertas
        try:
            rows = orden_service_module.listar_ordenes_abiertas()
        except Exception:
            rows = []

        # normalizar y buscar substring en el campo cliente
        for oid, mesa_id, cliente, total, fecha in rows:
            cliente_norm = (cliente or "").strip().lower()
            if t in cliente_norm:
                try:
                    orden = orden_service_module.obtener_orden_por_id(oid)
                    if orden:
                        mesa_id_orden = orden.get("mesa_id")
                        mesa = obtener_mesa_por_id(mesa_id_orden) if mesa_id_orden else (None, "Sin mesa", "libre")
                        dialog = OrdenDialog(mesa, parent=self)
                        try:
                            dialog.cargar_orden_por_id(oid)
                        except Exception:
                            pass
                        dialog.exec()
                        # actualizar vistas y caches después de cerrar
                        self.actualizar_mesas()
                        return
                except Exception:
                    # si algo falla con una orden particular, continuar buscando otras coincidencias
                    continue

    def on_orden_seleccionada(self, idx: int):
        orden_id = self.combo_ordenes.currentData()
        if orden_id:
            try:
                orden = orden_service_module.obtener_orden_por_id(orden_id)
                if orden:
                    mesa_id = orden.get("mesa_id")
                    mesa = obtener_mesa_por_id(mesa_id) if mesa_id else (None, "Sin mesa", "libre")
                    dialog = OrdenDialog(mesa, parent=self)
                    try:
                        dialog.cargar_orden_por_id(orden_id)
                    except Exception:
                        pass
                    dialog.exec()
                    self.actualizar_mesas()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo abrir orden: {e}")

    # -------------------------
    # Crear / editar / eliminar mesas / secciones
    # -------------------------
    def crear_nueva_orden(self):
        cliente, ok = QInputDialog.getText(self, "Nuevo cliente", "Nombre del cliente (opcional):")
        if not ok:
            return
        mesas = self._all_mesas_cache or obtener_mesas()
        opciones = [f"{m[1]} — {m[4] or 'Sin sección'} ({m[2]})" for m in mesas]
        if not opciones:
            QMessageBox.warning(self, "Error", "No hay mesas disponibles. Crea una mesa primero.")
            return
        sel, ok = QInputDialog.getItem(self, "Asignar mesa", "Seleccione mesa:", opciones, 0, False)
        if not ok:
            return
        idx = opciones.index(sel)
        mesa_tuple = mesas[idx]
        dialog = OrdenDialog((mesa_tuple[0], mesa_tuple[1], mesa_tuple[2], mesa_tuple[3], mesa_tuple[4]), parent=self)
        try:
            dialog.input_cliente.setText(cliente or "")
        except Exception:
            pass
        dialog.exec()
        self.actualizar_mesas()

    def agregar_mesa(self):
        numero, ok = QInputDialog.getInt(self, "Nueva Mesa", "Número de mesa:", 1, 1, 999)
        if not ok:
            return
        seccion_id = self.combo_secciones.currentData()
        if seccion_id is None:
            secciones = obtener_secciones()
            if not secciones:
                QMessageBox.warning(self, "Error", "Debe crear primero una sección")
                return
            nombres = [s[1] for s in secciones]
            nombre_sel, ok = QInputDialog.getItem(self, "Sección", "Seleccione sección:", nombres, 0, False)
            if not ok or not nombre_sel:
                return
            seccion_id = next((s[0] for s in secciones if s[1] == nombre_sel), None)
        if crear_mesa(numero, seccion_id):
            QMessageBox.information(self, "Éxito", f"Mesa {numero} creada")
            self.cargar_secciones()
            self.actualizar_mesas()
        else:
            QMessageBox.critical(self, "Error", "No se pudo crear la mesa (número duplicado)")

    def editar_mesa(self, mesa_id: int):
        mesa = obtener_mesa_por_id(mesa_id)
        if not mesa:
            QMessageBox.critical(self, "Error", "Mesa no encontrada")
            return
        dialog = EditarMesaDialog(mesa, self)
        if dialog.exec():
            self.cargar_secciones()
            self.actualizar_mesas()

    def eliminar_mesa(self):
        mesas = obtener_mesas()
        if not mesas:
            QMessageBox.information(self, "Información", "No hay mesas para eliminar")
            return
        numeros = [str(m[1]) for m in mesas]
        numero_seleccionado, ok = QInputDialog.getItem(
            self, "Eliminar Mesa", "Seleccione la mesa a eliminar:", numeros, 0, False
        )
        if not ok or not numero_seleccionado:
            return
        mesa_obj = next((m for m in mesas if str(m[1]) == numero_seleccionado), None)
        if not mesa_obj:
            QMessageBox.warning(self, "Error", "Mesa no encontrada")
            return
        mesa_id, mesa_numero, mesa_estado, *_ = mesa_obj
        if mesa_estado == "ocupada":
            QMessageBox.warning(self, "Error", "No se puede eliminar una mesa ocupada")
            return
        ok_del = eliminar_mesa(mesa_id)
        if not ok_del:
            QMessageBox.critical(self, "Error", "No se pudo eliminar la mesa (puede tener órdenes abiertas)")
            return
        QMessageBox.information(self, "Éxito", f"Mesa {mesa_numero} eliminada correctamente")
        self.cargar_secciones()
        self.actualizar_mesas()

    def mostrar_menu_contextual(self, widget: MesaWidget, pos):
        m = QMenu(self)
        act_editar = m.addAction("Editar Mesa")
        act_toggle = m.addAction("Alternar Estado")
        act_abrir = m.addAction("Abrir Orden")
        accion = m.exec_(widget.mapToGlobal(pos))
        if accion == act_editar:
            self.editar_mesa(widget.mesa_id)
        elif accion == act_toggle:
            nuevo = "libre" if widget.estado != "libre" else "ocupada"
            if cambiar_estado_mesa(widget.mesa_id, nuevo):
                widget.actualizar_estado(nuevo)
                self.estado_mesa_cambiado.emit()
            else:
                QMessageBox.critical(self, "Error", "No se pudo cambiar el estado")
        elif accion == act_abrir:
            self.abrir_orden(widget.mesa_id)

    def agregar_seccion(self):
        nombre, ok = QInputDialog.getText(self, "Nueva Sección", "Nombre de la sección:")
        if not ok or not nombre.strip():
            return
        sid = crear_seccion(nombre.strip())
        if sid:
            QMessageBox.information(self, "Éxito", f"Sección '{nombre}' creada")
            self.cargar_secciones()
            self.actualizar_mesas()
        else:
            QMessageBox.critical(self, "Error", "No se pudo crear la sección (puede existir ya)")

    def eliminar_seccion(self):
        secciones = obtener_secciones()
        if not secciones:
            QMessageBox.information(self, "Información", "No hay secciones registradas")
            return
        nombres = [s[1] for s in secciones]
        nombre_sel, ok = QInputDialog.getItem(
            self, "Eliminar Sección", "Seleccione la sección a eliminar:", nombres, 0, False
        )
        if not ok or not nombre_sel:
            return
        sec_id = next((s[0] for s in secciones if s[1] == nombre_sel), None)
        if sec_id is None:
            QMessageBox.warning(self, "Error", "Sección no encontrada")
            return
        if eliminar_seccion(sec_id):
            QMessageBox.information(self, "Éxito", f"Sección '{nombre_sel}' eliminada")
            self.cargar_secciones()
            self.actualizar_mesas()
        else:
            QMessageBox.critical(self, "Error", f"No se pudo eliminar la sección '{nombre_sel}' (tiene mesas asociadas)")