from ..db.connection import ConnectionManager

def obtener_facturas_rango(fecha_inicio: str, fecha_fin: str):
    """
    Devuelve lista de facturas entre dos fechas.
    Cada fila: (id, numero_factura, fecha, cliente_nombre, total, orden_id)
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, numero_factura, fecha, cliente_nombre, total, orden_id
            FROM facturas
            WHERE fecha BETWEEN ? AND ?
            ORDER BY fecha DESC
        """, (fecha_inicio, fecha_fin))
        return cur.fetchall()


def obtener_facturas_por_cliente(cliente: str):
    """
    Devuelve lista de facturas filtradas por nombre de cliente (coincidencia parcial).
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, numero_factura, fecha, cliente_nombre, total, orden_id
            FROM facturas
            WHERE cliente_nombre LIKE ?
            ORDER BY fecha DESC
        """, (f"%{cliente}%",))
        return cur.fetchall()


def eliminar_factura(factura_id: int):
    """
    Elimina una factura y sus detalles asociados.
    Retorna (ok, error_msg).
    """
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            # obtener orden asociada
            cur.execute("SELECT orden_id FROM facturas WHERE id = ?", (factura_id,))
            row = cur.fetchone()
            if not row:
                return False, "Factura no encontrada"
            orden_id = row[0]

            # eliminar detalles de la orden
            cur.execute("DELETE FROM orden_detalles WHERE orden_id = ?", (orden_id,))
            # eliminar la orden
            cur.execute("DELETE FROM ordenes WHERE id = ?", (orden_id,))
            # eliminar la factura
            cur.execute("DELETE FROM facturas WHERE id = ?", (factura_id,))

            conn.commit()
        return True, None
    except Exception as e:
        return False, str(e)


from ..db.connection import ConnectionManager

def obtener_detalles_factura(factura_id: int):
    """
    Devuelve detalles de una factura.
    Cada fila: (producto, variante, cantidad, precio_unitario, subtotal, cliente_nombre)
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                mi.nombre AS producto,
                COALESCE(v.nombre, '') AS variante,
                d.cantidad,
                COALESCE(d.precio_unitario, d.precio) AS precio_unitario,
                d.subtotal,
                f.cliente_nombre
            FROM facturas f
            JOIN ordenes o ON f.orden_id = o.id
            JOIN orden_detalles d ON o.id = d.orden_id
            LEFT JOIN menu_items mi ON d.menu_item_id = mi.id
            LEFT JOIN menu_item_variant v ON d.variant_id = v.id
            WHERE f.id = ?
            ORDER BY d.id
        """, (factura_id,))
        return cur.fetchall()