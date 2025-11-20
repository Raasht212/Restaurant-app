# src/app/db/init_db.py
from .connection import crear_conexion
from sqlite3 import Error
import logging

logger = logging.getLogger(__name__)

def inicializar_base_datos() -> bool:
    """
    Crear tablas, triggers e índices necesarios para la aplicación.
    Devuelve True si la inicialización se completó (o ya estaba aplicada).
    """
    comandos = [
        # Usuarios
        """CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT,
            usuario TEXT UNIQUE NOT NULL,
            clave TEXT NOT NULL,
            rol TEXT NOT NULL
        )""",

        # Secciones (para mesas)
        """CREATE TABLE IF NOT EXISTS secciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL
        )""",

        # Mesas
        """CREATE TABLE IF NOT EXISTS mesas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero INTEGER UNIQUE NOT NULL,
            estado TEXT NOT NULL DEFAULT 'libre',
            seccion_id INTEGER NOT NULL,
            FOREIGN KEY (seccion_id) REFERENCES secciones (id)
        )""",

        # Productos legacy (opcional, por compatibilidad)
        """CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL
        )""",

        # Órdenes
        """CREATE TABLE IF NOT EXISTS ordenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mesa_id INTEGER NOT NULL,
            cliente_nombre TEXT NOT NULL,
            estado TEXT NOT NULL DEFAULT 'abierta',
            total REAL DEFAULT 0,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            actualizado_en TIMESTAMP,
            cerrado_en TIMESTAMP,
            FOREIGN KEY (mesa_id) REFERENCES mesas (id)
        )""",


        """CREATE TABLE IF NOT EXISTS orden_detalles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orden_id INTEGER NOT NULL,
            producto_id INTEGER DEFAULT NULL,      -- compatibilidad con tabla productos
            menu_item_id INTEGER DEFAULT NULL,     -- referencia a menu_items (si aplica)
            variant_id INTEGER DEFAULT NULL,       -- referencia a variante (si se usa)
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL,                  -- campo legacy: precio aplicado (mantener compatibilidad)
            precio_unitario REAL DEFAULT NULL,     -- precio unitario explícito (más claro)
            subtotal REAL NOT NULL,
            fuente TEXT DEFAULT 'producto',        -- 'producto' o 'menu' para depuración
            FOREIGN KEY (orden_id) REFERENCES ordenes (id)
            -- NOTA: no se crean FKs hacia productos/menu_items para facilitar migraciones;
            -- se pueden añadir recreando la tabla con las constraints si se desea.
        )""",

        # Facturas
        """CREATE TABLE IF NOT EXISTS facturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orden_id INTEGER NOT NULL,
            numero_factura TEXT UNIQUE NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cliente_nombre TEXT NOT NULL,
            total REAL NOT NULL,
            FOREIGN KEY (orden_id) REFERENCES ordenes (id)
        )""",

        # Tasas de cambio
        """CREATE TABLE IF NOT EXISTS tasas_cambio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha DATE NOT NULL UNIQUE,
            tasa REAL NOT NULL
        )""",

        # Menú: secciones y items
        """CREATE TABLE IF NOT EXISTS menu_sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            descripcion TEXT DEFAULT NULL,
            position INTEGER DEFAULT 0,
            active INTEGER NOT NULL DEFAULT 1
        )""",

        """CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            descripcion TEXT DEFAULT NULL,
            precio REAL NOT NULL DEFAULT 0.0,
            disponible INTEGER NOT NULL DEFAULT 1,
            position INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (section_id) REFERENCES menu_sections(id) ON DELETE RESTRICT
        )""",

        # Variantes / tamaños por item (opcional; dejar para futuras mejoras)
        """CREATE TABLE IF NOT EXISTS menu_item_variant (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            menu_item_id INTEGER NOT NULL,
            clave TEXT NOT NULL,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            sku TEXT DEFAULT NULL,
            position INTEGER DEFAULT 0,
            active INTEGER NOT NULL DEFAULT 1,
            UNIQUE(menu_item_id, clave),
            FOREIGN KEY (menu_item_id) REFERENCES menu_items(id) ON DELETE CASCADE
        )"""
    ]

    actualizaciones = [
        # Trigger para prevenir stock negativo en productos (legacy)
        "CREATE TRIGGER IF NOT EXISTS prevent_negative_stock "
        "BEFORE UPDATE ON productos "
        "FOR EACH ROW "
        "WHEN NEW.stock < 0 "
        "BEGIN "
        "   SELECT RAISE(ABORT, 'Stock no puede ser negativo'); "
        "END;",

        # Índice para evitar más de una orden abierta por mesa
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_mesa_orden_abierta "
        "ON ordenes(mesa_id) WHERE estado = 'abierta';",

        # Índices para orden_detalles
        "CREATE INDEX IF NOT EXISTS idx_orden_detalles_menu_item ON orden_detalles(menu_item_id);",
        "CREATE INDEX IF NOT EXISTS idx_orden_detalles_producto ON orden_detalles(producto_id);",
        "CREATE INDEX IF NOT EXISTS idx_orden_detalles_orden ON orden_detalles(orden_id);",

        # Índices para menú
        "CREATE INDEX IF NOT EXISTS idx_menu_items_section ON menu_items(section_id);",
        "CREATE INDEX IF NOT EXISTS idx_menu_sections_position ON menu_sections(position);",
        "CREATE INDEX IF NOT EXISTS idx_variant_menu_item ON menu_item_variant(menu_item_id);"
    ]

    conn = crear_conexion()
    if not conn:
        logger.error("Inicialización abortada: no se pudo obtener conexión")
        return False

    try:
        cur = conn.cursor()

        # Asegurar que SQLite respete FKs
        try:
            cur.execute("PRAGMA foreign_keys = ON;")
        except Exception:
            pass

        # Ejecutar creación de tablas
        for sql in comandos:
            try:
                cur.execute(sql)
            except Error:
                logger.exception("Error al ejecutar comando de creación: %s", sql)

        # Ejecutar actualizaciones (triggers, índices)
        for sql in actualizaciones:
            try:
                cur.execute(sql)
            except Error:
                logger.debug("Actualización omitida o ya aplicada: %s", sql)

        conn.commit()

        # Seed inicial (solo si la tabla usuarios está vacía)
        try:
            cur.execute("SELECT COUNT(*) FROM usuarios")
            if cur.fetchone()[0] == 0:
                # usuario admin por defecto (cambiar contraseña en primer uso)
                cur.execute(
                    "INSERT INTO usuarios (nombre, apellido, usuario, clave, rol) VALUES (?, ?, ?, ?, ?)",
                    ("Administrador", "", "admin", "admin", "admin")
                )

                # Crear secciones iniciales de mesas
                cur.execute("INSERT INTO secciones (nombre) VALUES (?)", ("Principal",))
                cur.execute("INSERT INTO secciones (nombre) VALUES (?)", ("Terraza",))

                cur.execute("SELECT id FROM secciones WHERE nombre = ?", ("Principal",))
                principal_id = cur.fetchone()[0]
                cur.execute("SELECT id FROM secciones WHERE nombre = ?", ("Terraza",))
                terraza_id = cur.fetchone()[0]

                # Crear mesas asociadas
                for i in range(1, 6):
                    cur.execute("INSERT INTO mesas (numero, seccion_id) VALUES (?, ?)", (i, principal_id))
                for i in range(6, 11):
                    cur.execute("INSERT INTO mesas (numero, seccion_id) VALUES (?, ?)", (i, terraza_id))

                # Crear secciones del menú y algunos items de ejemplo
                cur.execute("INSERT OR IGNORE INTO menu_sections (nombre, descripcion, position, active) VALUES (?, ?, ?, ?)",
                            ("Pizzas", "Pizzas artesanales", 0, 1))
                cur.execute("INSERT OR IGNORE INTO menu_sections (nombre, descripcion, position, active) VALUES (?, ?, ?, ?)",
                            ("Bebidas", None, 1, 1))
                cur.execute("INSERT OR IGNORE INTO menu_sections (nombre, descripcion, position, active) VALUES (?, ?, ?, ?)",
                            ("Postres", None, 2, 1))

                # Obtener ids de secciones del menú
                cur.execute("SELECT id FROM menu_sections WHERE nombre = ?", ("Pizzas",))
                row = cur.fetchone()
                pizzas_section = row[0] if row else None

                # Insertar items ejemplo (si no existen)
                if pizzas_section:
                    cur.execute("INSERT OR IGNORE INTO menu_items (section_id, nombre, descripcion, precio, disponible, position) VALUES (?, ?, ?, ?, ?, ?)",
                                (pizzas_section, "Margarita", "Queso, salsa y albahaca", 8.50, 1, 0))
                    cur.execute("INSERT OR IGNORE INTO menu_items (section_id, nombre, descripcion, precio, disponible, position) VALUES (?, ?, ?, ?, ?, ?)",
                                (pizzas_section, "Pepperoni", "Pepperoni extra", 9.50, 1, 1))

                conn.commit()
        except Error:
            logger.exception("Error al insertar datos iniciales")

        return True
    except Error:
        logger.exception("Error inicializando la base de datos")
        return False
    finally:
        conn.close()