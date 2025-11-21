from ..db.connection import ConnectionManager

def obtener_usuario_logeado():
    """
    Devuelve el nombre del usuario actualmente logeado.
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("SELECT nombre FROM usuarios WHERE logeado = 1 LIMIT 1")
        row = cur.fetchone()
        return row[0] if row else "Invitado"