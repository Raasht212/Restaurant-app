from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import QSize

class MesaButton(QPushButton):
    def __init__(self, mesa_tuple, parent=None):
        super().__init__(parent)
        # admite ambas formas de tupla
        self.mesa_id = mesa_tuple[0]
        self.numero = mesa_tuple[1]
        self.estado = mesa_tuple[2]
        self.seccion_id = mesa_tuple[3] if len(mesa_tuple) > 3 else None
        self.seccion_nombre = mesa_tuple[4] if len(mesa_tuple) > 4 else None
        self.setFixedSize(160, 100)  # ancho x alto en píxeles


        self.setObjectName("mesaButton")  
        self._setup_style()
        self._setup_text_and_accessibility()

    def _setup_style(self):
        
        # Estilo base
        base_style = """
            QPushButton#mesaButton {
                font-weight: bold;
                font-size: 12pt;
                padding: 10px;
                border-radius: 10px;
                border: 3px solid #787878;
                text-align: center;
                color: #333333;
            }
            QPushButton#mesaButton:hover {
                border: 3px solid #FFFFFF;
            }
        """

        # Color según estado
        if self.estado == "ocupado":
            estado_style = "QPushButton#mesaButton { background-color: #990000; color: white; }"  # rojo
        elif self.estado == "reservada":
            estado_style = "QPushButton#mesaButton { background-color: #f1c40f; color: black; }"  # amarillo
        else:  # libre
            estado_style = "QPushButton#mesaButton { background-color: #007811; color: white; }"  # verde

        self.setStyleSheet(base_style + estado_style)

    def _setup_text_and_accessibility(self):
        texto = f"Mesa {self.numero}\nEstado: {self.estado}"
        self.setText(texto)
        tooltip = f"Mesa {self.numero} — Estado: {self.estado}"
        if self.seccion_nombre:
            tooltip += f" — Sección: {self.seccion_nombre}"
        self.setToolTip(tooltip)
        self.setAccessibleName(f"mesa_{self.mesa_id}")

    def actualizar_estado(self, nuevo_estado):
        self.estado = nuevo_estado
        self._setup_icon_and_style(self.iconSize())
        self._setup_text_and_accessibility()