from typing import List, Optional, Dict, Tuple
from database import crear_conexion
import datetime
import sqlite3

def obtener_productos_disponibles() -> List[Tuple[int, str, float, int]]:
    """
    Devuelve lista de productos con stock > 0:
    [(id, nombre, precio, stock), ...]
    """
    conexion = crear_conexion()
    if not conexion:
        return []
    try:
        cur = conexion.cursor()
        cur.execute("SELECT id, nombre, precio, stock FROM productos WHERE stock > 0 ORDER BY nombre")
        return cur.fetchall()
    finally:
        conexion.close()

def consultar_stock(producto_id: int) -> Optional[int]:
    conexion = crear_conexion()
    if not conexion:
        return None
    try:
        cur = conexion.cursor()
        cur.execute("SELECT stock FROM productos WHERE id = ?", (producto_id,))
        row = cur.fetchone()
        return int(row[0]) if row else 0
    finally:
        conexion.close()

def obtener_orden_abierta_por_mesa(mesa_id: int) -> Optional[Tuple[int, Optional[str], float]]:
    """
    Retorna (orden_id, cliente_nombre, total) o None si no hay orden abierta.
    """
    conexion = crear_conexion()
    if not conexion:
        return None
    try:
        cur = conexion.cursor()
        cur.execute("SELECT id, cliente_nombre, total FROM ordenes WHERE mesa_id = ? AND estado = 'abierta' LIMIT 1", (mesa_id,))
        return cur.fetchone()
    finally:
        conexion.close()

def obtener_detalles_orden(orden_id: int) -> List[Tuple[int, str, float, int, float]]:
    """
    Retorna lista con detalles de la orden:
    [(producto_id, nombre, precio, cantidad, subtotal), ...]
    """
    conexion = crear_conexion()
    if not conexion:
        return []
    try:
        cur = conexion.cursor()
        cur.execute("""
            SELECT p.id, p.nombre, p.precio, d.cantidad, d.subtotal
            FROM orden_detalles d
            LEFT JOIN productos p ON d.producto_id = p.id
            WHERE d.orden_id = ?
        """, (orden_id,))
        return cur.fetchall()
    finally:
        conexion.close()

def crear_o_actualizar_orden(
    mesa_id: int,
    cliente: str,
    productos: List[Dict],
    orden_id: Optional[int] = None
) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Crea una nueva orden (si orden_id es None) o actualiza la existente.
    'productos' es lista de dicts: {'id', 'cantidad', 'subtotal'}
    Devuelve (exito, orden_id, mensaje_error).
    NO aplica cambios de stock; solo crea/actualiza orden y detalles.
    """
    conexion = crear_conexion()
    if not conexion:
        return False, None, "No se pudo conectar a la base de datos"
    try:
        cur = conexion.cursor()
        total = float(sum(float(p["subtotal"]) for p in productos))

        if orden_id:
            cur.execute("UPDATE ordenes SET cliente_nombre = ?, total = ? WHERE id = ?", (cliente, total, orden_id))
        else:
            ahora = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
            cur.execute("INSERT INTO ordenes (mesa_id, cliente_nombre, total, estado) VALUES (?, ?, ?, ?)",
                        (mesa_id, cliente, total, "abierta"))
            orden_id = cur.lastrowid

        # Reemplazar detalles
        cur.execute("DELETE FROM orden_detalles WHERE orden_id = ?", (orden_id,))
        for p in productos:
            cur.execute(
                "INSERT INTO orden_detalles (orden_id, producto_id, cantidad, subtotal) VALUES (?, ?, ?, ?)",
                (orden_id, p["id"], int(p["cantidad"]), float(p["subtotal"]))
            )

        # Marcar mesa ocupada
        cur.execute("UPDATE mesas SET estado = 'ocupada' WHERE id = ?", (mesa_id,))

        conexion.commit()
        return True, orden_id, None
    except sqlite3.IntegrityError as e:
        conexion.rollback()
        return False, None, str(e)
    except Exception as e:
        conexion.rollback()
        return False, None, str(e)
    finally:
        conexion.close()

def cancelar_orden(orden_id: int) -> Tuple[bool, Optional[str]]:
    """
    Marca la orden como 'cancelada' y libera la mesa asociada.
    """
    conexion = crear_conexion()
    if not conexion:
        return False, "No se pudo conectar a la base de datos"
    
    try:
        cur = conexion.cursor()
        
        # 1. Obtener el ID de la mesa asociada a la orden
        cur.execute("SELECT mesa_id FROM ordenes WHERE id = ?", (orden_id,))
        row = cur.fetchone()
        
        if not row:
            return False, f"Orden con ID {orden_id} no encontrada."
        
        mesa_id = row[0]
        
        # 2. Actualizar el estado de la orden a 'cancelada'
        # Esto es un soft delete para mantener el historial
        cur.execute("UPDATE ordenes SET estado = 'abierta' WHERE id = ?", (orden_id,))
        
        # 3. Liberar la mesa
        cur.execute("UPDATE mesas SET estado = 'libre' WHERE id = ?", (mesa_id,))
        
        # 4. Confirmar la transacción
        conexion.commit()
        return True, None
        
    except Exception as e:
        conexion.rollback() # Deshacer si algo falla
        return False, str(e)
        
    finally:
        conexion.close()

def aplicar_cambios_stock(cambios: Dict[int, int]) -> Tuple[bool, Optional[str]]:
    """
    Aplica cambios sobre stock: cambios[producto_id] = diferencia (puede ser negativo).
    Verifica primero que para todas las diferencias positivas hay stock suficiente.
    Devuelve (ok, mensaje_error).
    """
    conexion = crear_conexion()
    if not conexion:
        return False, "No se pudo conectar a la base de datos"
    try:
        cur = conexion.cursor()
        # Verificaciones
        for pid, diff in cambios.items():
            if diff > 0:
                cur.execute("SELECT stock, nombre FROM productos WHERE id = ?", (pid,))
                row = cur.fetchone()
                if not row:
                    return False, f"Producto con ID {pid} no encontrado"
                stock_actual, nombre = row
                if stock_actual < diff:
                    return False, f"No hay suficiente stock de {nombre} (disponible {stock_actual})"

        # Aplicar cambios
        for pid, diff in cambios.items():
            if diff != 0:
                cur.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", (diff, pid))
        conexion.commit()
        return True, None
    except Exception as e:
        conexion.rollback()
        return False, str(e)
    finally:
        conexion.close()

def insertar_factura(orden_id: int, numero_factura: str, cliente: str, total: float) -> Tuple[bool, Optional[str]]:
    """
    Inserta una fila en facturas, marca orden como facturada y libera mesa.
    """
    conexion = crear_conexion()
    if not conexion:
        return False, "No se pudo conectar a la base de datos"
    try:
        cur = conexion.cursor()
        ahora = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
        cur.execute(
            "INSERT INTO facturas (orden_id, numero_factura, cliente_nombre, total) VALUES (?, ?, ?, ?)",
            (orden_id, numero_factura, cliente, float(total))
        )
        cur.execute("UPDATE ordenes SET estado = 'facturada' WHERE id = ?", (orden_id,))

        # Obtener mesa_id de la orden para liberar la mesa
        cur.execute("SELECT mesa_id FROM ordenes WHERE id = ?", (orden_id,))
        row = cur.fetchone()
        if row:
            mesa_id = row[0]
            cur.execute("UPDATE mesas SET estado = 'libre' WHERE id = ?", (mesa_id,))

        conexion.commit()
        return True, None
    except Exception as e:
        conexion.rollback()
        return False, str(e)
    finally:
        conexion.close()