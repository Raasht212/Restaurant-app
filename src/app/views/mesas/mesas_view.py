# src/app/views/mesas/mesas_view.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QScrollArea, QPushButton,
    QHBoxLayout, QMessageBox, QGridLayout, QGroupBox, QInputDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon

from ...services.mesas_service import (
    obtener_mesas, obtener_secciones, crear_mesa,
    eliminar_mesa, cambiar_estado_mesa, obtener_mesa_por_id, crear_seccion, eliminar_seccion
)

from ...config import resource_path
from .mesa_button import MesaButton
from .nuevo_mesa_dialog import NuevoMesaDialog
from .editar_mesa_dialog import EditarMesaDialog
from ..orden.orden import OrdenDialog  # import relativo correcto desde views/mesas -> views/orden

class MesasView(QWidget):
    mesa_seleccionada = Signal(int)
    estado_mesa_cambiado = Signal()

    def __init__(self):
        super().__init__()
        self._botones = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 10, 20, 20)
        layout.setSpacing(15)

        titulo = QLabel("CONTROL DE MESAS")
        titulo.setObjectName("titulo")
        titulo.setFont(QFont("Segoe UI", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filtrar por sección:"))

        self.combo_secciones = QComboBox()
        self.combo_secciones.setMinimumHeight(35)
        self.combo_secciones.currentIndexChanged.connect(self.filtrar_mesas)
        filter_layout.addWidget(self.combo_secciones)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Área de scroll con grid interno
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.NoFrame)

        self.scroll_content = QWidget()
        self.grid = QGridLayout(self.scroll_content)
        self.grid.setContentsMargins(10, 10, 10, 10)
        self.grid.setSpacing(20)
        self.scroll.setWidget(self.scroll_content)
        layout.addWidget(self.scroll)

        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.setSpacing(30)

        btn_agregar_mesa = QPushButton("Agregar Mesa")
        btn_agregar_mesa.setIcon(QIcon(str(resource_path("icons", "add.png"))))
        btn_agregar_mesa.clicked.connect(self.agregar_mesa)

        btn_eliminar = QPushButton("Eliminar Mesa")
        btn_eliminar.setIcon(QIcon(str(resource_path("icons", "delete.png"))))
        btn_eliminar.clicked.connect(self.eliminar_mesa)

        btn_agregar_seccion = QPushButton("Agregar Sección")
        btn_agregar_seccion.setIcon(QIcon(str(resource_path("icons", "add_section.png"))))
        btn_agregar_seccion.clicked.connect(self.agregar_seccion)
        
        btn_eliminar_seccion = QPushButton("Eliminar Sección")
        btn_eliminar_seccion.setIcon(QIcon(str(resource_path("icons", "delete_section.png"))))
        btn_eliminar_seccion.clicked.connect(self.eliminar_seccion)
        
        btn_layout.addWidget(btn_agregar_mesa)
        btn_layout.addWidget(btn_eliminar)
        btn_layout.addWidget(btn_agregar_seccion)
        btn_layout.addWidget(btn_eliminar_seccion)
        layout.addLayout(btn_layout)



        self.setLayout(layout)
        self.cargar_secciones()
        self.actualizar_mesas()

    def cargar_secciones(self):
        self.combo_secciones.blockSignals(True)
        try:
            self.combo_secciones.clear()
            self.combo_secciones.addItem("Todas las secciones", None)
            for sid, nombre in obtener_secciones():  # [(id, nombre)]
                self.combo_secciones.addItem(nombre, sid)
            self.combo_secciones.setCurrentIndex(0)
        finally:
            self.combo_secciones.blockSignals(False)

    def agregar_seccion(self):
        nombre, ok = QInputDialog.getText(self, "Nueva Sección", "Nombre de la sección:")
        if not ok or not nombre.strip():
            return
        sid = crear_seccion(nombre.strip())
        if sid:
            QMessageBox.information(self, "Éxito", f"Sección '{nombre}' creada")
            self.cargar_secciones()
        else:
            QMessageBox.critical(self, "Error", "No se pudo crear la sección (puede existir ya)")

    def filtrar_mesas(self):
        self.actualizar_mesas()

    def actualizar_mesas(self):
        # Limpiar grid
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        self._botones = []
        seccion_filtrar = self.combo_secciones.currentData()  # None o id

        mesas = obtener_mesas()  # (id, numero, estado, seccion_id, seccion_nombre)
        mesas_por_seccion = {}
        nombres_seccion = {}

        for mid, numero, estado, sec_id, sec_nombre in mesas:
            key = sec_id
            mesas_por_seccion.setdefault(key, []).append((mid, numero, estado))
            nombres_seccion[key] = sec_nombre or "Sin sección"

        if not mesas_por_seccion:
            placeholder = QLabel("No hay mesas registradas")
            placeholder.setAlignment(Qt.AlignCenter)
            self.grid.addWidget(placeholder, 0, 0)
            return

        cols = 3
        row_sec = 0
        for sec_id, lista_mesas in mesas_por_seccion.items():
            # si hay filtro y no coincide el id, saltar
            if seccion_filtrar is not None and sec_id != seccion_filtrar:
                continue

            group_box = QGroupBox(nombres_seccion.get(sec_id, "Sin sección"))
            inner_grid = QGridLayout()
            inner_grid.setSpacing(20)

            row = 0
            col = 0
            max_cols = cols
            for mid, numero, estado in lista_mesas:
                btn = MesaButton((mid, numero, estado, sec_id, nombres_seccion.get(sec_id)), parent=self)
                btn.clicked.connect(lambda _, mid=mid: self.abrir_orden(mid))
                btn.setContextMenuPolicy(Qt.CustomContextMenu)
                btn.customContextMenuRequested.connect(lambda pos, b=btn: self.mostrar_menu_contextual(b, pos))
                inner_grid.addWidget(btn, row, col)
                self._botones.append(btn)
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

            group_box.setLayout(inner_grid)
            self.grid.addWidget(group_box, row_sec, 0)
            row_sec += 1

    def abrir_orden(self, mesa):
        # mesa puede ser id (int) o tupla; normalizamos a id
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
            # recargar tras cerrar orden
            self.actualizar_mesas()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir orden: {e}")

    def agregar_mesa(self):
        from PySide6.QtWidgets import QInputDialog
        numero, ok = QInputDialog.getInt(self, "Nueva Mesa", "Número de mesa:", 1, 1, 999)
        if not ok:
            return

        # tomar la sección del combo o pedirla si está en "Todas"
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

        mesa_id, mesa_numero, mesa_estado, *_ = mesa_obj  # ignora seccion_id y nombre
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

    def mostrar_menu_contextual(self, button: MesaButton, pos):
        from PySide6.QtWidgets import QMenu
        m = QMenu(self)
        act_editar = m.addAction("Editar Mesa")
        act_toggle = m.addAction("Alternar Estado")
        act_abrir = m.addAction("Abrir Orden")
        accion = m.exec_(button.mapToGlobal(pos))
        if accion == act_editar:
            self.editar_mesa(button.mesa_id)
        elif accion == act_toggle:
            nuevo = "libre" if button.estado != "libre" else "ocupada"
            if cambiar_estado_mesa(button.mesa_id, nuevo):
                button.actualizar_estado(nuevo)
                self.estado_mesa_cambiado.emit()
            else:
                QMessageBox.critical(self, "Error", "No se pudo cambiar el estado")
        elif accion == act_abrir:
            self.abrir_orden(button.mesa_id)
            
            
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