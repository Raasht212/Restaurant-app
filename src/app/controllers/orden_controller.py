# src/app/controllers/orden_controller.py
from typing import List, Dict, Tuple, Optional
import logging

from ..services import orden_service

logger = logging.getLogger(__name__)


def preparar_payload(productos_seleccionados: List[Dict]) -> List[Dict]:
    """
    Normaliza la lista de productos seleccionados.
    Solo admite items de menú (menu_item_id + optional variant_id).
    """
    payload = []
    for p in productos_seleccionados:
        try:
            if "menu_item_id" not in p:
                raise ValueError(f"Detalle inválido, falta menu_item_id: {p}")

            pid = int(p["menu_item_id"])
            cantidad = int(p.get("cantidad", 1))
            if cantidad <= 0:
                raise ValueError(f"Cantidad inválida: {p}")

            subtotal = p.get("subtotal")
            subtotal = float(subtotal) if subtotal not in (None, "") else None
        except Exception as exc:
            raise ValueError(f"Producto con formato inválido: {p}") from exc

        entry = {"cantidad": cantidad, "menu_item_id": pid}
        if subtotal is not None:
            entry["subtotal"] = subtotal
        if "variant_id" in p:
            entry["variant_id"] = int(p["variant_id"])
        payload.append(entry)
    return payload


def confirmar_orden_flow(
    mesa_id: Optional[int],
    cliente: str,
    productos_seleccionados: List[Dict],
    orden_id: Optional[int] = None
) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Flujo simplificado:
      1) preparar payload
      2) persistir orden (crear o actualizar)
    """
    try:
        payload = preparar_payload(productos_seleccionados)
    except ValueError as e:
        return False, None, str(e)

    ok, nuevo_orden_id, err = orden_service.crear_o_actualizar_orden(
        mesa_id, cliente, payload, orden_id=orden_id
    )
    if not ok:
        return False, None, err

    return True, nuevo_orden_id, None


def generar_factura_flow(
    orden_id: int, cliente: str, total: float, numero_factura: str
) -> Tuple[bool, Optional[str]]:
    """
    Genera factura y cierra la orden.
    """
    ok, err = orden_service.insertar_factura(orden_id, numero_factura, cliente, total)
    return ok, err


def cancelar_orden_flow(orden_id: int) -> Tuple[bool, Optional[str]]:
    """
    Wrapper simple para cancelar orden usando orden_service.
    """
    ok, err = orden_service.cancelar_orden(orden_id)
    return ok, err