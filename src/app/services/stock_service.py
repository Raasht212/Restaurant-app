# src/app/services/stock_service.py
from typing import Dict, Optional, Tuple
from ..db.connection import ConnectionManager

def verificar_stock_suficiente(conn, cambios: Dict[int, int]) -> Tuple[bool, Optional[str]]:
    """
    cambios: {producto_id: cantidad_a_restar (positivo)}
    Verifica en la conexión dada que hay stock suficiente para todos los productos.
    """
    cur = conn.cursor()
    for pid, cantidad in cambios.items():
        if cantidad <= 0:
            continue
        cur.execute("SELECT stock, nombre FROM productos WHERE id = ?", (pid,))
        row = cur.fetchone()
        if not row:
            return False, f"Producto con ID {pid} no encontrado"
        stock_actual, nombre = row
        if stock_actual < cantidad:
            return False, f"No hay suficiente stock de {nombre} (disponible {stock_actual})"
    return True, None

def aplicar_cambios_stock_atomic(cambios: Dict[int, int]) -> Tuple[bool, Optional[str]]:
    """
    Aplica cambios de stock en una transacción única. Usa ConnectionManager.
    cambios: {producto_id: cantidad_a_restar (positivo) o negativa si se ajusta hacia arriba}
    """
    try:
        with ConnectionManager() as conn:
            ok, msg = verificar_stock_suficiente(conn, {k: v for k, v in cambios.items() if v > 0})
            if not ok:
                return False, msg
            cur = conn.cursor()
            for pid, diff in cambios.items():
                if diff == 0:
                    continue
                # restamos diff (si diff positivo), si diff negativo suma stock
                cur.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", (diff, pid))
        return True, None
    except Exception as e:
        return False, str(e)
    
def consultar_stock_batch(productos: Dict[int, int]) -> Dict[int, Optional[int]]:
    """
    Recibe un dict {producto_id: cantidad_solicitada}
    Devuelve {producto_id: stock_actual} o None si no existe.
    """
    resultados = {}
    with ConnectionManager() as conn:
        cur = conn.cursor()
        for pid in productos.keys():
            cur.execute("SELECT stock FROM productos WHERE id = ?", (pid,))
            row = cur.fetchone()
            resultados[pid] = int(row[0]) if row else None
    return resultados
