# src/app/services/orden_service.py
from typing import List, Tuple, Optional, Dict
import sqlite3
import datetime

from ..db.connection import ConnectionManager

def obtener_productos_disponibles() -> List[Tuple[int, str, float, int]]:
    """
    Devuelve lista de productos: (id, nombre, precio, stock)
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, precio, stock FROM productos ORDER BY nombre")
        return cur.fetchall()

def consultar_stock(producto_id: int) -> Optional[int]:
    """
    Devuelve el stock actual del producto o None si no existe.
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("SELECT stock FROM productos WHERE id = ?", (producto_id,))
        row = cur.fetchone()
        return int(row[0]) if row else None

def obtener_orden_abierta_por_mesa(mesa_id: int) -> Optional[Tuple[int, Optional[str], Optional[float]]]:
    """
    Retorna (orden_id, cliente, total) de la orden abierta para la mesa, o None.
    Se asume que la tabla 'ordenes' tiene un campo 'estado' que indica 'abierta'/'cerrada'.
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, cliente_nombre, total FROM ordenes WHERE mesa_id = ? AND estado = 'abierta' LIMIT 1",
            (mesa_id,)
        )
        return cur.fetchone()

def obtener_detalles_orden(orden_id: int) -> List[Tuple[int, str, float, int, float]]:
    """
    Devuelve lista de detalles: (producto_id, nombre, precio, cantidad, subtotal)
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT d.producto_id, p.nombre, p.precio, d.cantidad, d.subtotal
               FROM orden_detalles d
               JOIN productos p ON p.id = d.producto_id
               WHERE d.orden_id = ?""",
            (orden_id,)
        )
        return cur.fetchall()

def crear_o_actualizar_orden(mesa_id: int, cliente_nombre: str, productos: List[Dict], orden_id: Optional[int] = None) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Crea una nueva orden (y sus detalles) o actualiza una existente.
    productos: [{'id': int, 'cantidad': int, 'subtotal': float}, ...]
    Devuelve (ok, orden_id, err)
    """
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            ahora = datetime.datetime.now().isoformat(sep=' ', timespec='seconds')
            total = sum(float(p.get('subtotal', 0.0)) for p in productos)

            if orden_id:
                # actualizar cabecera
                cur.execute(
                    "UPDATE ordenes SET cliente = ?, total = ?, actualizado_en = ? WHERE id = ?",
                    (cliente_nombre, float(total), ahora, orden_id)
                )
                # eliminar detalles previos y reinsertar (sencillo y consistente)
                cur.execute("DELETE FROM orden_detalles WHERE orden_id = ?", (orden_id,))
                nuevo_id = orden_id
            else:
                # crear orden nueva
                cur.execute(
                    "INSERT INTO ordenes (mesa_id, cliente_nombre, total, estado, fecha) VALUES (?, ?, ?, 'abierta', ?)",
                    (mesa_id, cliente_nombre, float(total), ahora)
                )
                
                # marcar mesa como ocupada
                cur.execute("UPDATE mesas SET estado = 'ocupado' WHERE id = ?", (mesa_id,))

                nuevo_id = cur.lastrowid

            # insertar detalles
            for p in productos:
                pid = int(p['id'])
                cantidad = int(p['cantidad'])
                subtotal = float(p.get('subtotal', round(cantidad * 0.0, 2)))
                # intentar obtener precio actual si subtotal vacio
                cur.execute("SELECT precio FROM productos WHERE id = ?", (pid,))
                row = cur.fetchone()
                precio = float(row[0]) if row else 0.0
                if not p.get('subtotal'):
                    subtotal = round(precio * cantidad, 2)
                cur.execute(
                    "INSERT INTO orden_detalles (orden_id, producto_id, cantidad, precio, subtotal) VALUES (?, ?, ?, ?, ?)",
                    (nuevo_id, pid, cantidad, precio, subtotal)
                )
        return True, nuevo_id, None
    except sqlite3.IntegrityError as e:
        return False, None, str(e)
    except Exception as e:
        return False, None, str(e)

def insertar_factura(orden_id: int, numero_factura: str, cliente_nombre: str, total: float) -> Tuple[bool, Optional[str]]:
    """
    Inserta una fila en la tabla de facturas y marca la orden como cerrada.
    Devuelve (ok, err).
    """
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            ahora = datetime.datetime.now().isoformat(sep=' ', timespec='seconds')
            cur.execute(
                "INSERT INTO facturas (orden_id, numero_factura, cliente_nombre, total, fecha) VALUES (?, ?, ?, ?, ?)",
                (orden_id, numero_factura, cliente_nombre, float(total), ahora)
            )
            # marcar orden como cerrada
            cur.execute("UPDATE ordenes SET estado = 'cerrada', cerrado_en = ? WHERE id = ?", (ahora, orden_id))
            
            # liberar mesa asociada
            cur.execute("UPDATE mesas SET estado = 'libre' WHERE id = (SELECT mesa_id FROM ordenes WHERE id = ?)", (orden_id,))

        return True, None
    except sqlite3.IntegrityError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)