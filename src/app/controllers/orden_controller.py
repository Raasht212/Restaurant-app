# src/app/controllers/orden_controller.py
from typing import List, Dict, Tuple, Optional
import logging

from ..services import orden_service
from ..services.stock_service import aplicar_cambios_stock_atomic, consultar_stock_batch, consultar_stock

logger = logging.getLogger(__name__)


def preparar_payload(productos_seleccionados: List[Dict]) -> List[Dict]:
    payload = []
    for p in productos_seleccionados:
        try:
            # admite tanto "id" legacy como "menu_item_id"/"producto_id" según tu payload
            if "menu_item_id" in p:
                pid = int(p["menu_item_id"])
                key = "menu_item_id"
            elif "producto_id" in p:
                pid = int(p["producto_id"])
                key = "producto_id"
            else:
                # legacy: "id" se interpreta como producto_id
                pid = int(p["id"])
                key = "producto_id"

            cantidad = int(p.get("cantidad", 1))
            subtotal = p.get("subtotal")
            subtotal = float(subtotal) if subtotal not in (None, "") else None
        except Exception as exc:
            raise ValueError(f"Producto con formato inválido: {p}") from exc

        entry = {"cantidad": cantidad}
        entry[key] = pid
        if subtotal is not None:
            entry["subtotal"] = subtotal
        # propagar variant_id si existe
        if "variant_id" in p:
            entry["variant_id"] = int(p["variant_id"])
        payload.append(entry)
    return payload


def construir_cambios_stock(detalles_originales: Dict[int, Dict], productos_finales: List[Dict]) -> Dict[int, int]:
    """
    detalles_originales: mapping producto_id -> {"cantidad_original": int, ...}
    productos_finales: lista de dicts con llave 'producto_id' o 'menu_item_id' (solo los de productos físicos deben afectar stock)
    Retorna dict producto_id -> diff (positivo = se consumirá adicionalmente, negativo = devolver stock)
    """
    cambios: Dict[int, int] = {}
    # Normalizar final_map solo para productos que afectan stock (aquí consideramos 'producto_id' como los que usan stock)
    final_map = {}
    for p in productos_finales:
        if "producto_id" in p:
            final_map[int(p["producto_id"])] = int(p["cantidad"])
        else:
            # items de menú no gestionan stock en este esquema
            continue

    # Diffs por producto presentes en final_map
    for pid, cantidad_final in final_map.items():
        cantidad_original = int(detalles_originales.get(pid, {}).get("cantidad_original", 0))
        diff = cantidad_final - cantidad_original
        if diff != 0:
            cambios[pid] = cambios.get(pid, 0) + diff

    # Productos que estaban en originales pero ya no en final => devolver todo el original (diff negativo)
    for pid_str, det in detalles_originales.items():
        pid_int = int(pid_str)
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
    Flujo:
      1) preparar payload
      2) construir cambios de stock (solo para productos físicos: producto_id)
      3) validar disponibilidad (batch)
      4) persistir orden (crear o actualizar)
      5) aplicar cambios de stock atómicamente (si aplica)
      6) si falla aplicar stock, revertir la orden si era nueva
    """
    try:
        payload = preparar_payload(productos_seleccionados)
    except ValueError as e:
        return False, None, str(e)

    cambios = construir_cambios_stock(detalles_originales, payload)

    # 3) validar disponibilidad para diffs positivos usando consultar_stock_batch si existe
    positivos = {pid: diff for pid, diff in cambios.items() if diff > 0}
    if positivos:
        try:
            # si tienes una función batch es más eficiente; si no, consultar_stock_batch puede resolver
            if callable(consultar_stock_batch):
                stocks = consultar_stock_batch(list(positivos.keys()))
                # stocks: dict producto_id -> stock_actual (implementa según tu service)
                for pid, diff in positivos.items():
                    stock_actual = stocks.get(pid)
                    if stock_actual is None:
                        return False, None, f"Producto no existe id={pid}"
                    if stock_actual < diff:
                        return False, None, f"Stock insuficiente para producto id={pid} (solicitado={diff}, disponible={stock_actual})"
            else:
                # fallback: consultas individuales
                for pid, diff in positivos.items():
                    stock_actual = consultar_stock(pid)
                    if stock_actual is None:
                        return False, None, f"Producto no existe id={pid}"
                    if stock_actual < diff:
                        return False, None, f"Stock insuficiente para producto id={pid} (solicitado={diff}, disponible={stock_actual})"
        except Exception as e:
            logger.exception("Error validando stock: %s", e)
            return False, None, f"Error validando stock: {e}"

    # 4) persistir orden (aún no aplicamos cambios de stock)
    ok, nuevo_orden_id, err = orden_service.crear_o_actualizar_orden(mesa_id, cliente, payload, orden_id=orden_id)
    if not ok:
        return False, None, err

    # 5) aplicar diffs de stock atómicamente
    if cambios:
        try:
            ok_stock, msg_stock = aplicar_cambios_stock_atomic(cambios)
        except Exception as e:
            logger.exception("Error aplicando cambios de stock: %s", e)
            ok_stock, msg_stock = False, str(e)

        if not ok_stock:
            logger.warning("Fallo aplicando stock: %s. Intentando revertir orden (id=%s).", msg_stock, nuevo_orden_id)
            # 6) revertir: si la orden fue nueva, eliminarla; si fue actualización, preferimos informar al usuario
            try:
                if orden_id is None and nuevo_orden_id:
                    # borrar orden y sus detalles para deshacer
                    success_revert, err_revert = orden_service.cancelar_orden(nuevo_orden_id)
                    if not success_revert:
                        logger.error("No se pudo revertir orden recién creada id=%s: %s", nuevo_orden_id, err_revert)
                        return False, nuevo_orden_id, f"{msg_stock}; además fallo al revertir orden: {err_revert}"
                    # devolver mensaje de fallo de stock original
                    return False, None, msg_stock
                else:
                    # en caso de actualización decidimos no revertir automáticamente (riesgo de perder datos)
                    return False, nuevo_orden_id, f"Aplicación de stock falló: {msg_stock}"
            except Exception as e:
                logger.exception("Error durante revert de orden: %s", e)
                return False, nuevo_orden_id, f"{msg_stock}; además fallo al intentar revertir orden: {e}"

    return True, nuevo_orden_id, None


def generar_factura_flow(orden_id: int, cliente: str, total: float, numero_factura: str) -> Tuple[bool, Optional[str]]:
    ok, err = orden_service.insertar_factura(orden_id, numero_factura, cliente, total)
    return ok, err


def cancelar_orden_flow(orden_id: int) -> Tuple[bool, Optional[str]]:
    """
    Wrapper simple para cancelar orden usando orden_service.
    """
    ok, err = orden_service.cancelar_orden(orden_id)
    return ok, err