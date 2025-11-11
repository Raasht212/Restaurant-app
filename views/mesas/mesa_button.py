import os
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QPixmap, QGuiApplication

class MesaButton(QPushButton):
    clicked_long = Signal(int)

    def __init__(self, mesa_data, parent=None,
                 size: QSize = QSize(200, 140), icon_size: QSize = QSize(64, 64)):
        """
        mesa_data expected: (id, numero, estado, seccion)
        """
        super().__init__(parent)
        self.mesa_id = mesa_data[0]
        self.numero = mesa_data[1]
        self.estado = mesa_data[2] if len(mesa_data) > 2 else "libre"
        self.seccion = mesa_data[3] if len(mesa_data) > 3 else None

        self.setObjectName("mesaButton")
        # Usa fixed size o al menos minimum + max para evitar reflow inesperado
        self.setMinimumSize(size)
        self.setMaximumSize(size)
        self.setFixedSize(size)              # fuerza tamaño estable
        self.setIconSize(icon_size)

        self._setup_icon_and_style(icon_size)
        self._setup_text_and_accessibility()

    def _setup_icon_and_style(self, icon_size):
        icon_map = {
            "ocupada": "resources/icons/ocupada.png",
            "reservada": "resources/icons/reservada.png",
            "libre": "resources/icons/libre.png"
        }
        icon_path = icon_map.get(self.estado, icon_map["libre"])
        icon_applied = False

        if os.path.exists(icon_path):
            pix = QPixmap(icon_path)
            if not pix.isNull():
                # considerar devicePixelRatio para pantallas HiDPI
                dpr = QGuiApplication.primaryScreen().devicePixelRatio() or 1.0
                target = QSize(int(icon_size.width() * dpr), int(icon_size.height() * dpr))
                scaled = pix.scaled(target, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                # Ajustar icon real al tamaño mostrado (dividir por dpr para Qt)
                displayed = scaled.scaled(icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.setIcon(QIcon(displayed))
                # Asegurar que Qt conoce el tamaño real del icono
                self.setIconSize(displayed.size())
                icon_applied = True

        # QSS reducido en padding para que no colapse el icono
        base_style = """
            QPushButton#mesaButton {
                font-weight: bold;
                font-size: 12pt;
                padding: 6px;                /* <--- reduce padding */
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
        # Forzar salto de línea para evitar que el texto ocupe espacio lateral
        self.setText(f"Mesa {self.numero}\nEstado: {self.estado}")
        self.setToolTip(f"Mesa {self.numero} — Estado: {self.estado}"
                        + (f" — Sección: {self.seccion}" if self.seccion else ""))
        self.setAccessibleName(f"mesa_{self.mesa_id}")

    def actualizar_estado(self, nuevo_estado):
        self.estado = nuevo_estado
        self._setup_icon_and_style(self.iconSize())
        self.setToolTip(f"Mesa {self.numero} — Estado: {self.estado}")
        self.setText(f"Mesa {self.numero}\nEstado: {self.estado}")