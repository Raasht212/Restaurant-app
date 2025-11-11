from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QScrollArea, QPushButton,
    QHBoxLayout, QMessageBox, QGridLayout, QGroupBox, QInputDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon
from .controller import (
    obtener_mesas, obtener_secciones, crear_mesa,
    eliminar_mesa, cambiar_estado_mesa, obtener_mesa_por_id
)
from .mesa_button import MesaButton
from .nuevo_mesa_dialog import NuevoMesaDialog
from .editar_mesa_dialog import EditarMesaDialog
from views.orden.orden import OrdenDialog  # Asegúrate que OrdenDialog acepta (mesa_tuple, parent)

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

        btn_agregar = QPushButton("Agregar Mesa")
        btn_agregar.setIcon(QIcon("resources/icons/add.png"))
        btn_agregar.setMinimumHeight(40)
        btn_agregar.clicked.connect(self.agregar_mesa)

        btn_eliminar = QPushButton("Eliminar Mesa")
        btn_eliminar.setIcon(QIcon("resources/icons/delete.png"))
        btn_eliminar.setMinimumHeight(40)
        btn_eliminar.clicked.connect(self.eliminar_mesa)

        btn_layout.addWidget(btn_agregar)
        btn_layout.addWidget(btn_eliminar)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.cargar_secciones()
        self.actualizar_mesas()

    def cargar_secciones(self):
        self.combo_secciones.clear()
        self.combo_secciones.addItem("Todas las secciones", None)
        secciones = obtener_secciones()
        for s in secciones:
            self.combo_secciones.addItem(s, s)

    def filtrar_mesas(self):
        self.actualizar_mesas()

    def actualizar_mesas(self):
        # Limpiar grid
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self._botones = []
        seccion_filtrar = self.combo_secciones.currentData()

        mesas = obtener_mesas()
        # Agrupar por sección (mantener orden)
        mesas_por_seccion = {}
        for m in mesas:
            sec = m[3] or "Sin sección"
            mesas_por_seccion.setdefault(sec, []).append(m)

        if not mesas_por_seccion:
            placeholder = QLabel("No hay mesas registradas")
            placeholder.setAlignment(Qt.AlignCenter)
            self.grid.addWidget(placeholder, 0, 0)
            return

        cols = 3
        for sec_idx, (sec, mesas_sec) in enumerate(mesas_por_seccion.items()):
            # Si existe filtro y no coincide, saltar
            if seccion_filtrar and sec != seccion_filtrar:
                continue

            # Group box por sección
            group_box = QGroupBox(sec)
            group_box.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    font-size: 14pt;
                    color: #800020;
                    border: 2px solid #800020;
                    border-radius: 10px;
                    margin-top: 20px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    padding: 0 10px;
                    background-color: #F5F5DC;
                }
            """)
            inner_grid = QGridLayout()
            inner_grid.setSpacing(20)

            row = 0
            col = 0
            max_cols = cols
            for mesa in mesas_sec:
                btn = MesaButton(mesa, parent=self)
                # conectar con id de forma segura
                btn.clicked.connect(lambda _, mid=mesa[0]: self.abrir_orden(mid))
                btn.setContextMenuPolicy(Qt.CustomContextMenu)
                btn.customContextMenuRequested.connect(lambda pos, b=btn: self.mostrar_menu_contextual(b, pos))
                inner_grid.addWidget(btn, row, col)
                self._botones.append(btn)
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

            group_box.setLayout(inner_grid)
            # Colocar groupbox en la grid principal por sección
            # Para simplicidad colocamos verticalmente (cada sección en una fila)
            self.grid.addWidget(group_box, sec_idx, 0)

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
            # Si la orden afecta el estado de la mesa, OrdenDialog debería emitir estado_mesa_cambiado
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
        dialog = NuevoMesaDialog(self)
        if dialog.exec():
            self.cargar_secciones()
            self.actualizar_mesas()

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
        # Pedir selección mediante QInputDialog con números existentes
        mesas = obtener_mesas()
        if not mesas:
            QMessageBox.information(self, "Información", "No hay mesas para eliminar")
            return
        numeros = [str(m[1]) for m in mesas]
        numero_seleccionado, ok = QInputDialog.getItem(
            self,
            "Eliminar Mesa",
            "Seleccione la mesa a eliminar:",
            numeros,
            0,
            False
        )
        if not ok or not numero_seleccionado:
            return
        # buscar mesa por número
        mesa_obj = next((m for m in mesas if str(m[1]) == numero_seleccionado), None)
        if not mesa_obj:
            QMessageBox.warning(self, "Error", "Mesa no encontrada")
            return
        mesa_id, mesa_numero, mesa_estado, _ = mesa_obj
        if mesa_estado == "ocupada":
            QMessageBox.warning(self, "Error", "No se puede eliminar una mesa ocupada")
            return
        # verificar con controller si se puede eliminar
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