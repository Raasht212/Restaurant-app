# src/app/services/menu_service.py
from typing import List, Optional, Tuple, Dict, Any
import sqlite3
from ..db.connection import ConnectionManager

# Tipos de retorno:
# - CRUD que devuelven listas: List[Tuple] o List[Dict]
# - Operaciones que cambian estado devuelven Tuple[bool, Optional[str]] -> (ok, error_message)

# --------------------------
# Secciones (menu_section)
# --------------------------



def listar_secciones(only_active: bool = True) -> List[Tuple]:
    """
    Devuelve lista de secciones.
    Cada fila: (id, nombre, descripcion, position, active)
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        if only_active:
            cur.execute("SELECT id, nombre, descripcion, position, active FROM menu_sections WHERE active=1 ORDER BY position, nombre")
        else:
            cur.execute("SELECT id, nombre, descripcion, position, active FROM menu_sections ORDER BY position, nombre")
        return cur.fetchall()


def crear_seccion(nombre: str, descripcion: Optional[str] = None, position: int = 0) -> Tuple[bool, Optional[str]]:
    """
    Crea una sección. Devuelve (ok, error_message).
    """
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO menu_sections(nombre, descripcion, position) VALUES (?, ?, ?)", (nombre, descripcion, position))
            conn.commit()
        return True, None
    except sqlite3.IntegrityError as e:
        return False, "Ya existe una sección con ese nombre"
    except Exception as e:
        return False, str(e)


def obtener_seccion_por_id(section_id: int) -> Optional[Tuple]:
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, descripcion, position, active FROM menu_sections WHERE id = ?", (section_id,))
        return cur.fetchone()


def actualizar_seccion(section_id: int, nombre: str, descripcion: Optional[str], position: int, active: int = 1) -> Tuple[bool, Optional[str]]:
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE menu_sections SET nombre = ?, descripcion = ?, position = ?, active = ? WHERE id = ?",
                        (nombre, descripcion, position, active, section_id))
            conn.commit()
        return True, None
    except sqlite3.IntegrityError:
        return False, "Ya existe una sección con ese nombre"
    except Exception as e:
        return False, str(e)


def eliminar_seccion(section_id: int, soft: bool = True) -> Tuple[bool, Optional[str]]:
    """
    Elimina una sección.
    - Si soft=True marca active=0 (recomendado).
    - Si soft=False intenta borrado físico (fallará si hay items referenciando la sección).
    """
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            if soft:
                cur.execute("UPDATE menu_sections SET active = 0 WHERE id = ?", (section_id,))
            else:
                cur.execute("DELETE FROM menu_sections WHERE id = ?", (section_id,))
            conn.commit()
        return True, None
    except Exception as e:
        return False, str(e)


# --------------------------
# Items (menu_items)
# --------------------------
def listar_items_por_seccion(section_id: int, only_disponible: bool = True) -> List[Tuple]:
    """
    Devuelve lista de items en una sección.
    Cada fila: (id, section_id, nombre, descripcion, precio, disponible, position, created_at)
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        if only_disponible:
            cur.execute("""
                SELECT id, section_id, nombre, descripcion, precio, disponible, position, created_at
                FROM menu_items
                WHERE section_id = ? AND disponible = 1
                ORDER BY position, nombre
            """, (section_id,))
        else:
            cur.execute("""
                SELECT id, section_id, nombre, descripcion, precio, disponible, position, created_at
                FROM menu_items
                WHERE section_id = ?
                ORDER BY position, nombre
            """, (section_id,))
        return cur.fetchall()


def crear_item(section_id: int, nombre: str, descripcion: Optional[str], precio: float, disponible: int = 1, position: int = 0) -> Tuple[bool, Optional[str]]:
    """
    Crea un item en la sección indicada.
    Devuelve (ok, error_message).
    """
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO menu_items (section_id, nombre, descripcion, precio, disponible, position)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (section_id, nombre, descripcion, precio, disponible, position))
            conn.commit()
        return True, None
    except sqlite3.IntegrityError as e:
        # normalmente aquí no hay constraint UNIQUE por nombre+section, si lo añades puede entrar aquí
        return False, "Registro duplicado o error de integridad"
    except Exception as e:
        return False, str(e)


def obtener_item_por_id(item_id: int) -> Optional[Tuple]:
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, section_id, nombre, descripcion, precio, disponible, position, created_at
            FROM menu_items WHERE id = ?
        """, (item_id,))
        return cur.fetchone()


def actualizar_item(item_id: int, section_id: int, nombre: str, descripcion: Optional[str], precio: float, disponible: int = 1, position: int = 0) -> Tuple[bool, Optional[str]]:
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE menu_items
                SET section_id = ?, nombre = ?, descripcion = ?, precio = ?, disponible = ?, position = ?
                WHERE id = ?
            """, (section_id, nombre, descripcion, precio, disponible, position, item_id))
            conn.commit()
        return True, None
    except sqlite3.IntegrityError:
        return False, "Registro duplicado o error de integridad"
    except Exception as e:
        return False, str(e)


def eliminar_item(item_id: int) -> Tuple[bool, Optional[str]]:
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM menu_items WHERE id = ?", (item_id,))
            conn.commit()
        return True, None
    except Exception as e:
        return False, str(e)


# --------------------------
# Utilidades y helpers
# --------------------------
def toggle_disponibilidad_item(item_id: int, disponible: int) -> Tuple[bool, Optional[str]]:
    """
    Cambia la disponibilidad de un ítem (1 = disponible, 0 = no disponible)
    """
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE menu_items SET disponible = ? WHERE id = ?", (1 if disponible else 0, item_id))
            conn.commit()
        return True, None
    except Exception as e:
        return False, str(e)


def mover_item_position(item_id: int, new_position: int) -> Tuple[bool, Optional[str]]:
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE menu_items SET position = ? WHERE id = ?", (new_position, item_id))
            conn.commit()
        return True, None
    except Exception as e:
        return False, str(e)


def buscar_items_por_nombre(term: str, only_disponible: bool = True) -> List[Tuple]:
    """
    Búsqueda simple por nombre en todo el menú.
    """
    like = f"%{term}%"
    with ConnectionManager() as conn:
        cur = conn.cursor()
        if only_disponible:
            cur.execute("""
                SELECT id, section_id, nombre, descripcion, precio, disponible, position, created_at
                FROM menu_items
                WHERE nombre LIKE ? AND disponible = 1
                ORDER BY section_id, position, nombre
            """, (like,))
        else:
            cur.execute("""
                SELECT id, section_id, nombre, descripcion, precio, disponible, position, created_at
                FROM menu_items
                WHERE nombre LIKE ?
                ORDER BY section_id, position, nombre
            """, (like,))
        return cur.fetchall()