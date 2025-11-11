from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton,
    QLineEdit, QDoubleSpinBox, QSpinBox, QMessageBox,
    QDialog, QDialogButtonBox, QFormLayout, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from .controller import obtener_productos, crear_producto, actualizar_producto, eliminar_producto

class EditarProductoDialog(QDialog):
    def __init__(self, producto, parent=None):
        """
        producto: tuple (id, nombre, precio, stock)
        """
        super().__init__(parent)
        self.setWindowTitle("Editar Producto")
        self.producto = producto
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        form = QFormLayout()
        form.setSpacing(15)

        self.input_nombre = QLineEdit(self.producto[1])
        self.input_nombre.setMinimumHeight(40)
        form.addRow("Nombre:", self.input_nombre)

        self.input_precio = QDoubleSpinBox()
        self.input_precio.setValue(float(self.producto[2]))
        self.input_precio.setPrefix("$ ")
        self.input_precio.setMinimum(0.01)
        self.input_precio.setMaximum(100000)
        self.input_precio.setDecimals(2)
        self.input_precio.setMinimumHeight(40)
        form.addRow("Precio:", self.input_precio)

        self.input_stock = QSpinBox()
        self.input_stock.setValue(int(self.producto[3]))
        self.input_stock.setMinimum(0)
        self.input_stock.setMaximum(100000)
        self.input_stock.setMinimumHeight(40)
        form.addRow("Stock:", self.input_stock)

        layout.addLayout(form)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
        self.setLayout(layout)

    def get_datos(self):
        return (
            self.input_nombre.text().strip(),
            float(self.input_precio.value()),
            int(self.input_stock.value())
        )

class InventarioView(QWidget):
    def __init__(self, es_admin=False):
        super().__init__()
        self.es_admin = es_admin
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        titulo = QLabel("GESTIÓN DE INVENTARIO")
        titulo.setObjectName("titulo")
        titulo.setFont(QFont("Segoe UI", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        if self.es_admin:
            form_layout = QHBoxLayout()
            form_layout.setSpacing(12)

            self.input_nombre = QLineEdit()
            self.input_nombre.setPlaceholderText("Nombre del producto")
            self.input_nombre.setMinimumHeight(40)

            self.input_precio = QDoubleSpinBox()
            self.input_precio.setPrefix("$ ")
            self.input_precio.setMinimum(0.01)
            self.input_precio.setMaximum(100000)
            self.input_precio.setDecimals(2)
            self.input_precio.setMinimumHeight(40)
            self.input_precio.setMinimumWidth(120)

            self.input_stock = QSpinBox()
            self.input_stock.setMinimum(0)
            self.input_stock.setMaximum(100000)
            self.input_stock.setMinimumHeight(40)
            self.input_stock.setMinimumWidth(100)

            btn_agregar = QPushButton("Agregar Producto")
            btn_agregar.setMinimumHeight(45)
            btn_agregar.clicked.connect(self.agregar_producto)

            form_layout.addWidget(self.input_nombre, 3)
            form_layout.addWidget(self.input_precio, 1)
            form_layout.addWidget(self.input_stock, 1)
            form_layout.addWidget(btn_agregar, 2)

            layout.addLayout(form_layout)

        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(4)
        self.tabla_productos.setHorizontalHeaderLabels(["ID", "Producto", "Precio", "Stock"])
        self.tabla_productos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_productos.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_productos.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.tabla_productos)

        if self.es_admin:
            btn_layout = QHBoxLayout()
            btn_layout.setAlignment(Qt.AlignCenter)
            btn_layout.setSpacing(20)

            btn_editar = QPushButton("Editar Producto")
            btn_editar.setMinimumHeight(40)
            btn_editar.clicked.connect(self.editar_producto)

            btn_eliminar = QPushButton("Eliminar Producto")
            btn_eliminar.setMinimumHeight(40)
            btn_eliminar.clicked.connect(self.eliminar_producto)

            btn_layout.addWidget(btn_editar)
            btn_layout.addWidget(btn_eliminar)
            layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.cargar_productos()

    def cargar_productos(self):
        productos = obtener_productos()
        self.tabla_productos.setRowCount(len(productos))
        for row, producto in enumerate(productos):
            pid, nombre, precio, stock = producto
            self.tabla_productos.setItem(row, 0, QTableWidgetItem(str(pid)))
            self.tabla_productos.setItem(row, 1, QTableWidgetItem(nombre))
            self.tabla_productos.setItem(row, 2, QTableWidgetItem(f"${float(precio):.2f}"))
            self.tabla_productos.setItem(row, 3, QTableWidgetItem(str(stock)))

    def agregar_producto(self):
        # Solo administradores deben invocar este método (vista controla visibilidad)
        nombre = self.input_nombre.text().strip()
        precio = float(self.input_precio.value())
        stock = int(self.input_stock.value())

        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre del producto es obligatorio")
            return

        ok, err = crear_producto(nombre, precio, stock)
        if not ok:
            QMessageBox.critical(self, "Error", err or "Error al agregar producto")
            return

        self.cargar_productos()
        # Limpiar formulario
        self.input_nombre.clear()
        self.input_precio.setValue(0.01)
        self.input_stock.setValue(0)
        QMessageBox.information(self, "Éxito", "Producto agregado correctamente")

    def editar_producto(self):
        fila_seleccionada = self.tabla_productos.currentRow()
        if fila_seleccionada < 0:
            QMessageBox.warning(self, "Error", "Seleccione un producto para editar")
            return

        producto_id = int(self.tabla_productos.item(fila_seleccionada, 0).text())
        nombre = self.tabla_productos.item(fila_seleccionada, 1).text()
        precio = float(self.tabla_productos.item(fila_seleccionada, 2).text().replace("$", "").strip())
        stock = int(self.tabla_productos.item(fila_seleccionada, 3).text())

        producto = (producto_id, nombre, precio, stock)
        dialog = EditarProductoDialog(producto, self)
        if dialog.exec() == QDialog.Accepted:
            nombre_n, precio_n, stock_n = dialog.get_datos()
            if not nombre_n:
                QMessageBox.warning(self, "Error", "El nombre del producto es obligatorio")
                return
            ok, err = actualizar_producto(producto_id, nombre_n, precio_n, stock_n)
            if not ok:
                QMessageBox.critical(self, "Error", err or "Error al actualizar producto")
                return
            self.cargar_productos()
            QMessageBox.information(self, "Éxito", "Producto actualizado correctamente")

    def eliminar_producto(self):
        fila_seleccionada = self.tabla_productos.currentRow()
        if fila_seleccionada < 0:
            QMessageBox.warning(self, "Error", "Seleccione un producto para eliminar")
            return

        producto_id = int(self.tabla_productos.item(fila_seleccionada, 0).text())
        nombre = self.tabla_productos.item(fila_seleccionada, 1).text()

        respuesta = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro de eliminar el producto '{nombre}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if respuesta != QMessageBox.Yes:
            return

        ok, err = eliminar_producto(producto_id)
        if not ok:
            QMessageBox.critical(self, "Error", err or "No se pudo eliminar el producto")
            return

        self.cargar_productos()
        QMessageBox.information(self, "Éxito", "Producto eliminado correctamente")