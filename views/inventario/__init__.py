from .inventario import InventarioView, EditarProductoDialog
from .controller import (
    obtener_productos,
    crear_producto,
    actualizar_producto,
    eliminar_producto
)

__all__ = ["InventarioView", "EditarProductoDialog", "obtener_productos", "crear_producto", "actualizar_producto", "eliminar_producto"]