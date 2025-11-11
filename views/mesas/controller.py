from typing import List, Optional, Tuple
from database import crear_conexion

def obtener_mesas() -> List[Tuple]:
    """
    Devuelve una lista de tuplas con el formato:
    (id, numero, estado, seccion)
    """
    conexion = crear_conexion()
    if not conexion:
        return []
    try:
        cur = conexion.cursor()
        cur.execute("SELECT id, numero, estado, seccion FROM mesas ORDER BY seccion, numero")
        return cur.fetchall()
    finally:
        conexion.close()

def obtener_mesa_por_id(mesa_id: int) -> Optional[Tuple]:
    conexion = crear_conexion()
    if not conexion:
        return None
    try:
        cur = conexion.cursor()
        cur.execute("SELECT id, numero, estado, seccion FROM mesas WHERE id = ?", (mesa_id,))
        return cur.fetchone()
    finally:
        conexion.close()

def crear_mesa(numero: int, seccion: str = "Principal") -> bool:
    conexion = crear_conexion()
    if not conexion:
        return False
    try:
        cur = conexion.cursor()
        cur.execute("SELECT COUNT(*) FROM mesas WHERE numero = ?", (numero,))
        if cur.fetchone()[0] > 0:
            return False
        cur.execute("INSERT INTO mesas (numero, seccion, estado) VALUES (?, ?, ?)", (numero, seccion, "libre"))
        conexion.commit()
        return True
    except Exception:
        return False
    finally:
        conexion.close()

def actualizar_mesa(mesa_id: int, numero: int, estado: str, seccion: str) -> bool:
    conexion = crear_conexion()
    if not conexion:
        return False
    try:
        cur = conexion.cursor()
        cur.execute("SELECT COUNT(*) FROM mesas WHERE numero = ? AND id != ?", (numero, mesa_id))
        if cur.fetchone()[0] > 0:
            return False
        cur.execute("UPDATE mesas SET numero = ?, estado = ?, seccion = ? WHERE id = ?", (numero, estado, seccion, mesa_id))
        conexion.commit()
        return True
    except Exception:
        return False
    finally:
        conexion.close()

def eliminar_mesa(mesa_id: int) -> bool:
    """
    Intenta eliminar la mesa. Devuelve False si hay órdenes abiertas o en caso de error.
    """
    conexion = crear_conexion()
    if not conexion:
        return False
    try:
        cur = conexion.cursor()
        # comprobar órdenes abiertas (defensivo)
        try:
            cur.execute("SELECT COUNT(*) FROM ordenes WHERE mesa_id = ? AND estado = 'abierta'", (mesa_id,))
            if cur.fetchone()[0] > 0:
                return False
        except Exception:
            # si no existe la tabla ordenes, continuar con la eliminación
            pass
        cur.execute("DELETE FROM mesas WHERE id = ?", (mesa_id,))
        conexion.commit()
        return True
    except Exception:
        return False
    finally:
        conexion.close()

def cambiar_estado_mesa(mesa_id: int, nuevo_estado: str) -> bool:
    conexion = crear_conexion()
    if not conexion:
        return False
    try:
        cur = conexion.cursor()
        cur.execute("UPDATE mesas SET estado = ? WHERE id = ?", (nuevo_estado, mesa_id))
        conexion.commit()
        return True
    except Exception:
        return False
    finally:
        conexion.close()

def obtener_secciones() -> List[str]:
    conexion = crear_conexion()
    if not conexion:
        return []
    try:
        cur = conexion.cursor()
        cur.execute("SELECT DISTINCT seccion FROM mesas ORDER BY seccion")
        rows = cur.fetchall()
        return [r[0] for r in rows if r and r[0]]
    finally:
        conexion.close()