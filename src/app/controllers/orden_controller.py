# src/app/controllers/orden_controller.py
from typing import List, Dict, Tuple, Optional
from ..services.orden_service import crear_o_actualizar_orden, insertar_factura
from ..services.stock_service import aplicar_cambios_stock_atomic

def preparar_payload(productos_seleccionados: List[Dict]) -> List[Dict]:
    """
    Normaliza y valida el esquema mínimo esperado para cada producto:
    {'id': int, 'cantidad': int, 'subtotal': float}
    """
    payload = []
    for p in productos_seleccionados:
        try:
            pid = int(p["id"])
            cantidad = int(p["cantidad"])
            subtotal = float(p["subtotal"])
        except Exception:
            raise ValueError("Producto con formato inválido")
        payload.append({"id": pid, "cantidad": cantidad, "subtotal": subtotal})
    return payload

def construir_cambios_stock(detalles_originales: Dict[int, Dict], productos_finales: List[Dict]) -> Dict[int, int]:
    """
    Construye el dict cambios donde:
      cambios[producto_id] = diferencia (positiva => restar stock; negativa => sumar stock)
    - detalles_originales: {pid: {'cantidad_original': X, ...}}
    - productos_finales: list de {'id', 'cantidad', 'subtotal'}
    """
    cambios: Dict[int, int] = {}
    final_map = {int(p["id"]): int(p["cantidad"]) for p in productos_finales}

    # aumentos / modificaciones
    for pid, cantidad_final in final_map.items():
        cantidad_original = int(detalles_originales.get(pid, {}).get("cantidad_original", 0))
        diff = cantidad_final - cantidad_original
        if diff != 0:
            cambios[pid] = cambios.get(pid, 0) + diff

    # eliminados -> devolver stock (diff negativo)
    for pid, det in detalles_originales.items():
        if pid not in final_map:
            cantidad_original = int(det.get("cantidad_original", 0))
            if cantidad_original != 0:
                cambios[pid] = cambios.get(pid, 0) - cantidad_original

    return cambios

def confirmar_orden_flow(
    mesa_id: int,
    cliente: str,
    productos_seleccionados: List[Dict],
    detalles_originales: Dict[int, Dict],
    orden_id: Optional[int] = None
) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Orquesta el flujo completo de confirmación de orden:
      1) prepara payload
      2) construye cambios de stock
      3) verifica y aplica aumentos de stock atómicamente
      4) crea/actualiza orden en BD
      5) aplica el resto de cambios (incluye decrementos negativos) atómicamente
    Devuelve (ok, orden_id, mensaje_error)
    """
    try:
        payload = preparar_payload(productos_seleccionados)
    except ValueError as e:
        return False, None, str(e)

    cambios = construir_cambios_stock(detalles_originales, payload)

    # Primero validar y aplicar aumentos (diff > 0) para reservar stock
    aumentos = {k: v for k, v in cambios.items() if v > 0}
    if aumentos:
        ok, msg = aplicar_cambios_stock_atomic(aumentos)
        if not ok:
            return False, None, msg

    # Crear o actualizar orden (persistir detalles)
    ok, nuevo_orden_id, err = crear_o_actualizar_orden(mesa_id, cliente, payload, orden_id=orden_id)
    if not ok:
        return False, None, err

    # Aplicar los cambios restantes (pueden incluir negativos y los positivos ya aplicados; re-aplicar
    # completos aquí si tu servicio espera la carga total). Para seguridad aplicamos los diffs restantes.
    restante = {k: v for k, v in cambios.items() if v != 0}
    if restante:
        ok2, msg2 = aplicar_cambios_stock_atomic(restante)
        if not ok2:
            return False, nuevo_orden_id, msg2

    return True, nuevo_orden_id, None

def generar_factura_flow(orden_id: int, cliente: str, total: float, numero_factura: str) -> Tuple[bool, Optional[str]]:
    """
    Encapsula el llamado a insertar_factura y devuelve (ok, mensaje_error)
    """
    ok, err = insertar_factura(orden_id, numero_factura, cliente, total)
    return ok, err