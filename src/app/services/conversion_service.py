from ..db.connection import ConnectionManager
from typing import Optional

def guardar_tasa(fecha: str, tasa: float) -> bool:
    with ConnectionManager() as conn:
        cur = conn.cursor()
        try:
            cur.execute("INSERT OR REPLACE INTO tasas_cambio (fecha, tasa) VALUES (?, ?)", (fecha, tasa))
            return True
        except Exception as e:
            print("Error guardando tasa:", e)
            return False

def obtener_tasa(fecha: str) -> Optional[float]:
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("SELECT tasa FROM tasas_cambio WHERE fecha = ?", (fecha,))
        row = cur.fetchone()
        return float(row[0]) if row else None

def usd_a_ves(monto_usd: float, fecha: str) -> Optional[float]:
    tasa = obtener_tasa(fecha)
    if tasa is None:
        return None
    return round(monto_usd * tasa, 2)

def ves_a_usd(monto_ves: float, fecha: str) -> Optional[float]:
    tasa = obtener_tasa(fecha)
    if tasa is None:
        return None
    return round(monto_ves / tasa, 2)

def listar_tasas() -> list[tuple[str, float]]:
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("SELECT fecha, tasa FROM tasas_cambio ORDER BY fecha DESC")
        return [(row[0], float(row[1])) for row in cur.fetchall()]
    
def eliminar_tasa(fecha: str) -> bool:
    with ConnectionManager() as conn:
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM tasas_cambio WHERE fecha = ?", (fecha,))
            return True
        except Exception as e:
            print("Error eliminando tasa:", e)
            return False
        
def actualizar_tasa(fecha: str, nueva_tasa: float) -> bool:
    with ConnectionManager() as conn:
        cur = conn.cursor()
        try:
            cur.execute("UPDATE tasas_cambio SET tasa = ? WHERE fecha = ?", (nueva_tasa, fecha))
            return True
        except Exception as e:
            print("Error actualizando tasa:", e)
            return False
        
def obtener_tasa_del_dia() -> Optional[float]:
    """
    Devuelve la tasa más reciente registrada en la base de datos.
    Si no existe ninguna tasa, retorna None.
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("SELECT tasa FROM tasas_cambio ORDER BY fecha DESC LIMIT 1")
        row = cur.fetchone()
        return float(row[0]) if row else None