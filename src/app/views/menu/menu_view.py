# src/app/views/menu/menu_view.py
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox,
    QCheckBox, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ...services import menu_service


# --- Dialogs mínimos para crear/editar secciones e items ---
class SectionDialog(QDialog):
    def __init__(self, parent=None, section: Optional[tuple] = None):
        super().__init__(parent)
        self.setWindowTitle("Sección" if section is None else "Editar Sección")
        self.section = section
        self.setup_ui()

    def setup_ui(self):
        self.setMinimumWidth(360)
        layout = QFormLayout(self)

        self.input_nombre = QLineEdit(self.section[1] if self.section else "")
        self.input_descripcion = QTextEdit(self.section[2] if self.section and len(self.section) > 2 else "")
        self.input_position = QSpinBox()
        self.input_position.setMinimum(0)
        self.input_position.setValue(self.section[3] if self.section and len(self.section) > 3 else 0)
        self.input_active = QCheckBox("Activa")
        self.input_active.setChecked(self.section[4] == 1 if self.section and len(self.section) > 4 else True)

        layout.addRow("Nombre:", self.input_nombre)
        layout.addRow("Descripción:", self.input_descripcion)
        layout.addRow("Posición:", self.input_position)
        layout.addRow("", self.input_active)

        btn_layout = QHBoxLayout()
        btn_guardar = QPushButton("Guardar")
        btn_cancel = QPushButton("Cancelar")
        btn_guardar.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_guardar)
        layout.addRow(btn_layout)

    def values(self):
        return {
            "nombre": self.input_nombre.text().strip(),
            "descripcion": self.input_descripcion.toPlainText().strip() or None,
            "position": int(self.input_position.value()),
            "active": 1 if self.input_active.isChecked() else 0
        }


class ItemDialog(QDialog):
    def __init__(self, parent=None, section_id: Optional[int] = None, item: Optional[tuple] = None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Item" if item is None else "Editar Item")
        self.section_id = section_id
        self.item = item
        self.setup_ui()

    def setup_ui(self):
        self.setMinimumWidth(420)
        layout = QFormLayout(self)

        self.input_section = QComboBox()
        # cargar secciones (id,nombre,desc,position,active)
        sections = menu_service.listar_secciones(only_active=False)
        for s in sections:
            self.input_section.addItem(s[1], s[0])
        if self.section_id:
            idx = self.input_section.findData(self.section_id)
            if idx >= 0:
                self.input_section.setCurrentIndex(idx)

        self.input_nombre = QLineEdit(self.item[2] if self.item else "")
        self.input_descripcion = QTextEdit(self.item[3] if self.item and len(self.item) > 3 else "")
        self.input_precio = QDoubleSpinBox()
        self.input_precio.setMinimum(0.0)
        self.input_precio.setDecimals(2)
        self.input_precio.setValue(self.item[4] if self.item and len(self.item) > 4 else 0.0)
        self.input_disponible = QCheckBox("Disponible")
        self.input_disponible.setChecked((self.item[5] == 1) if self.item and len(self.item) > 5 else True)
        self.input_position = QSpinBox()
        self.input_position.setMinimum(0)
        self.input_position.setValue(self.item[6] if self.item and len(self.item) > 6 else 0)

        layout.addRow("Sección:", self.input_section)
        layout.addRow("Nombre:", self.input_nombre)
        layout.addRow("Descripción:", self.input_descripcion)
        layout.addRow("Precio:", self.input_precio)
        layout.addRow("", self.input_disponible)
        layout.addRow("Posición:", self.input_position)

        btn_layout = QHBoxLayout()
        btn_guardar = QPushButton("Guardar")
        btn_cancel = QPushButton("Cancelar")
        btn_guardar.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_guardar)
        layout.addRow(btn_layout)

    def values(self):
        return {
            "section_id": int(self.input_section.currentData()),
            "nombre": self.input_nombre.text().strip(),
            "descripcion": self.input_descripcion.toPlainText().strip() or None,
            "precio": float(self.input_precio.value()),
            "disponible": 1 if self.input_disponible.isChecked() else 0,
            "position": int(self.input_position.value())
        }


# --- MenuView principal ---
class MenuView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
        self.refresh_sections()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # Left: lista de secciones y acciones sobre secciones
        left = QVBoxLayout()
        lbl_sections = QLabel("Secciones")
        lbl_sections.setFont(QFont("Segoe UI", 12, QFont.Bold))
        left.addWidget(lbl_sections)

        self.list_sections = QListWidget()
        self.list_sections.itemSelectionChanged.connect(self.on_section_selected)
        left.addWidget(self.list_sections)

        sec_btn_layout = QHBoxLayout()
        btn_new_section = QPushButton("Nueva")
        btn_edit_section = QPushButton("Editar")
        btn_delete_section = QPushButton("Eliminar")
        btn_new_section.clicked.connect(self.new_section)
        btn_edit_section.clicked.connect(self.edit_section)
        btn_delete_section.clicked.connect(self.delete_section)
        sec_btn_layout.addWidget(btn_new_section)
        sec_btn_layout.addWidget(btn_edit_section)
        sec_btn_layout.addWidget(btn_delete_section)
        left.addLayout(sec_btn_layout)

        main_layout.addLayout(left, 1)

        # Right: tabla de items por sección y acciones
        right = QVBoxLayout()
        header_layout = QHBoxLayout()
        lbl_items = QLabel("Items")
        lbl_items.setFont(QFont("Segoe UI", 12, QFont.Bold))
        header_layout.addWidget(lbl_items)

        # búsqueda y botones de item
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar items...")
        self.search_input.returnPressed.connect(self.buscar_items)
        header_layout.addStretch()
        header_layout.addWidget(self.search_input)

        right.addLayout(header_layout)

        self.table_items = QTableWidget()
        self.table_items.setColumnCount(5)
        self.table_items.setHorizontalHeaderLabels(["ID", "Nombre", "Descripción", "Precio", "Disponible"])
        self.table_items.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_items.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_items.setEditTriggers(QTableWidget.NoEditTriggers)
        right.addWidget(self.table_items)

        item_btn_layout = QHBoxLayout()
        btn_new_item = QPushButton("Nuevo Item")
        btn_edit_item = QPushButton("Editar Item")
        btn_delete_item = QPushButton("Eliminar Item")
        btn_toggle_disp = QPushButton("Alternar Disponible")
        btn_refresh = QPushButton("Refrescar")
        btn_new_item.clicked.connect(self.new_item)
        btn_edit_item.clicked.connect(self.edit_item)
        btn_delete_item.clicked.connect(self.delete_item)
        btn_toggle_disp.clicked.connect(self.toggle_disponibilidad)
        btn_refresh.clicked.connect(self.refresh_items)
        item_btn_layout.addWidget(btn_new_item)
        item_btn_layout.addWidget(btn_edit_item)
        item_btn_layout.addWidget(btn_delete_item)
        item_btn_layout.addWidget(btn_toggle_disp)
        item_btn_layout.addWidget(btn_refresh)
        right.addLayout(item_btn_layout)

        main_layout.addLayout(right, 3)

    # --- Secciones ---
    def refresh_sections(self):
        self.list_sections.clear()
        sections = menu_service.listar_secciones(only_active=False)
        for sec in sections:
            # sec: (id, nombre, descripcion, position, active)
            item = QListWidgetItem(f"{sec[1]} {'(inactiva)' if sec[4] == 0 else ''}")
            font = QFont("Segoe UI", 12)
            item.setFont(font)
            item.setData(Qt.UserRole, sec)
            self.list_sections.addItem(item)
        # seleccionar la primera sección si existe
        if self.list_sections.count() > 0:
            self.list_sections.setCurrentRow(0)
        else:
            self.table_items.setRowCount(0)

    def on_section_selected(self):
        item = self.list_sections.currentItem()
        if not item:
            return
        sec = item.data(Qt.UserRole)
        self.current_section = sec
        self.refresh_items()

    def new_section(self):
        dlg = SectionDialog(self)
        if dlg.exec() == QDialog.Accepted:
            vals = dlg.values()
            ok, err = menu_service.crear_seccion(vals["nombre"], vals["descripcion"], vals["position"])
            if not ok:
                QMessageBox.warning(self, "Error", err or "No se pudo crear la sección")
            self.refresh_sections()

    def edit_section(self):
        item = self.list_sections.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Seleccione una sección")
            return
        sec = item.data(Qt.UserRole)
        dlg = SectionDialog(self, section=sec)
        if dlg.exec() == QDialog.Accepted:
            vals = dlg.values()
            ok, err = menu_service.actualizar_seccion(sec[0], vals["nombre"], vals["descripcion"], vals["position"], vals["active"])
            if not ok:
                QMessageBox.warning(self, "Error", err or "No se pudo actualizar la sección")
            self.refresh_sections()

    def delete_section(self):
        item = self.list_sections.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Seleccione una sección")
            return
        sec = item.data(Qt.UserRole)
        resp = QMessageBox.question(self, "Confirmar", f"¿Eliminar sección '{sec[1]}'? (se recomienda desactivarla)")
        if resp == QMessageBox.Yes:
            ok, err = menu_service.eliminar_seccion(sec[0], soft=True)
            if not ok:
                QMessageBox.warning(self, "Error", err or "No se pudo eliminar/desactivar la sección")
            self.refresh_sections()

    # --- Items ---
    def refresh_items(self):
        sec = getattr(self, "current_section", None)
        if not sec:
            self.table_items.setRowCount(0)
            return
        section_id = sec[0]
        items = menu_service.listar_items_por_seccion(section_id, only_disponible=False)
        self.table_items.setRowCount(len(items))
        for row, it in enumerate(items):
            # it: (id, section_id, nombre, descripcion, precio, disponible, position, created_at)
            self.table_items.setItem(row, 0, QTableWidgetItem(str(it[0])))
            self.table_items.setItem(row, 1, QTableWidgetItem(it[2] or ""))
            self.table_items.setItem(row, 2, QTableWidgetItem(it[3] or ""))
            self.table_items.setItem(row, 3, QTableWidgetItem(f"{it[4]:.2f}"))
            self.table_items.setItem(row, 4, QTableWidgetItem("Sí" if it[5] == 1 else "No"))
        self.table_items.resizeRowsToContents()

    def new_item(self):
        sec = getattr(self, "current_section", None)
        section_id = sec[0] if sec else None
        dlg = ItemDialog(self, section_id=section_id)
        if dlg.exec() == QDialog.Accepted:
            vals = dlg.values()
            ok, err = menu_service.crear_item(vals["section_id"], vals["nombre"], vals["descripcion"], vals["precio"], vals["disponible"], vals["position"])
            if not ok:
                QMessageBox.warning(self, "Error", err or "No se pudo crear el item")
            self.refresh_items()

    def edit_item(self):
        row = self.table_items.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Seleccione un item para editar")
            return
        item_id = int(self.table_items.item(row, 0).text())
        item = menu_service.obtener_item_por_id(item_id)
        if not item:
            QMessageBox.warning(self, "Error", "Item no encontrado")
            return
        dlg = ItemDialog(self, section_id=item[1], item=item)
        if dlg.exec() == QDialog.Accepted:
            vals = dlg.values()
            ok, err = menu_service.actualizar_item(item_id, vals["section_id"], vals["nombre"], vals["descripcion"], vals["precio"], vals["disponible"], vals["position"])
            if not ok:
                QMessageBox.warning(self, "Error", err or "No se pudo actualizar el item")
            self.refresh_items()

    def delete_item(self):
        row = self.table_items.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Seleccione un item para eliminar")
            return
        item_id = int(self.table_items.item(row, 0).text())
        resp = QMessageBox.question(self, "Confirmar", "¿Eliminar item seleccionado?")
        if resp == QMessageBox.Yes:
            ok, err = menu_service.eliminar_item(item_id)
            if not ok:
                QMessageBox.warning(self, "Error", err or "No se pudo eliminar el item")
            self.refresh_items()

    def toggle_disponibilidad(self):
        row = self.table_items.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Seleccione un item")
            return
        item_id = int(self.table_items.item(row, 0).text())
        item = menu_service.obtener_item_por_id(item_id)
        if not item:
            QMessageBox.warning(self, "Error", "Item no encontrado")
            return
        new_disp = 0 if item[5] == 1 else 1
        ok, err = menu_service.toggle_disponibilidad_item(item_id, new_disp)
        if not ok:
            QMessageBox.warning(self, "Error", err or "No se pudo cambiar la disponibilidad")
        self.refresh_items()

    def buscar_items(self):
        term = self.search_input.text().strip()
        if not term:
            # si búsqueda vacía, recargar items de la sección actual
            self.refresh_items()
            return
        results = menu_service.buscar_items_por_nombre(term, only_disponible=False)
        self.table_items.setRowCount(len(results))
        for row, it in enumerate(results):
            self.table_items.setItem(row, 0, QTableWidgetItem(str(it[0])))
            self.table_items.setItem(row, 1, QTableWidgetItem(it[2] or ""))
            self.table_items.setItem(row, 2, QTableWidgetItem(it[3] or ""))
            self.table_items.setItem(row, 3, QTableWidgetItem(f"{it[4]:.2f}"))
            self.table_items.setItem(row, 4, QTableWidgetItem("Sí" if it[5] == 1 else "No"))
        self.table_items.resizeRowsToContents()