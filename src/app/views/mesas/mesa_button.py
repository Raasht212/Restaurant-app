import os
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap, QGuiApplication
from ...config import resource_path

class MesaButton(QPushButton):
    def __init__(self, mesa_tuple, parent=None):
        super().__init__(parent)
        # admite ambas formas de tupla
        self.mesa_id = mesa_tuple[0]
        self.numero = mesa_tuple[1]
        self.estado = mesa_tuple[2]
        self.seccion_id = mesa_tuple[3] if len(mesa_tuple) > 3 else None
        self.seccion_nombre = mesa_tuple[4] if len(mesa_tuple) > 4 else None
        self.setFixedSize(120, 100)  # ancho x alto en píxeles


        self.setObjectName("mesaButton")  # coincide con el QSS
        self._setup_icon_and_style(QSize(48, 48))
        self._setup_text_and_accessibility()

    def _setup_icon_and_style(self, icon_size: QSize):
        icon_map = {
            "ocupada": resource_path("src","app","resources","icons", "ocupada.png"),
            "reservada": resource_path("src","app","resources","icons", "reservada.png"),
            "libre": resource_path("src","app","resources","icons", "libre.png")
        }
        icon_path = icon_map.get(self.estado, icon_map["libre"])
        icon_applied = False

        if os.path.exists(str(icon_path)):
            pix = QPixmap(str(icon_path))
            if not pix.isNull():
                screen = QGuiApplication.primaryScreen()
                dpr = screen.devicePixelRatio() if screen is not None else 1.0
                target = QSize(int(icon_size.width() * dpr), int(icon_size.height() * dpr))
                scaled = pix.scaled(target, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                displayed = scaled.scaled(icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.setIcon(QIcon(displayed))
                self.setIconSize(displayed.size())
                icon_applied = True

        base_style = """
            QPushButton#mesaButton {
                font-weight: bold;
                font-size: 12pt;
                padding: 6px;
                border-radius: 10px;
                border: 2px solid #800020;
                text-align: center;
                color: #333333;
                background-color: rgba(255, 255, 255, 0.95);
            }
            QPushButton#mesaButton:hover {
                background-color: rgba(255, 255, 255, 0.98);
                border: 2px solid #900028;
            }
        """

        estado_style = ""
        if not icon_applied:
            if self.estado == "ocupada":
                estado_style = "QPushButton#mesaButton { background-color: #ffdddd; }"
            elif self.estado == "reservada":
                estado_style = "QPushButton#mesaButton { background-color: #fff7dd; }"
            else:
                estado_style = "QPushButton#mesaButton { background-color: #ddffdd; }"

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