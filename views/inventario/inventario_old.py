from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QHeaderView, QPushButton, 
    QLineEdit, QDoubleSpinBox, QSpinBox, QMessageBox,
    QDialog, QDialogButtonBox, QFormLayout, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from database import crear_conexion, sqlite3

class EditarProductoDialog(QDialog):
    def __init__(self, producto, parent=None):
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
        self.input_precio.setValue(self.producto[2])
        self.input_precio.setPrefix("$ ")
        self.input_precio.setMinimum(0.01)
        self.input_precio.setMaximum(10000)
        self.input_precio.setMinimumHeight(40)
        form.addRow("Precio:", self.input_precio)
        
        self.input_stock = QSpinBox()
        self.input_stock.setValue(self.producto[3])
        self.input_stock.setMinimum(0)
        self.input_stock.setMaximum(10000)
        self.input_stock.setMinimumHeight(40)
        form.addRow("Stock:", self.input_stock)
        
        layout.addLayout(form)
        
        # Botones
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        btn_box.setStyleSheet("""
            QPushButton {
                min-width: 80px;
                min-height: 35px;
                padding: 5px;
            }
        """)
        
        layout.addWidget(btn_box)
        self.setLayout(layout)
    
    def get_datos(self):
        return (
            self.input_nombre.text().strip(),
            self.input_precio.value(),
            self.input_stock.value()
        )

class InventarioView(QWidget):
    def __init__(self, es_admin=False):
        super().__init__()
        print(f"Creando InventarioView con es_admin={es_admin}")  # Para depuración
        self.es_admin = es_admin
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Título
        titulo = QLabel("GESTIÓN DE INVENTARIO")
        titulo.setObjectName("titulo")
        titulo.setFont(QFont("Segoe UI", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Solo mostrar controles de modificación si es administrador
        if self.es_admin:
            print("Mostrando controles de admin en inventario")  # Para depuración
            
            # Formulario para agregar productos
            form_layout = QHBoxLayout()
            form_layout.setSpacing(15)
            
            self.input_nombre = QLineEdit()
            self.input_nombre.setPlaceholderText("Nombre del producto")
            self.input_nombre.setMinimumHeight(40)
            
            self.input_precio = QDoubleSpinBox()
            self.input_precio.setPrefix("$ ")
            self.input_precio.setMinimum(0.01)
            self.input_precio.setMaximum(10000)
            self.input_precio.setDecimals(2)
            self.input_precio.setMinimumHeight(40)
            self.input_precio.setMinimumWidth(120)
            
            self.input_stock = QSpinBox()
            self.input_stock.setMinimum(0)
            self.input_stock.setMaximum(10000)
            self.input_stock.setMinimumHeight(40)
            self.input_stock.setMinimumWidth(100)
            
            btn_agregar = QPushButton("Agregar Producto")
            btn_agregar.setMinimumHeight(45)
            btn_agregar.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: #333333;
                    font-weight: bold;
                    border-radius: 5px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #219653;
                }
            """)
            btn_agregar.clicked.connect(self.agregar_producto)
            
            form_layout.addWidget(self.input_nombre, 3)
            form_layout.addWidget(self.input_precio, 1)
            form_layout.addWidget(self.input_stock, 1)
            form_layout.addWidget(btn_agregar, 2)
            
            layout.addLayout(form_layout)
        
        # Tabla de productos (visible para todos)
        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(4)
        self.tabla_productos.setHorizontalHeaderLabels(["ID", "Producto", "Precio", "Stock"])
        self.tabla_productos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_productos.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_productos.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_productos.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #800020;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #800020;
                color: white;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.tabla_productos)
        
        # Solo mostrar botones de acción si es administrador
        if self.es_admin:
            btn_layout = QHBoxLayout()
            btn_layout.setAlignment(Qt.AlignCenter)
            btn_layout.setSpacing(30)
            
            btn_editar = QPushButton("Editar Producto")
            btn_editar.setMinimumHeight(45)
            btn_editar.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: #333333;
                    font-weight: bold;
                    border-radius: 5px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            btn_editar.clicked.connect(self.editar_producto)
            
            btn_eliminar = QPushButton("Eliminar Producto")
            btn_eliminar.setMinimumHeight(45)
            btn_eliminar.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: #333333;
                    font-weight: bold;
                    border-radius: 5px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            btn_eliminar.clicked.connect(self.eliminar_producto)
            
            btn_layout.addWidget(btn_editar)
            btn_layout.addWidget(btn_eliminar)
            layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        self.cargar_productos()
    
    def cargar_productos(self):
        conexion = crear_conexion()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute("SELECT id, nombre, precio, stock FROM productos")
                productos = cursor.fetchall()
                
                self.tabla_productos.setRowCount(len(productos))
                
                for row, producto in enumerate(productos):
                    self.tabla_productos.setItem(row, 0, QTableWidgetItem(str(producto[0])))
                    self.tabla_productos.setItem(row, 1, QTableWidgetItem(producto[1]))
                    self.tabla_productos.setItem(row, 2, QTableWidgetItem(f"${producto[2]:.2f}"))
                    self.tabla_productos.setItem(row, 3, QTableWidgetItem(str(producto[3])))
                    
            except Exception as e:
                print(f"Error cargando productos: {e}")
            finally:
                conexion.close()
    
    def agregar_producto(self):
        # Esta función solo es accesible para administradores
        nombre = self.input_nombre.text().strip()
        precio = self.input_precio.value()
        stock = self.input_stock.value()
        
        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre del producto es obligatorio")
            return
            
        conexion = crear_conexion()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute(
                    "INSERT INTO productos (nombre, precio, stock) VALUES (?, ?, ?)",
                    (nombre, precio, stock)
                )
                conexion.commit()
                self.cargar_productos()
                
                # Limpiar formulario
                self.input_nombre.clear()
                self.input_precio.setValue(0.01)
                self.input_stock.setValue(0)
                
                QMessageBox.information(self, "Éxito", "Producto agregado correctamente")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al agregar producto: {str(e)}")
            finally:
                conexion.close()
    
    def editar_producto(self):
        # Esta función solo es accesible para administradores
        fila_seleccionada = self.tabla_productos.currentRow()
        if fila_seleccionada < 0:
            QMessageBox.warning(self, "Error", "Seleccione un producto para editar")
            return
            
        producto_id = int(self.tabla_productos.item(fila_seleccionada, 0).text())
        nombre = self.tabla_productos.item(fila_seleccionada, 1).text()
        precio = float(self.tabla_productos.item(fila_seleccionada, 2).text().replace('$', ''))
        stock = int(self.tabla_productos.item(fila_seleccionada, 3).text())
        
        producto = (producto_id, nombre, precio, stock)
        
        dialog = EditarProductoDialog(producto, self)
        if dialog.exec():
            nombre, precio, stock = dialog.get_datos()
            
            if not nombre:
                QMessageBox.warning(self, "Error", "El nombre del producto es obligatorio")
                return
                
            conexion = crear_conexion()
            if conexion:
                try:
                    cursor = conexion.cursor()
                    cursor.execute(
                        "UPDATE productos SET nombre = ?, precio = ?, stock = ? WHERE id = ?",
                        (nombre, precio, stock, producto_id)
                    )
                    conexion.commit()
                    self.cargar_productos()
                    QMessageBox.information(self, "Éxito", "Producto actualizado correctamente")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error al actualizar producto: {str(e)}")
                finally:
                    conexion.close()
    
    def eliminar_producto(self):
        # Esta función solo es accesible para administradores
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
        
        if respuesta == QMessageBox.Yes:
            conexion = crear_conexion()
            if conexion:
                try:
                    cursor = conexion.cursor()
                    cursor.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
                    conexion.commit()
                    self.cargar_productos()
                    QMessageBox.information(self, "Éxito", "Producto eliminado correctamente")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error al eliminar producto: {str(e)}")
                finally:
                    conexion.close()