# src/app/services/orden_service.py
from typing import List, Tuple, Optional, Dict
import sqlite3
import datetime

from ..db.connection import ConnectionManager

# Formato de fila devuelta por obtener_detalles_orden:
# (detalle_id, item_id, nombre, cantidad, precio_unitario, subtotal, variant_id, fuente)

# --------------------------
# Lecturas simples
# --------------------------
def obtener_orden_abierta_por_mesa(mesa_id: int) -> Optional[Tuple[int, Optional[str], Optional[float]]]:
    """
    Devuelve (orden_id, cliente_nombre, total) de la orden abierta para la mesa, o None.
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, cliente_nombre, total FROM ordenes WHERE mesa_id = ? AND estado = 'abierta' LIMIT 1",
            (mesa_id,)
        )
        return cur.fetchone()


def obtener_detalles_orden(orden_id: int) -> List[Tuple]:
    """
    Devuelve los detalles de la orden haciendo JOIN a menu_items.
    Cada fila: (detalle_id, item_id, nombre, cantidad, precio_unitario, subtotal, variant_id)
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                d.id,
                d.menu_item_id AS item_id,
                mi.nombre AS nombre,
                d.cantidad,
                COALESCE(d.precio_unitario, d.precio) AS precio_unitario,
                d.subtotal,
                d.variant_id
            FROM orden_detalles d
            LEFT JOIN menu_items mi ON mi.id = d.menu_item_id
            WHERE d.orden_id = ?
            ORDER BY d.id
        """, (orden_id,))
        return cur.fetchall()


# --------------------------
# Helpers internos
# --------------------------
def _now_iso() -> str:
    return datetime.datetime.now().isoformat(sep=' ', timespec='seconds')

def _validar_y_calcular_detalles(cur, productos: List[Dict]) -> Tuple[bool, Optional[str], List[Dict], float]:
    """
    Normaliza y valida la lista de productos recibidos.
    Cada dict entrante debe ser:
      - {"menu_item_id": X, "variant_id": optional, "cantidad": N, "subtotal": optional}
    Retorna: (ok, msg_error, detalles_normalizados, total)
    detalle normalizado ejemplo:
      {"menu_item_id": int, "variant_id": Optional[int], "cantidad": int,
       "precio_unitario": float, "subtotal": float, "fuente": "menu"}
    """
    detalles = []
    total = 0.0

    for p in productos:
        # validar cantidad
        try:
            cantidad = int(p.get("cantidad", 1))
            if cantidad <= 0:
                return False, f"Cantidad inválida para línea: {p}", [], 0.0
        except Exception:
            return False, f"Cantidad inválida para línea: {p}", [], 0.0

        menu_item_id = p.get("menu_item_id")
        variant_id = p.get("variant_id")

        if menu_item_id is None:
            return False, f"Detalle sin menu_item_id válido: {p}", [], 0.0

        # obtener precio base del item de menú
        cur.execute("SELECT precio FROM menu_items WHERE id = ?", (int(menu_item_id),))
        row = cur.fetchone()
        if not row:
            return False, f"Item de menú no existe (id={menu_item_id})", [], 0.0
        precio = float(row[0])

        # si viene variante, preferir precio de variante
        if variant_id is not None:
            cur.execute("SELECT precio FROM menu_item_variant WHERE id = ?", (int(variant_id),))
            vr = cur.fetchone()
            if not vr:
                return False, f"Variante no existe (id={variant_id})", [], 0.0
            precio = float(vr[0])

        subtotal = p.get("subtotal")
        if subtotal in (None, ""):
            subtotal = round(precio * cantidad, 2)
        else:
            try:
                subtotal = round(float(subtotal), 2)
            except Exception:
                return False, f"Subtotal inválido en línea: {p}", [], 0.0

        detalles.append({
            "menu_item_id": int(menu_item_id),
            "variant_id": int(variant_id) if variant_id is not None else None,
            "cantidad": cantidad,
            "precio_unitario": precio,
            "subtotal": subtotal,
            "fuente": "menu"
        })
        total += subtotal

    return True, None, detalles, round(total, 2)


# --------------------------
# Crear / Actualizar órdenes
# --------------------------
def crear_o_actualizar_orden(
    mesa_id: Optional[int],
    cliente_nombre: str,
    productos: List[Dict],
    orden_id: Optional[int] = None
) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Crea o actualiza una orden y sus detalles.
    - Si orden_id es None crea una orden nueva; si se proporciona actualiza existente.
    - Devuelve (ok, orden_id, mensaje_error)
    """
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            ahora = _now_iso()

            # Validar y normalizar líneas
            ok, msg, detalles_norm, total = _validar_y_calcular_detalles(cur, productos)
            if not ok:
                return False, None, msg

            if orden_id:
                # actualizar cabecera y reemplazar detalles
                cur.execute(
                    "UPDATE ordenes SET cliente_nombre = ?, total = ?, actualizado_en = ? WHERE id = ?",
                    (cliente_nombre, float(total), ahora, orden_id)
                )
                cur.execute("DELETE FROM orden_detalles WHERE orden_id = ?", (orden_id,))
                nuevo_id = orden_id
            else:
                # crear orden nueva
                cur.execute(
                    "INSERT INTO ordenes (mesa_id, cliente_nombre, total, estado, fecha) VALUES (?, ?, ?, 'abierta', ?)",
                    (mesa_id, cliente_nombre, float(total), ahora)
                )
                nuevo_id = cur.lastrowid
                # marcar mesa ocupada si aplica
                if mesa_id is not None:
                    cur.execute("UPDATE mesas SET estado = 'ocupado' WHERE id = ?", (mesa_id,))

            # Insertar detalles normalizados (solo fuente 'menu')
            for d in detalles_norm:
                cur.execute("""
                    INSERT INTO orden_detalles
                    (orden_id, menu_item_id, variant_id, cantidad, precio, precio_unitario, subtotal)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    nuevo_id,
                    d["menu_item_id"],
                    d.get("variant_id"),
                    d["cantidad"],
                    d["precio_unitario"],   # mantener 'precio' legacy
                    d["precio_unitario"],
                    d["subtotal"]
                ))

            conn.commit()
        return True, nuevo_id, None
    except sqlite3.IntegrityError as e:
        return False, None, f"Integridad DB: {e}"
    except Exception as e:
        return False, None, str(e)


# --------------------------
# Cancelar / Facturar
# --------------------------
def cancelar_orden(orden_id: int) -> Tuple[bool, Optional[str]]:
    """
    Cancela una orden abierta: elimina detalles y la orden, libera la mesa.
    """
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            # obtener mesa asociada
            cur.execute("SELECT mesa_id FROM ordenes WHERE id = ? AND estado = 'abierta'", (orden_id,))
            row = cur.fetchone()
            if not row:
                return False, "Orden no existe o no está abierta"
            mesa_id = row[0]

            # eliminar detalles y orden
            cur.execute("DELETE FROM orden_detalles WHERE orden_id = ?", (orden_id,))
            cur.execute("DELETE FROM ordenes WHERE id = ?", (orden_id,))

            # liberar mesa si aplica
            if mesa_id is not None:
                cur.execute("UPDATE mesas SET estado = 'libre' WHERE id = ?", (mesa_id,))

            conn.commit()
        return True, None
    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        return False, str(e)


def insertar_factura(
    orden_id: int,
    numero_factura: str,
    cliente_nombre: str,
    total: float
) -> Tuple[bool, Optional[str]]:
    """
    Inserta una factura, marca la orden como cerrada y libera la mesa asociada.
    """
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            ahora = _now_iso()

            # insertar factura
            cur.execute(
                "INSERT INTO facturas (orden_id, numero_factura, cliente_nombre, total, fecha) VALUES (?, ?, ?, ?, ?)",
                (orden_id, numero_factura, cliente_nombre, float(total), ahora)
            )

            # marcar orden como cerrada
            cur.execute(
                "UPDATE ordenes SET estado = 'cerrada', cerrado_en = ? WHERE id = ?",
                (ahora, orden_id)
            )

            # liberar mesa asociada si existe
            cur.execute("SELECT mesa_id FROM ordenes WHERE id = ?", (orden_id,))
            row = cur.fetchone()
            mesa_id = row[0] if row else None
            if mesa_id is not None:
                cur.execute("UPDATE mesas SET estado = 'libre' WHERE id = ?", (mesa_id,))

            conn.commit()
        return True, None
    except sqlite3.IntegrityError as e:
        try:
            conn.rollback()
        except Exception:
            pass
        return False, f"Integridad DB: {e}"
    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        return False, str(e)


def listar_ordenes_abiertas(estado: str = "abierta"):
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, mesa_id, cliente_nombre, total, fecha FROM ordenes WHERE estado = ? ORDER BY fecha DESC",
            (estado,)
        )
        return [
            (int(r[0]), int(r[1]) if r[1] is not None else None, r[2] or "", float(r[3] or 0.0), r[4])
            for r in cur.fetchall()
        ]


def obtener_orden_por_id(orden_id: int):
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, mesa_id, cliente_nombre, total, estado, fecha FROM ordenes WHERE id = ?", (orden_id,))
        r = cur.fetchone()
        if not r:
            return None
        return {
            "id": int(r[0]),
            "mesa_id": int(r[1]) if r[1] is not None else None,
            "cliente": r[2] or "",
            "total": float(r[3] or 0.0),
            "estado": r[4],
            "fecha": r[5]
        }