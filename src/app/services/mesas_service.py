from typing import List, Optional, Tuple
from ..db.connection import crear_conexion, ConnectionManager

def obtener_mesas() -> List[Tuple]:
    """
    (id, numero, estado, seccion_id, seccion_nombre)
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT m.id, m.numero, m.estado, s.id AS seccion_id, s.nombre AS seccion_nombre
            FROM mesas m
            JOIN secciones s ON m.seccion_id = s.id
            ORDER BY s.nombre, m.numero
        """)
        return cur.fetchall()

def obtener_mesa_por_id(mesa_id: int) -> Optional[Tuple]:
    """
    (id, numero, estado, seccion_id, seccion_nombre)
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT m.id, m.numero, m.estado, s.id, s.nombre
            FROM mesas m
            JOIN secciones s ON m.seccion_id = s.id
            WHERE m.id = ?
        """, (mesa_id,))
        return cur.fetchone()


def crear_mesa(numero: int, seccion_id: int) -> bool:
    with ConnectionManager() as conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM mesas WHERE numero = ?", (numero,))
            if cur.fetchone()[0] > 0:
                return False
            cur.execute(
                "INSERT INTO mesas (numero, seccion_id, estado) VALUES (?, ?, ?)",
                (numero, seccion_id, "libre")
            )
            return True
        except Exception:
            conn.rollback()
            return False

def actualizar_mesa(mesa_id: int, numero: int, estado: str, seccion_id: int) -> bool:
    with ConnectionManager() as conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM mesas WHERE numero = ? AND id != ?", (numero, mesa_id))
            if cur.fetchone()[0] > 0:
                return False
            cur.execute(
                "UPDATE mesas SET numero = ?, estado = ?, seccion_id = ? WHERE id = ?",
                (numero, estado, seccion_id, mesa_id)
            )
            return True
        except Exception:
            conn.rollback()
            return False

def eliminar_mesa(mesa_id: int) -> bool:
    """
    Intenta eliminar la mesa. Devuelve False si hay órdenes abiertas o en caso de error.
    """
    with ConnectionManager() as conn:
        try:
            cur = conn.cursor()
            # comprobar órdenes abiertas (defensivo)
            try:
                cur.execute("SELECT COUNT(*) FROM ordenes WHERE mesa_id = ? AND estado = 'abierta'", (mesa_id,))
                if cur.fetchone()[0] > 0:
                    return False
            except Exception:
                # si no existe la tabla ordenes, continuar con la eliminación
                pass
            cur.execute("DELETE FROM mesas WHERE id = ?", (mesa_id,))
            return True
        except Exception:
            conn.rollback()
            return False

def cambiar_estado_mesa(mesa_id: int, nuevo_estado: str) -> bool:
    with ConnectionManager() as conn:
        try:
            cur = conn.cursor()
            cur.execute("UPDATE mesas SET estado = ? WHERE id = ?", (nuevo_estado, mesa_id))
            return True
        except Exception:
            conn.rollback()
            return False

def obtener_secciones() -> List[Tuple[int, str]]:
    """
    Devuelve lista de secciones como (id, nombre).
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, nombre FROM secciones ORDER BY nombre")
        return cur.fetchall()
    
def crear_seccion(nombre: str):
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO secciones (nombre) VALUES (?)", (nombre,))
        conn.commit()
        return cur.lastrowid

def eliminar_seccion(seccion_id: int) -> bool:
    """
    Elimina una sección si no tiene mesas asociadas.
    Devuelve True si se eliminó, False si no se pudo.
    """
    with ConnectionManager() as conn:
        try:
            cur = conn.cursor()
            # comprobar mesas asociadas
            cur.execute("SELECT COUNT(*) FROM mesas WHERE seccion_id = ?", (seccion_id,))
            if cur.fetchone()[0] > 0:
                return False  # no se puede eliminar, tiene mesas

            cur.execute("DELETE FROM secciones WHERE id = ?", (seccion_id,))
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False