# src/app/services/usuarios_service.py
from typing import List, Optional, Tuple
import hashlib
import sqlite3

from ..db.connection import ConnectionManager


def obtener_usuarios() -> List[Tuple]:
    """
    Devuelve lista de usuarios: [(id, nombre, apellido, usuario, rol), ...].
    (omitimos la clave en la respuesta por seguridad).
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        # Asegúrate de que la tabla 'usuarios' contiene las columnas nombre, apellido, usuario, rol
        cur.execute("SELECT id, nombre, apellido, usuario, rol FROM usuarios ORDER BY id")
        rows = cur.fetchall()

    # Si por compatibilidad la tabla no tiene 'apellido' (esquema antiguo), normalizamos la salida
    normalized = []
    for r in rows:
        # r esperado: (id, nombre, apellido, usuario, rol)
        if len(r) == 5:
            normalized.append(r)
        else:
            # fallback por si devuelve (id, usuario, rol) u otros formatos
            # intentamos reconstruir: (id, nombre='', apellido='', usuario=r[1], rol=r[2])
            if len(r) >= 3:
                normalized.append((r[0], r[1] if len(r) > 1 else "", "" , r[2] if len(r) > 2 else "", r[3] if len(r) > 3 else ""))
            else:
                normalized.append((r[0], "", "", "", ""))
    return normalized

def obtener_usuario_por_id(usuario_id: int) -> Optional[Tuple]:
    """
    Devuelve (id, nombre, usuario, rol) o None si no existe.
    No devuelve la clave en texto.
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, apellido, usuario, rol FROM usuarios WHERE id = ?", (usuario_id,))
        return cur.fetchone()

def registrar_usuario(nombre: str, apellido: str, usuario: str, clave: str, rol: str) -> Tuple[bool, Optional[str]]:
    """
    Registra un usuario nuevo.
    Devuelve (ok, mensaje_error).
    """
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = ?", (usuario,))
            if cur.fetchone()[0] > 0:
                return False, "El nombre de usuario ya existe"
            cur.execute(
                "INSERT INTO usuarios (nombre, apellido, usuario, clave, rol) VALUES (?, ?, ?, ?, ?)",
                (nombre, apellido, usuario, clave, rol)
            )
        return True, None
    except sqlite3.IntegrityError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def actualizar_usuario(usuario_id: int, nombre: str, apellido: str, usuario: str, clave: Optional[str], rol: str) -> Tuple[bool, Optional[str]]:
    """
    Actualiza un usuario. Si `clave` es None o cadena vacía, no la modifica.
    Devuelve (ok, mensaje_error).
    """
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = ? AND id != ?", (usuario, usuario_id))
            if cur.fetchone()[0] > 0:
                return False, "El nombre de usuario ya está en uso por otro usuario"
            if clave:
                cur.execute(
                    "UPDATE usuarios SET nombre = ?, apellido = ?, usuario = ?, clave = ?, rol = ? WHERE id = ?",
                    (nombre, apellido, usuario, clave, rol, usuario_id)
                )
            else:
                cur.execute(
                    "UPDATE usuarios SET nombre = ?, apellido = ?, usuario = ?, rol = ? WHERE id = ?",
                    (nombre, apellido, usuario, rol, usuario_id)
                )
        return True, None
    except sqlite3.IntegrityError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def eliminar_usuario_por_id(usuario_id: int) -> Tuple[bool, Optional[str]]:
    """
    Elimina un usuario por id. Devuelve (ok, mensaje_error).
    """
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
        return True, None
    except Exception as e:
        return False, str(e)