from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QSpinBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from database import crear_conexion, sqlite3
import datetime
import random

class OrdenDialog(QDialog):
    estado_mesa_cambiado = Signal()
    
    def __init__(self, mesa):
        super().__init__()
        self.mesa = mesa
        self.productos_seleccionados = []
        self.orden_id = None
        self.detalles_originales = {}  # Para almacenar cantidades originales
        self.setWindowTitle(f"Orden - Mesa {mesa[1]}")
        self.setMinimumSize(800, 600)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Información de la mesa
        mesa_layout = QHBoxLayout()
        self.label_mesa = QLabel(f"Mesa: {self.mesa[1]}")
        mesa_layout.addWidget(self.label_mesa)
        
        self.label_estado = QLabel(f"Estado: {'Ocupada' if self.mesa[3] == 'ocupada' else 'Libre'}")
        mesa_layout.addWidget(self.label_estado)
        mesa_layout.addStretch()
        
        # Nombre del cliente
        cliente_layout = QVBoxLayout()
        cliente_layout.addWidget(QLabel("Nombre del Cliente:"))
        self.input_cliente = QLineEdit()
        self.input_cliente.setPlaceholderText("Ingrese nombre del cliente")
        self.input_cliente.setMinimumHeight(40)
        cliente_layout.addWidget(self.input_cliente)
        
        # Productos disponibles
        productos_layout = QVBoxLayout()
        productos_layout.addWidget(QLabel("Productos Disponibles:"))
        
        # Selección de productos
        producto_selector_layout = QHBoxLayout()
        
        self.combo_productos = QComboBox()
        self.combo_productos.setMinimumHeight(40)
        self.cargar_productos()
        
        self.spin_cantidad = QSpinBox()
        self.spin_cantidad.setMinimum(1)
        self.spin_cantidad.setMaximum(100)
        self.spin_cantidad.setValue(1)
        self.spin_cantidad.setMinimumHeight(40)
        
        btn_agregar = QPushButton("Agregar")
        btn_agregar.setMinimumHeight(40)
        btn_agregar.clicked.connect(self.agregar_producto)
        
        producto_selector_layout.addWidget(self.combo_productos, 4)
        producto_selector_layout.addWidget(self.spin_cantidad, 1)
        producto_selector_layout.addWidget(btn_agregar, 1)
        
        productos_layout.addLayout(producto_selector_layout)
        
        # Tabla de productos seleccionados
        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(5)
        self.tabla_productos.setHorizontalHeaderLabels(["Producto", "Precio", "Cantidad", "Subtotal", ""])
        self.tabla_productos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Total
        total_layout = QHBoxLayout()
        total_layout.addWidget(QLabel("Total:"))
        self.label_total = QLabel("0.00")
        self.label_total.setFont(QFont("Arial", 14, QFont.Bold))
        self.label_total.setStyleSheet("color: #e74c3c;")
        total_layout.addWidget(self.label_total)
        total_layout.addStretch()
        
        # Botones
        btn_layout = QHBoxLayout()
        self.btn_confirmar = QPushButton("Confirmar Orden")
        self.btn_confirmar.setMinimumHeight(45)
        self.btn_confirmar.setStyleSheet("background-color: #27ae60; color: #333333; font-weight: bold;")
        self.btn_confirmar.clicked.connect(self.confirmar_orden)
        
        self.btn_factura = QPushButton("Generar Factura")
        self.btn_factura.setMinimumHeight(45)
        self.btn_factura.setStyleSheet("background-color: #9b59b6; color: #333333; font-weight: bold;")
        self.btn_factura.clicked.connect(self.generar_factura)
        self.btn_factura.setVisible(False)
        
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setMinimumHeight(45)
        btn_cancelar.setStyleSheet("background-color: #e74c3c; color: #333333; font-weight: bold;")
        btn_cancelar.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_cancelar)
        btn_layout.addWidget(self.btn_confirmar)
        btn_layout.addWidget(self.btn_factura)
        
        # Agregar elementos al layout principal
        layout.addLayout(mesa_layout)
        layout.addLayout(cliente_layout)
        layout.addLayout(productos_layout)
        layout.addWidget(self.tabla_productos)
        layout.addLayout(total_layout)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
        # Cargar orden existente si la mesa está ocupada
        if self.mesa[3] == "ocupada":
            self.cargar_orden_existente()
            self.input_cliente.setEnabled(False)
        else:
            # Asegurarse de limpiar cualquier dato previo
            self.productos_seleccionados = []
            self.orden_id = None
            self.detalles_originales = {}
            self.actualizar_tabla_productos()
    
    def cargar_productos(self):
        self.combo_productos.clear()
        conexion = crear_conexion()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute("SELECT id, nombre, precio FROM productos WHERE stock > 0")
                productos = cursor.fetchall()
                
                for producto in productos:
                    self.combo_productos.addItem(f"{producto[1]} - ${producto[2]:.2f}", producto[0])
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error cargando productos: {e}")
            finally:
                conexion.close()
    
    def agregar_producto(self):
        indice = self.combo_productos.currentIndex()
        if indice < 0:
            QMessageBox.warning(self, "Error", "Seleccione un producto")
            return
            
        producto_id = self.combo_productos.itemData(indice)
        nombre = self.combo_productos.currentText().split(' - ')[0]
        precio = float(self.combo_productos.currentText().split(' - $')[1])
        cantidad = self.spin_cantidad.value()
        
        stock_disponible = self.consultar_stock(producto_id)
        if stock_disponible is None:
            return
            
        # Calcular cantidad total en la orden (incluyendo ya existente)
        cantidad_total = cantidad
        if producto_id in self.detalles_originales:
            cantidad_total += self.detalles_originales[producto_id]['cantidad_actual']
        
        # Verificar stock disponible
        if cantidad_total > stock_disponible:
            QMessageBox.warning(
                self, 
                "Stock insuficiente",
                f"No hay suficiente stock de {nombre}\nStock disponible: {stock_disponible}"
            )
            return
        
        # Actualizar o agregar producto
        subtotal = precio * cantidad
        producto_existente = next(
            (p for p in self.productos_seleccionados if p['id'] == producto_id), 
            None
        )
        
        if producto_existente:
            producto_existente['cantidad'] += cantidad
            producto_existente['subtotal'] = producto_existente['cantidad'] * precio
        else:
            self.productos_seleccionados.append({
                'id': producto_id,
                'nombre': nombre,
                'precio': precio,
                'cantidad': cantidad,
                'subtotal': subtotal
            })
        
        self.actualizar_tabla_productos()
    
    def consultar_stock(self, producto_id):
        conexion = crear_conexion()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute("SELECT stock FROM productos WHERE id = ?", (producto_id,))
                resultado = cursor.fetchone()
                return resultado[0] if resultado else 0
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error consultando stock: {str(e)}")
            finally:
                conexion.close()
        return None
    
    def actualizar_tabla_productos(self):
        self.tabla_productos.setRowCount(len(self.productos_seleccionados))
        total = 0
        
        for fila, producto in enumerate(self.productos_seleccionados):
            self.tabla_productos.setItem(fila, 0, QTableWidgetItem(producto['nombre']))
            self.tabla_productos.setItem(fila, 1, QTableWidgetItem(f"${producto['precio']:.2f}"))
            self.tabla_productos.setItem(fila, 2, QTableWidgetItem(str(producto['cantidad'])))
            self.tabla_productos.setItem(fila, 3, QTableWidgetItem(f"${producto['subtotal']:.2f}"))
            
            btn_eliminar = QPushButton("Eliminar")
            btn_eliminar.setStyleSheet("background-color: #e74c3c; color: white;")
            btn_eliminar.clicked.connect(lambda _, f=fila: self.eliminar_producto(f))
            self.tabla_productos.setCellWidget(fila, 4, btn_eliminar)
            
            total += producto['subtotal']
        
        self.label_total.setText(f"${total:.2f}")
    
    def eliminar_producto(self, fila):
        if 0 <= fila < len(self.productos_seleccionados):
            self.productos_seleccionados.pop(fila)
            self.actualizar_tabla_productos()
    
    def cargar_orden_existente(self):
        conexion = crear_conexion()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute("""
                    SELECT id, cliente_nombre 
                    FROM ordenes 
                    WHERE mesa_id = ? AND estado = 'abierta'
                """, (self.mesa[0],))
                orden = cursor.fetchone()
                
                if orden:
                    self.orden_id = orden[0]
                    self.input_cliente.setText(orden[1])
                    
                    # Obtener productos de la orden
                    cursor.execute("""
                        SELECT p.id, p.nombre, p.precio, d.cantidad, d.subtotal
                        FROM orden_detalles d
                        JOIN productos p ON d.producto_id = p.id
                        WHERE d.orden_id = ?
                    """, (self.orden_id,))
                    
                    self.detalles_originales = {}
                    self.productos_seleccionados = []
                    
                    for producto in cursor.fetchall():
                        producto_id = producto[0]
                        self.detalles_originales[producto_id] = {
                            'cantidad_original': producto[3],
                            'cantidad_actual': producto[3]
                        }
                        self.productos_seleccionados.append({
                            'id': producto_id,
                            'nombre': producto[1],
                            'precio': producto[2],
                            'cantidad': producto[3],
                            'subtotal': producto[4]
                        })
                    
                    self.actualizar_tabla_productos()
                    self.btn_factura.setVisible(True)
                else:
                    # No existe orden abierta, limpiar datos
                    self.orden_id = None
                    self.productos_seleccionados = []
                    self.detalles_originales = {}
                    self.actualizar_tabla_productos()
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error cargando orden existente: {e}")
            finally:
                conexion.close()
    
    def confirmar_orden(self):
        cliente = self.input_cliente.text().strip()
        if not cliente:
            QMessageBox.warning(self, "Error", "Debe ingresar el nombre del cliente")
            return
            
        if not self.productos_seleccionados:
            QMessageBox.warning(self, "Error", "Debe agregar al menos un producto a la orden")
            return
            
        conexion = crear_conexion()
        if conexion:
            try:
                cursor = conexion.cursor()
                
                # Verificar si ya existe una orden para esta mesa
                cursor.execute("SELECT id FROM ordenes WHERE mesa_id = ? AND estado = 'abierta'", (self.mesa[0],))
                orden_existente = cursor.fetchone()
                
                if orden_existente:
                    # Actualizar orden existente
                    self.orden_id = orden_existente[0]
                    cursor.execute("""
                        UPDATE ordenes 
                        SET cliente_nombre = ?, total = ?
                        WHERE id = ?
                    """, (cliente, float(self.label_total.text().replace('$', '')), self.orden_id))
                else:
                    # Crear nueva orden
                    cursor.execute("""
                        INSERT INTO ordenes (mesa_id, cliente_nombre, estado, total) 
                        VALUES (?, ?, ?, ?)
                    """, (self.mesa[0], cliente, 'abierta', float(self.label_total.text().replace('$', ''))))
                    self.orden_id = cursor.lastrowid
                
                # Actualizar estado de la mesa
                cursor.execute("""
                    UPDATE mesas SET estado = 'ocupada' WHERE id = ?
                """, (self.mesa[0],))
                
                # Manejar cambios en el inventario
                cambios_stock = {}
                
                # Calcular cambios para productos nuevos
                for producto in self.productos_seleccionados:
                    producto_id = producto['id']
                    cantidad_actual = producto['cantidad']
                    
                    # Calcular diferencia con la cantidad original
                    if producto_id in self.detalles_originales:
                        cantidad_original = self.detalles_originales[producto_id]['cantidad_original']
                        diferencia = cantidad_actual - cantidad_original
                    else:
                        cantidad_original = 0
                        diferencia = cantidad_actual
                    
                    cambios_stock[producto_id] = diferencia
                
                # Calcular cambios para productos eliminados
                for producto_id, detalle in self.detalles_originales.items():
                    if producto_id not in cambios_stock:
                        cambios_stock[producto_id] = -detalle['cantidad_original']
                
                # Verificar stock disponible para cambios
                for producto_id, diferencia in cambios_stock.items():
                    if diferencia > 0:  # Solo verificar si estamos agregando
                        cursor.execute("SELECT stock, nombre FROM productos WHERE id = ?", (producto_id,))
                        stock_actual, nombre = cursor.fetchone()
                        
                        if stock_actual < diferencia:
                            QMessageBox.warning(
                                self, 
                                "Stock insuficiente",
                                f"No hay suficiente stock de {nombre}\nStock disponible: {stock_actual}"
                            )
                            conexion.rollback()
                            return
                
                # Aplicar cambios al inventario
                for producto_id, diferencia in cambios_stock.items():
                    if diferencia != 0:
                        cursor.execute("""
                            UPDATE productos 
                            SET stock = stock - ? 
                            WHERE id = ?
                        """, (diferencia, producto_id))
                
                # Eliminar detalles antiguos e insertar nuevos
                cursor.execute("DELETE FROM orden_detalles WHERE orden_id = ?", (self.orden_id,))
                
                for producto in self.productos_seleccionados:
                    cursor.execute("""
                        INSERT INTO orden_detalles (orden_id, producto_id, cantidad, subtotal)
                        VALUES (?, ?, ?, ?)
                    """, (self.orden_id, producto['id'], producto['cantidad'], producto['subtotal']))
                
                conexion.commit()
                QMessageBox.information(self, "Éxito", "Orden registrada correctamente")
                
                # Actualizar detalles originales para futuras ediciones
                for producto in self.productos_seleccionados:
                    producto_id = producto['id']
                    self.detalles_originales[producto_id] = {
                        'cantidad_original': producto['cantidad'],
                        'cantidad_actual': producto['cantidad']
                    }
                
                self.input_cliente.setEnabled(False)
                self.btn_factura.setVisible(True)
                self.estado_mesa_cambiado.emit()
                
            except sqlite3.IntegrityError:
                QMessageBox.critical(self, "Error", "Ya existe una orden abierta para esta mesa")
            except Exception as e:
                conexion.rollback()
                QMessageBox.critical(self, "Error", f"Error al guardar la orden: {str(e)}")
            finally:
                conexion.close()
    
    def generar_factura(self):
        total = sum(p['subtotal'] for p in self.productos_seleccionados)
        numero_factura = f"FACT-{datetime.datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        
        conexion = crear_conexion()
        if conexion:
            try:
                cursor = conexion.cursor()
                
                # Crear factura
                cursor.execute("""
                    INSERT INTO facturas (orden_id, numero_factura, cliente_nombre, total) 
                    VALUES (?, ?, ?, ?)
                """, (self.orden_id, numero_factura, self.input_cliente.text(), total))
                
                # Actualizar estado de la orden
                cursor.execute("""
                    UPDATE ordenes SET estado = 'facturada' 
                    WHERE id = ?
                """, (self.orden_id,))
                
                # Liberar mesa
                cursor.execute("""
                    UPDATE mesas SET estado = 'libre' 
                    WHERE id = ?
                """, (self.mesa[0],))
                
                conexion.commit()
                self.mostrar_resumen_factura(numero_factura, total)
                self.estado_mesa_cambiado.emit()
                
                # Limpiar datos para futuras órdenes
                self.productos_seleccionados = []
                self.orden_id = None
                self.detalles_originales = {}
                self.actualizar_tabla_productos()
                self.input_cliente.clear()
                self.input_cliente.setEnabled(True)
                self.btn_factura.setVisible(False)
                
            except Exception as e:
                conexion.rollback()
                QMessageBox.critical(self, "Error", f"Error al generar factura: {str(e)}")
            finally:
                conexion.close()
    
    def mostrar_resumen_factura(self, numero_factura, total):
        mensaje = f"<b>FACTURA GENERADA</b><br><br>"
        mensaje += f"<b>Número:</b> {numero_factura}<br>"
        mensaje += f"<b>Fecha:</b> {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}<br>"
        mensaje += f"<b>Mesa:</b> {self.mesa[1]}<br>"
        mensaje += f"<b>Cliente:</b> {self.input_cliente.text()}<br><br>"
        
        mensaje += "<b>Detalle de productos:</b><br>"
        mensaje += "<table border='1' style='border-collapse: collapse; width: 100%;'>"
        mensaje += "<tr><th>Producto</th><th>Precio</th><th>Cantidad</th><th>Subtotal</th></tr>"
        
        for producto in self.productos_seleccionados:
            mensaje += f"<tr><td>{producto['nombre']}</td>"
            mensaje += f"<td>${producto['precio']:.2f}</td>"
            mensaje += f"<td>{producto['cantidad']}</td>"
            mensaje += f"<td>${producto['subtotal']:.2f}</td></tr>"
        
        mensaje += f"<tr><td colspan='3' align='right'><b>Total:</b></td>"
        mensaje += f"<td><b>${total:.2f}</b></td></tr>"
        mensaje += "</table>"
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Factura Generada")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(mensaje)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()