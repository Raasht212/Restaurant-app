# src/app/services/usuarios_service.py
from typing import List, Optional, Tuple
import hashlib
import sqlite3

from ..db.connection import ConnectionManager

def _encriptar_clave(clave: str) -> str:
    return hashlib.sha256(clave.encode("utf-8")).hexdigest()

def obtener_usuarios() -> List[Tuple]:
    """
    Devuelve lista de usuarios: [(id, usuario, rol), ...]
    (omitimos la clave en la respuesta por seguridad).
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, usuario, rol FROM usuarios ORDER BY id")
        return cur.fetchall()

def obtener_usuario_por_id(usuario_id: int) -> Optional[Tuple]:
    """
    Devuelve (id, nombre, usuario, rol) o None si no existe.
    No devuelve la clave en texto.
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, usuario, rol FROM usuarios WHERE id = ?", (usuario_id,))
        return cur.fetchone()

def registrar_usuario(nombre: str, usuario: str, clave: str, rol: str) -> Tuple[bool, Optional[str]]:
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
            clave_encriptada = _encriptar_clave(clave)
            cur.execute(
                "INSERT INTO usuarios (nombre, usuario, clave, rol) VALUES (?, ?, ?, ?)",
                (nombre, usuario, clave_encriptada, rol)
            )
        return True, None
    except sqlite3.IntegrityError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def actualizar_usuario(usuario_id: int, nombre: str, usuario: str, clave: Optional[str], rol: str) -> Tuple[bool, Optional[str]]:
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
                clave_encriptada = _encriptar_clave(clave)
                cur.execute(
                    "UPDATE usuarios SET nombre = ?, usuario = ?, clave = ?, rol = ? WHERE id = ?",
                    (nombre, usuario, clave_encriptada, rol, usuario_id)
                )
            else:
                cur.execute(
                    "UPDATE usuarios SET nombre = ?, usuario = ?, rol = ? WHERE id = ?",
                    (nombre, usuario, rol, usuario_id)
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