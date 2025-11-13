# src/app/db/init_db.py
from .connection import crear_conexion
from sqlite3 import Error
import logging

logger = logging.getLogger(__name__)

def inicializar_base_datos() -> bool:
    """Crear tablas necesarias, triggers e índices; devuelve True si todo OK."""
    comandos = [
        """CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            usuario TEXT UNIQUE NOT NULL,
            clave TEXT NOT NULL,
            rol TEXT NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS mesas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero INTEGER UNIQUE NOT NULL,
            estado TEXT NOT NULL DEFAULT 'libre',
            seccion_id INTEGER NOT NULL,
            FOREIGN KEY (seccion_id) REFERENCES secciones (id)
        )""",
        """CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS ordenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mesa_id INTEGER NOT NULL,
            cliente_nombre TEXT NOT NULL,
            estado TEXT NOT NULL DEFAULT 'abierta',
            total REAL DEFAULT 0,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cerrado_en TIMESTAMP,
            FOREIGN KEY (mesa_id) REFERENCES mesas (id)
        )""",
        """CREATE TABLE IF NOT EXISTS orden_detalles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orden_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (orden_id) REFERENCES ordenes (id),
            FOREIGN KEY (producto_id) REFERENCES productos (id)
        )""",
        """CREATE TABLE IF NOT EXISTS facturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orden_id INTEGER NOT NULL,
            numero_factura TEXT UNIQUE NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cliente_nombre TEXT NOT NULL,
            total REAL NOT NULL,
            FOREIGN KEY (orden_id) REFERENCES ordenes (id)
        )""",
        """CREATE TABLE IF NOT EXISTS secciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL
        )""",
    ]

    actualizaciones = [
        # Trigger para prevenir stock negativo
        "CREATE TRIGGER IF NOT EXISTS prevent_negative_stock "
        "BEFORE UPDATE ON productos "
        "FOR EACH ROW "
        "WHEN NEW.stock < 0 "
        "BEGIN "
        "   SELECT RAISE(ABORT, 'Stock no puede ser negativo'); "
        "END;",
        # Índice para evitar más de una orden abierta por mesa
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_mesa_orden_abierta "
        "ON ordenes(mesa_id) WHERE estado = 'abierta';"
    ]

    conn = crear_conexion()
    if not conn:
        logger.error("Inicialización abortada: no se pudo obtener conexión")
        return False

    try:
        cur = conn.cursor()
        for sql in comandos:
            try:
                cur.execute(sql)
            except Error:
                logger.exception("Error al ejecutar comando de creación: %s", sql)

        for sql in actualizaciones:
            try:
                cur.execute(sql)
            except Error:
                logger.debug("Actualización omitida (posible ya aplicada): %s", sql)

        conn.commit()

        # seed inicial: admin + mesas si no existen usuarios
        try:
            cur.execute("SELECT COUNT(*) FROM usuarios")
            if cur.fetchone()[0] == 0:
                cur.execute(
                    "INSERT INTO usuarios (nombre, usuario, clave, rol) VALUES (?, ?, ?, ?)",
                    ("Administrador", "admin", "admin", "admin")
                )
                
                
                # Crear secciones iniciales
                cur.execute("INSERT INTO secciones (nombre) VALUES (?)", ("Principal",))
                cur.execute("INSERT INTO secciones (nombre) VALUES (?)", ("Terraza",))

                # Obtener IDs de secciones
                cur.execute("SELECT id FROM secciones WHERE nombre = ?", ("Principal",))
                principal_id = cur.fetchone()[0]
                cur.execute("SELECT id FROM secciones WHERE nombre = ?", ("Terraza",))
                terraza_id = cur.fetchone()[0]

                # Crear mesas asociadas
                for i in range(1, 6):
                    cur.execute("INSERT INTO mesas (numero, seccion_id) VALUES (?, ?)", (i, principal_id))
                for i in range(6, 11):
                    cur.execute("INSERT INTO mesas (numero, seccion_id) VALUES (?, ?)", (i, terraza_id))

                    
                    
                    
                    
                    
                    
                    
                    
                conn.commit()
        except Error:
            logger.exception("Error al insertar datos iniciales")

        return True
    except Error:
        logger.exception("Error inicializando la base de datos")
        return False
    finally:
        conn.close()