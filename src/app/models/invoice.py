# src/app/models/invoice.py
from ..db.connection import ConnectionManager

class Invoice:
    def __init__(self, id, numero_factura, fecha, cliente_nombre, total, orden_id):
        self.id = id
        self.numero_factura = numero_factura
        self.fecha = fecha
        self.cliente_nombre = cliente_nombre
        self.total = total
        self.orden_id = orden_id

    @staticmethod
    def obtener_por_rango_fechas(desde: str, hasta: str):
        """Obtiene las facturas en un rango de fechas."""
        with ConnectionManager() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, numero_factura, fecha, cliente_nombre, total, orden_id "
                "FROM facturas WHERE fecha BETWEEN ? AND ? ORDER BY fecha",
                (desde, hasta)
            )
            rows = cur.fetchall()
            return [Invoice(*row) for row in rows]

    def obtener_detalle(self):
        """Obtiene el detalle de la factura (productos y precios)."""
        with ConnectionManager() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT producto_id, nombre, cantidad, precio_unitario, subtotal_linea "
                "FROM factura_detalles WHERE factura_id = ?",
                (self.id,)
            )
            rows = cur.fetchall()
            return [
                {
                    "producto_id": r[0],
                    "nombre": r[1],
                    "cantidad": r[2],
                    "precio_unitario": float(r[3]),
                    "subtotal_linea": float(r[4]),
                }
                for r in rows
            ]