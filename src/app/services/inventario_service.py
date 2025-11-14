# src/app/services/inventario_service.py
from typing import List, Optional, Tuple
import sqlite3

from ..db.connection import ConnectionManager

def obtener_productos() -> List[Tuple[int, str, float, int]]:
    """
    Devuelve lista de productos: (id, nombre, precio, stock)
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, precio, stock FROM productos ORDER BY nombre")
        return cur.fetchall()

def crear_producto(nombre: str, precio: float, stock: int) -> Tuple[bool, Optional[str]]:
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO productos (nombre, precio, stock) VALUES (?, ?, ?)",
                (nombre, float(precio), int(stock))
            )
        return True, None
    except sqlite3.IntegrityError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def actualizar_producto(producto_id: int, nombre: str, precio: float, stock: int) -> Tuple[bool, Optional[str]]:
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE productos SET nombre = ?, precio = ?, stock = ? WHERE id = ?",
                (nombre, float(precio), int(stock), producto_id)
            )
        return True, None
    except sqlite3.IntegrityError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def eliminar_producto(producto_id: int) -> Tuple[bool, Optional[str]]:
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            # Verificación defensiva: evitar eliminar producto referenciado en ordenes
            try:
                cur.execute("SELECT COUNT(*) FROM orden_detalles WHERE producto_id = ?", (producto_id,))
                if cur.fetchone()[0] > 0:
                    return False, "El producto está referenciado en órdenes y no puede eliminarse"
            except Exception:
                # si la tabla no existe o falla la comprobación, continuamos con la eliminación
                pass
            cur.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
        return True, None
    except Exception as e:
        return False, str(e)