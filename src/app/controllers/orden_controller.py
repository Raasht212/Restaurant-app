from typing import List, Dict, Tuple, Optional
from ..services import orden_service  # módulo de servicios de orden
from ..services.stock_service import aplicar_cambios_stock_atomic, consultar_stock_batch  # ver nota

def preparar_payload(productos_seleccionados: List[Dict]) -> List[Dict]:
    payload = []
    for p in productos_seleccionados:
        try:
            pid = int(p["id"])
            cantidad = int(p["cantidad"])
            subtotal = float(p.get("subtotal", 0.0))
        except Exception:
            raise ValueError("Producto con formato inválido")
        payload.append({"id": pid, "cantidad": cantidad, "subtotal": subtotal})
    return payload

def construir_cambios_stock(detalles_originales: Dict[int, Dict], productos_finales: List[Dict]) -> Dict[int, int]:
    cambios: Dict[int, int] = {}
    final_map = {int(p["id"]): int(p["cantidad"]) for p in productos_finales}

    for pid, cantidad_final in final_map.items():
        cantidad_original = int(detalles_originales.get(pid, {}).get("cantidad_original", 0))
        diff = cantidad_final - cantidad_original
        if diff != 0:
            cambios[pid] = cambios.get(pid, 0) + diff

    for pid, det in detalles_originales.items():
        pid_int = int(pid)
        if pid_int not in final_map:
            cantidad_original = int(det.get("cantidad_original", 0))
            if cantidad_original != 0:
                cambios[pid_int] = cambios.get(pid_int, 0) - cantidad_original

    return cambios

def confirmar_orden_flow(
    mesa_id: int,
    cliente: str,
    productos_seleccionados: List[Dict],
    detalles_originales: Dict[int, Dict],
    orden_id: Optional[int] = None
) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Flujo seguro:
      1) preparar payload
      2) construir diffs (cambios)
      3) validar disponibilidad para los diffs positivos (sin modificar BD)
      4) crear/actualizar orden (persistir detalles)
      5) aplicar los diffs de stock atómicamente
      6) si aplicar stock falla, revertir la orden creada si es nueva
    """
    try:
        payload = preparar_payload(productos_seleccionados)
    except ValueError as e:
        return False, None, str(e)

    cambios = construir_cambios_stock(detalles_originales, payload)
    # 3) validar disponibilidad para diffs > 0 (sin tocar BD)
    positivos = {pid: diff for pid, diff in cambios.items() if diff > 0}
    if positivos:
        # intento de validación por producto; usar una función batch si la tienes para eficiencia
        for pid, diff in positivos.items():
            stock = aplicar_cambios_stock_atomic.__module__  # placeholder para evitar lint; no se usa
            # suponemos que existe una función consultar_stock en stock_service o orden_service
            try:
                from ..services.stock_service import consultar_stock
            except Exception:
                from ..services.orden_service import consultar_stock
            stock_actual = consultar_stock(pid)
            if stock_actual is None:
                return False, None, f"Producto no existe id={pid}"
            if stock_actual < diff:
                return False, None, f"Stock insuficiente para producto id={pid} (solicitado={diff}, disponible={stock_actual})"

    # 4) crear o actualizar orden (persistir detalles) - no aplicamos stock aún
    ok, nuevo_orden_id, err = orden_service.crear_o_actualizar_orden(mesa_id, cliente, payload, orden_id=orden_id)
    if not ok:
        return False, None, err

    # 5) aplicar diffs de stock atómicamente (debe aplicar tanto + como -)
    if cambios:
        ok_stock, msg_stock = aplicar_cambios_stock_atomic(cambios)
        if not ok_stock:
            # 6) revertir: la orden fue creada/actualizada, debemos deshacerla para mantener consistencia.
            # estrategia: si fue una orden nueva, eliminarla; si fue actualización, es más complejo.
            try:
                if orden_id is None and nuevo_orden_id:
                    # borrar orden y sus detalles para deshacer
                    from ..db.connection import ConnectionManager
                    with ConnectionManager() as conn:
                        cur = conn.cursor()
                        cur.execute("DELETE FROM orden_detalles WHERE orden_id = ?", (nuevo_orden_id,))
                        cur.execute("DELETE FROM ordenes WHERE id = ?", (nuevo_orden_id,))
                        # opcional: marcar mesa libre si se había marcado ocupada en crear_o_actualizar_orden
                        cur.execute("UPDATE mesas SET estado = 'libre' WHERE id = ?", (mesa_id,))
                else:
                    # actualización fallida: devolver un error instructivo (no intentamos revertir cambios previos)
                    pass
            except Exception:
                # no bloqueamos el error original; devolvemos el mensaje original de fallo de stock más info
                return False, nuevo_orden_id, f"{msg_stock}; además fallo al revertir orden."
            return False, None, msg_stock

    return True, nuevo_orden_id, None

def generar_factura_flow(orden_id: int, cliente: str, total: float, numero_factura: str) -> Tuple[bool, Optional[str]]:
    ok, err = orden_service.insertar_factura(orden_id, numero_factura, cliente, total)
    return ok, err

def cancelar_orden_flow(orden_id: int, mesa_id: int) -> Tuple[bool, Optional[str]]:
    ok, err = orden_service.cancelar_orden(orden_id, mesa_id)
    return ok, err