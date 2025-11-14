# src/app/db/connection.py
from pathlib import Path
import sqlite3
from sqlite3 import Error
from typing import Optional
from ..config import DB_PATH
import logging

logger = logging.getLogger(__name__)

def crear_conexion(path: Optional[Path] = None) -> Optional[sqlite3.Connection]:
    """Crear y devolver una conexión sqlite3; devuelve None en fallo."""
    db_path = Path(path) if path else Path(DB_PATH)
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        return conn
    except Error:
        logger.exception("No se pudo crear la conexión a la BD (%s)", db_path)
        return None

class ConnectionManager:
    """Context manager para conexiones sqlite3.

    Uso:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            ...
    """
    def __init__(self, path: Optional[Path] = None):
        self.path = Path(path) if path else Path(DB_PATH)
        self.conn: Optional[sqlite3.Connection] = None

    def __enter__(self):
        try:
            self.conn = sqlite3.connect(str(self.path))
            self.conn.row_factory = sqlite3.Row
            return self.conn
        except Error:
            logger.exception("No se pudo abrir la conexión (%s)", self.path)
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.conn:
            return
        try:
            if exc_type:
                self.conn.rollback()
            else:
                self.conn.commit()
        finally:
            self.conn.close()
            self.conn = None