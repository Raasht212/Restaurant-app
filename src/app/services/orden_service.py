from typing import List, Tuple, Optional, Dict
import sqlite3
import datetime

from ..db.connection import ConnectionManager  # ajusta si tu import es distinto


def obtener_productos_disponibles() -> List[Tuple[int, str, float, int]]:
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, precio, stock FROM productos ORDER BY nombre")
        return cur.fetchall()


def consultar_stock(producto_id: int) -> Optional[int]:
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("SELECT stock FROM productos WHERE id = ?", (producto_id,))
        row = cur.fetchone()
        return int(row[0]) if row else None


def obtener_orden_abierta_por_mesa(mesa_id: int) -> Optional[Tuple[int, Optional[str], Optional[float]]]:
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, cliente_nombre, total FROM ordenes WHERE mesa_id = ? AND estado = 'abierta' LIMIT 1",
            (mesa_id,)
        )
        return cur.fetchone()


def obtener_detalles_orden(orden_id: int) -> List[Tuple[int, str, float, int, float]]:
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT d.producto_id, p.nombre, d.precio, d.cantidad, d.subtotal
               FROM orden_detalles d
               JOIN productos p ON p.id = d.producto_id
               WHERE d.orden_id = ?""",
            (orden_id,)
        )
        return cur.fetchall()


def _validar_y_calcular_detalles(cur, productos: List[Dict]) -> Tuple[bool, Optional[str], List[Dict], float]:
    """
    Valida que los productos existan y que haya stock suficiente (si corresponde).
    Devuelve (ok, mensaje_error, detalles_normalizados, total_calculado)
    Cada detalle normalizado: {'id': int, 'cantidad': int, 'precio': float, 'subtotal': float}
    """
    detalles = []
    total = 0.0
    for p in productos:
        try:
            pid = int(p["id"])
            cantidad = int(p["cantidad"])
        except Exception:
            return False, f"Producto con formato inválido: {p}", [], 0.0

        # obtener precio y stock actual
        cur.execute("SELECT precio, stock FROM productos WHERE id = ?", (pid,))
        row = cur.fetchone()
        if not row:
            return False, f"Producto no existe (id={pid})", [], 0.0
        precio = float(row[0])
        stock = int(row[1]) if row[1] is not None else None

        subtotal = p.get("subtotal")
        if subtotal is None or subtotal == "":
            subtotal = round(precio * cantidad, 2)
        else:
            subtotal = float(subtotal)

        # comprobar stock básico (evita reservar más de lo disponible)
        if stock is not None and cantidad > stock:
            return False, f"Stock insuficiente para producto id={pid} (solicitado={cantidad}, disponible={stock})", [], 0.0

        detalles.append({"id": pid, "cantidad": cantidad, "precio": precio, "subtotal": subtotal})
        total += subtotal

    return True, None, detalles, round(total, 2)


def crear_o_actualizar_orden(
    mesa_id: int,
    cliente_nombre: str,
    productos: List[Dict],
    orden_id: Optional[int] = None
) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Crea o actualiza una orden y sus detalles. Marca la mesa como 'ocupado' al crear.
    Devuelve (ok, orden_id, mensaje_error)
    """
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            ahora = datetime.datetime.now().isoformat(sep=' ', timespec='seconds') if hasattr(datetime, "datetime") else datetime.now().isoformat(sep=' ', timespec='seconds')

            # Validar y normalizar detalles (obtiene precios desde BD)
            ok, msg, detalles_norm, total = _validar_y_calcular_detalles(cur, productos)
            if not ok:
                return False, None, msg

            if orden_id:
                # Actualizar cabecera
                cur.execute(
                    "UPDATE ordenes SET cliente_nombre = ?, total = ?, actualizado_en = ? WHERE id = ?",
                    (cliente_nombre, float(total), ahora, orden_id)
                )
                # Eliminar detalles anteriores
                cur.execute("DELETE FROM orden_detalles WHERE orden_id = ?", (orden_id,))
                nuevo_id = orden_id
            else:
                # Crear orden nueva y obtener lastrowid inmediatamente
                cur.execute(
                    "INSERT INTO ordenes (mesa_id, cliente_nombre, total, estado, fecha) VALUES (?, ?, ?, 'abierta', ?)",
                    (mesa_id, cliente_nombre, float(total), ahora)
                )
                nuevo_id = cur.lastrowid
                # marcar mesa como ocupada
                cur.execute("UPDATE mesas SET estado = 'ocupado' WHERE id = ?", (mesa_id,))

            # Insertar detalles normalizados
            for d in detalles_norm:
                cur.execute(
                    "INSERT INTO orden_detalles (orden_id, producto_id, cantidad, precio, subtotal) VALUES (?, ?, ?, ?, ?)",
                    (nuevo_id, d["id"], d["cantidad"], d["precio"], d["subtotal"])
                )

        return True, nuevo_id, None
    except sqlite3.IntegrityError as e:
        return False, None, f"Integridad DB: {e}"
    except Exception as e:
        return False, None, str(e)
    

def cancelar_orden(orden_id: int) -> Tuple[bool, Optional[str]]:
    """
    Cancela una orden abierta, elimina sus detalles y libera la mesa asociada.
    Devuelve (ok, mensaje_error)
    """
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()

            # Obtener mesa asociada
            cur.execute("SELECT mesa_id FROM ordenes WHERE id = ? AND estado = 'abierta'", (orden_id,))
            row = cur.fetchone()
            if not row:
                return False, "Orden no existe o no está abierta"
            mesa_id = row[0]

            

            # Eliminar detalles de la orden
            cur.execute("DELETE FROM orden_detalles WHERE orden_id = ?", (orden_id,))

            # Eliminar la orden
            cur.execute("DELETE FROM ordenes WHERE id = ?", (orden_id,))

            # Liberar la mesa
            cur.execute("UPDATE mesas SET estado = 'libre' WHERE id = ?", (mesa_id,))

        return True, None
    except Exception as e:
        return False, str(e)


def insertar_factura(
    orden_id: int,
    numero_factura: str,
    cliente_nombre: str,
    total: float
) -> Tuple[bool, Optional[str]]:
    """
    Inserta una factura y marca la orden como cerrada; libera la mesa asociada.
    Devuelve (ok, mensaje_error)
    """
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            ahora = datetime.datetime.now().isoformat(sep=' ', timespec='seconds')

            # Insertar factura
            cur.execute(
                "INSERT INTO facturas (orden_id, numero_factura, cliente_nombre, total, fecha) VALUES (?, ?, ?, ?, ?)",
                (orden_id, numero_factura, cliente_nombre, float(total), ahora)
            )

            # Marcar orden como cerrada
            cur.execute(
                "UPDATE ordenes SET estado = 'cerrada', cerrado_en = ? WHERE id = ?",
                (ahora, orden_id)
            )

            # Liberar mesa asociada
            cur.execute(
                "UPDATE mesas SET estado = 'libre' WHERE id = (SELECT mesa_id FROM ordenes WHERE id = ?)",
                (orden_id,)
            )

        return True, None
    except sqlite3.IntegrityError as e:
        return False, f"Integridad DB: {e}"
    except Exception as e:
        return False, str(e)
    