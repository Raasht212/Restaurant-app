# views/orden/__init__.py
from .orden import OrdenDialog
from .controller import (
    obtener_productos_disponibles,
    consultar_stock,
    obtener_orden_abierta_por_mesa,
    obtener_detalles_orden,
    crear_o_actualizar_orden,
    aplicar_cambios_stock,
    insertar_factura
)

__all__ = [
    "OrdenDialog",
    "obtener_productos_disponibles",
    "consultar_stock",
    "obtener_orden_abierta_por_mesa",
    "obtener_detalles_orden",
    "crear_o_actualizar_orden",
    "aplicar_cambios_stock",
    "insertar_factura",
]