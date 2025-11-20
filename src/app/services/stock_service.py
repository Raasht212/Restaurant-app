# src/app/services/stock_service.py
from typing import Dict, List, Optional, Tuple
import sqlite3
import logging

from ..db.connection import ConnectionManager

logger = logging.getLogger(__name__)

def consultar_stock(producto_id: int) -> Optional[int]:
    """
    Devuelve el stock actual del producto (int) o None si no existe.
    """
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            cur.execute("SELECT stock FROM productos WHERE id = ?", (int(producto_id),))
            row = cur.fetchone()
            return int(row[0]) if row and row[0] is not None else None
    except Exception as e:
        logger.exception("Error consultando stock para id=%s: %s", producto_id, e)
        return None

def consultar_stock_batch(producto_ids: List[int]) -> Dict[int, Optional[int]]:
    """
    Devuelve un dict {producto_id: stock_actual_or_None} para la lista de ids.
    Siempre devuelve una entrada por id solicitada.
    """
    if not producto_ids:
        return {}
    try:
        placeholders = ",".join("?" for _ in producto_ids)
        sql = f"SELECT id, stock FROM productos WHERE id IN ({placeholders})"
        with ConnectionManager() as conn:
            cur = conn.cursor()
            cur.execute(sql, tuple(producto_ids))
            rows = cur.fetchall()
        result: Dict[int, Optional[int]] = {pid: None for pid in producto_ids}
        for r in rows:
            pid = int(r[0])
            stock = int(r[1]) if r[1] is not None else None
            result[pid] = stock
        return result
    except Exception as e:
        logger.exception("Error en consultar_stock_batch: %s", e)
        # fallback: devolver None para todos
        return {pid: None for pid in producto_ids}

def aplicar_cambios_stock_atomic(cambios: Dict[int, int]) -> Tuple[bool, Optional[str]]:
    """
    Aplica diffs de stock de forma atómica (todos o ninguno).
    'cambios' es dict producto_id -> diff (positivo = reducir stock, negativo = aumentar stock).
    Retorna (ok, mensaje_error).
    Nota: en SQLite usamos transacción explícita. Validamos que no quedará stock negativo.
    """
    if not cambios:
        return True, None

    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            # Asegurar modo transaccional explícito
            try:
                cur.execute("BEGIN")
            except Exception:
                pass

            # Validar que todos los productos existen y que los diffs positivos tienen stock suficiente
            ids = list(cambios.keys())
            placeholders = ",".join("?" for _ in ids)
            cur.execute(f"SELECT id, stock FROM productos WHERE id IN ({placeholders})", tuple(ids))
            rows = {int(r[0]): (int(r[1]) if r[1] is not None else None) for r in cur.fetchall()}

            for pid, diff in cambios.items():
                if pid not in rows:
                    conn.rollback()
                    return False, f"Producto no existe id={pid}"
                stock_actual = rows[pid]
                # diff positivo significa consumir stock adicional
                if diff > 0:
                    if stock_actual is None:
                        conn.rollback()
                        return False, f"Producto id={pid} no tiene campo stock definido"
                    if stock_actual < diff:
                        conn.rollback()
                        return False, f"Stock insuficiente para producto id={pid} (solicitado={diff}, disponible={stock_actual})"

            # Aplicar cambios
            for pid, diff in cambios.items():
                # reducir stock si diff>0 => stock = stock - diff
                # aumentar stock si diff<0 => stock = stock - diff (restar negativo -> sumar)
                cur.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", (diff, pid))

            conn.commit()
        return True, None
    except sqlite3.IntegrityError as ie:
        logger.exception("Integrity error aplicando cambios de stock: %s", ie)
        try:
            conn.rollback()
        except Exception:
            pass
        return False, str(ie)
    except Exception as e:
        logger.exception("Error aplicando cambios de stock: %s", e)
        try:
            conn.rollback()
        except Exception:
            pass
        return False, str(e)