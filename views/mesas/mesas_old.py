import sqlite3
import os
from PySide6.QtWidgets import (
    QWidget, QGridLayout, QPushButton, QScrollArea, 
    QVBoxLayout, QLabel, QMessageBox, QInputDialog,
    QGroupBox, QComboBox, QHBoxLayout, QDialog,
    QFormLayout, QLineEdit
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QFont, QPixmap, QColor, QPainter
from database import crear_conexion
from views.orden.orden import OrdenDialog

class MesaButton(QPushButton):
    def __init__(self, mesa_data, parent=None):
        super().__init__(parent)
        self.mesa_data = mesa_data
        self.setObjectName("mesaButton")
        self.setup_ui()
        
    def setup_ui(self):
        self.setMinimumSize(250, 250)
        self.setIconSize(QSize(50, 50))
        
        estado = self.mesa_data[3]  # índice 3 es estado
        
        # Determinar qué icono usar según el estado
        if estado == "ocupada":
            icon_path = "resources/icons/ocupada.png"
        else:
            icon_path = "resources/icons/libre.png"
        
        # Cargar icono con fondo transparente
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            
            # Crear una copia para no modificar el original
            transparent_pixmap = QPixmap(pixmap.size())
            transparent_pixmap.fill(Qt.transparent)
            
            # Pintar solo los píxeles no blancos
            painter = QPainter(transparent_pixmap)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()
            
            # Escalar manteniendo relación de aspecto
            transparent_pixmap = transparent_pixmap.scaled(
                120, 120, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.setIcon(QIcon(transparent_pixmap))
        else:
            # Si no existe el archivo, usar texto y color
            if estado == "ocupada":
                self.setStyleSheet("background-color: #ffcccc;")
            else:
                self.setStyleSheet("background-color: #ccffcc;")
        
        # Texto adicional
        texto = f"Mesa {self.mesa_data[1]}"
        
            
        self.setText(texto)
        self.setStyleSheet("""
            QPushButton#mesaButton {
                font-weight: bold;
                font-size: 14pt;
                padding: 15px;
                border-radius: 15px;
                border: 2px solid #800020;
                text-align: center;
                background-color: rgba(255, 255, 255, 0.7);
                color: #333333; /* Texto negro */
            }
            QPushButton#mesaButton:hover {
                background-color: rgba(255, 255, 255, 0.9);
                border: 2px solid #900028;
            }
        """)

class MesasView(QWidget):
    mesa_seleccionada = Signal(int)
    estado_mesa_cambiado = Signal()
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 10, 20, 20)
        layout.setSpacing(15)
        
        # Título
        titulo = QLabel("CONTROL DE MESAS")
        titulo.setObjectName("titulo")
        titulo.setFont(QFont("Segoe UI", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Filtro de secciones
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filtrar por sección:"))
        
        self.combo_secciones = QComboBox()
        self.combo_secciones.setMinimumHeight(35)
        self.combo_secciones.currentIndexChanged.connect(self.filtrar_mesas)
        filter_layout.addWidget(self.combo_secciones)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Área de scroll para mesas
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.NoFrame)
        
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_layout.setSpacing(20)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)
        
        self.scroll.setWidget(self.scroll_content)
        layout.addWidget(self.scroll)
        
        # Botones de control
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.setSpacing(30)
        
        btn_agregar = QPushButton("Agregar Mesa")
        btn_agregar.setIcon(QIcon("resources/icons/add.png"))
        btn_agregar.setMinimumHeight(50)
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
        btn_agregar.clicked.connect(self.agregar_mesa)
        
        btn_eliminar = QPushButton("Eliminar Mesa")
        btn_eliminar.setIcon(QIcon("resources/icons/delete.png"))
        btn_eliminar.setMinimumHeight(50)
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
        btn_eliminar.clicked.connect(self.eliminar_mesa)
        
        btn_layout.addWidget(btn_agregar)
        btn_layout.addWidget(btn_eliminar)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        self.cargar_secciones()
        self.actualizar_mesas()
    
    def cargar_secciones(self):
        conexion = crear_conexion()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute("SELECT DISTINCT seccion FROM mesas ORDER BY seccion")
                secciones = cursor.fetchall()
                
                self.combo_secciones.clear()
                self.combo_secciones.addItem("Todas las secciones", None)
                
                for seccion in secciones:
                    self.combo_secciones.addItem(seccion[0], seccion[0])
                    
            except Exception as e:
                print(f"Error cargando secciones: {e}")
            finally:
                conexion.close()
    
    def filtrar_mesas(self):
        self.actualizar_mesas()
    
    def actualizar_mesas(self):
        # Limpiar layout existente
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            
        # Obtener sección seleccionada
        seccion = self.combo_secciones.currentData()
        
        # Obtener mesas de la base de datos
        conexion = crear_conexion()
        if conexion:
            try:
                cursor = conexion.cursor()
                
                if seccion:
                    cursor.execute("""
                        SELECT id, numero, seccion, estado 
                        FROM mesas 
                        WHERE seccion = ?
                        ORDER BY numero
                    """, (seccion,))
                else:
                    cursor.execute("SELECT id, numero, seccion, estado FROM mesas ORDER BY seccion, numero")
                
                mesas = cursor.fetchall()
                
                # Agrupar mesas por sección
                mesas_por_seccion = {}
                for mesa in mesas:
                    seccion = mesa[2]
                    if seccion not in mesas_por_seccion:
                        mesas_por_seccion[seccion] = []
                    mesas_por_seccion[seccion].append(mesa)
                
                # Crear grupos para cada sección
                for seccion, mesas_seccion in mesas_por_seccion.items():
                    group_box = QGroupBox(seccion)
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
                    
                    grid_layout = QGridLayout()
                    grid_layout.setAlignment(Qt.AlignCenter)
                    grid_layout.setSpacing(20)
                    
                    # Agregar mesas a la grilla
                    row, col = 0, 0
                    max_cols = 4
                    
                    for mesa in mesas_seccion:
                        btn_mesa = MesaButton(mesa)
                        btn_mesa.clicked.connect(lambda checked, m=mesa: self.abrir_orden(m))
                        grid_layout.addWidget(btn_mesa, row, col)
                        
                        col += 1
                        if col >= max_cols:
                            col = 0
                            row += 1
                    
                    group_box.setLayout(grid_layout)
                    self.scroll_layout.addWidget(group_box)
                        
            except Exception as e:
                print(f"Error cargando mesas: {e}")
            finally:
                conexion.close()
    
    def abrir_orden(self, mesa):
        # Actualizar datos de la mesa antes de abrir el diálogo
        conexion = crear_conexion()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute("SELECT id, numero, seccion, estado FROM mesas WHERE id = ?", (mesa[0],))
                mesa_actualizada = cursor.fetchone()
                if mesa_actualizada:
                    mesa = mesa_actualizada
            except Exception as e:
                print(f"Error actualizando mesa: {e}")
            finally:
                conexion.close()
        
        dialog = OrdenDialog(mesa)
        dialog.estado_mesa_cambiado.connect(self.actualizar_mesas)
        dialog.exec()
    
    def agregar_mesa(self):
        # Diálogo para agregar nueva mesa
        dialog = QDialog(self)
        dialog.setWindowTitle("Agregar Nueva Mesa")
        dialog.setFixedSize(400, 200)
        
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        # Número de mesa
        self.input_numero = QLineEdit()
        self.input_numero.setPlaceholderText("Ingrese número de mesa")
        self.input_numero.setMinimumHeight(40)
        form_layout.addRow("Número de mesa:", self.input_numero)
        
        # Sección
        self.input_seccion = QLineEdit()
        self.input_seccion.setPlaceholderText("Ej: Terraza, Principal, VIP")
        self.input_seccion.setMinimumHeight(40)
        form_layout.addRow("Sección:", self.input_seccion)
        
        layout.addLayout(form_layout)
        
        # Botones
        btn_layout = QHBoxLayout()
        
        btn_guardar = QPushButton("Guardar")
        btn_guardar.setMinimumHeight(45)
        btn_guardar.setStyleSheet("""
            background-color: #27ae60;
            color: #333333;
            font-weight: bold;
        """)
        btn_guardar.clicked.connect(lambda: self.guardar_mesa(dialog))
        
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setMinimumHeight(45)
        btn_cancelar.setStyleSheet("""
            background-color: #e74c3c;
            color: #333333;
            font-weight: bold;
        """)
        btn_cancelar.clicked.connect(dialog.reject)
        
        btn_layout.addWidget(btn_cancelar)
        btn_layout.addWidget(btn_guardar)
        layout.addLayout(btn_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def guardar_mesa(self, dialog):
        numero = self.input_numero.text().strip()
        seccion = self.input_seccion.text().strip() or "Principal"
        
        if not numero:
            QMessageBox.warning(self, "Error", "El número de mesa es obligatorio")
            return
            
        try:
            numero = int(numero)
        except ValueError:
            QMessageBox.warning(self, "Error", "El número de mesa debe ser un valor numérico")
            return
            
        conexion = crear_conexion()
        if conexion:
            try:
                cursor = conexion.cursor()
                
                # Verificar si la mesa ya existe
                cursor.execute("SELECT COUNT(*) FROM mesas WHERE numero = ?", (numero,))
                if cursor.fetchone()[0] > 0:
                    QMessageBox.warning(self, "Error", f"Ya existe una mesa con el número {numero}")
                    return
                
                # Insertar nueva mesa
                cursor.execute(
                    "INSERT INTO mesas (numero, seccion) VALUES (?, ?)",
                    (numero, seccion)
                )
                conexion.commit()
                
                # Actualizar vistas
                self.cargar_secciones()
                self.actualizar_mesas()
                
                QMessageBox.information(self, "Éxito", f"Mesa {numero} agregada correctamente")
                dialog.accept()
                
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Error", f"Ya existe una mesa con el número {numero}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al agregar mesa: {str(e)}")
            finally:
                conexion.close()
    
    def eliminar_mesa(self):
        # Obtener todas las mesas
        conexion = crear_conexion()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute("SELECT id, numero, seccion, estado FROM mesas ORDER BY seccion, numero")
                mesas = cursor.fetchall()
                
                if not mesas:
                    QMessageBox.information(self, "Información", "No hay mesas para eliminar")
                    return
                
                # Crear lista de números de mesa
                numeros_mesas = [str(mesa[1]) for mesa in mesas]
                
                # Mostrar diálogo para seleccionar mesa a eliminar
                numero, ok = QInputDialog.getItem(
                    self,
                    "Eliminar Mesa",
                    "Seleccione la mesa a eliminar:",
                    numeros_mesas,
                    0,  # Índice por defecto
                    False  # No editable
                )
                
                if ok and numero:
                    # Encontrar la mesa seleccionada
                    mesa_a_eliminar = None
                    for mesa in mesas:
                        if str(mesa[1]) == numero:
                            mesa_a_eliminar = mesa
                            break
                    
                    if mesa_a_eliminar:
                        # Verificar si la mesa está ocupada
                        if mesa_a_eliminar[3] == "ocupada":  # índice 3 es estado
                            QMessageBox.warning(self, "Error", "No se puede eliminar una mesa ocupada")
                            return
                            
                        # Confirmar eliminación
                        respuesta = QMessageBox.question(
                            self,
                            "Confirmar eliminación",
                            f"¿Está seguro de eliminar la Mesa {mesa_a_eliminar[1]}?",
                            QMessageBox.Yes | QMessageBox.No
                        )
                        
                        if respuesta == QMessageBox.Yes:
                            cursor.execute("DELETE FROM mesas WHERE id = ?", (mesa_a_eliminar[0],))
                            conexion.commit()
                            self.cargar_secciones()
                            self.actualizar_mesas()
                            QMessageBox.information(self, "Éxito", f"Mesa {mesa_a_eliminar[1]} eliminada correctamente")
            
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar mesa: {str(e)}")
            finally:
                conexion.close()