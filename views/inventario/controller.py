from typing import List, Optional, Tuple
from database import crear_conexion
import sqlite3

def obtener_productos() -> List[Tuple[int, str, float, int]]:
    """
    Devuelve lista de productos: (id, nombre, precio, stock)
    """
    conexion = crear_conexion()
    if not conexion:
        return []
    try:
        cur = conexion.cursor()
        cur.execute("SELECT id, nombre, precio, stock FROM productos ORDER BY nombre")
        return cur.fetchall()
    finally:
        conexion.close()

def crear_producto(nombre: str, precio: float, stock: int) -> Tuple[bool, Optional[str]]:
    conexion = crear_conexion()
    if not conexion:
        return False, "No se pudo conectar a la base de datos"
    try:
        cur = conexion.cursor()
        cur.execute("INSERT INTO productos (nombre, precio, stock) VALUES (?, ?, ?)", (nombre, float(precio), int(stock)))
        conexion.commit()
        return True, None
    except sqlite3.IntegrityError as e:
        conexion.rollback()
        return False, str(e)
    except Exception as e:
        conexion.rollback()
        return False, str(e)
    finally:
        conexion.close()

def actualizar_producto(producto_id: int, nombre: str, precio: float, stock: int) -> Tuple[bool, Optional[str]]:
    conexion = crear_conexion()
    if not conexion:
        return False, "No se pudo conectar a la base de datos"
    try:
        cur = conexion.cursor()
        cur.execute("UPDATE productos SET nombre = ?, precio = ?, stock = ? WHERE id = ?", (nombre, float(precio), int(stock), producto_id))
        conexion.commit()
        return True, None
    except sqlite3.IntegrityError as e:
        conexion.rollback()
        return False, str(e)
    except Exception as e:
        conexion.rollback()
        return False, str(e)
    finally:
        conexion.close()

def eliminar_producto(producto_id: int) -> Tuple[bool, Optional[str]]:
    conexion = crear_conexion()
    if not conexion:
        return False, "No se pudo conectar a la base de datos"
    try:
        cur = conexion.cursor()
        # Verificación defensiva: evitar eliminar producto referenciado en ordenes
        try:
            cur.execute("SELECT COUNT(*) FROM orden_detalles WHERE producto_id = ?", (producto_id,))
            if cur.fetchone()[0] > 0:
                return False, "El producto está referenciado en órdenes y no puede eliminarse"
        except Exception:
            pass
        cur.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
        conexion.commit()
        return True, None
    except Exception as e:
        conexion.rollback()
        return False, str(e)
    finally:
        conexion.close()