from ..db.connection import ConnectionManager

def obtener_detalles_factura(factura_id: int):
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT p.nombre, d.cantidad, d.precio, d.subtotal
            FROM facturas f
            JOIN ordenes o ON f.orden_id = o.id
            JOIN orden_detalles d ON o.id = d.orden_id
            JOIN productos p ON d.producto_id = p.id
            WHERE f.id = ?
        """, (factura_id,))
        return cur.fetchall()