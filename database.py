import sqlite3
from sqlite3 import Error
import datetime

def crear_conexion():
    """Crear conexión a la base de datos"""
    try:
        conexion = sqlite3.connect('restaurante.db')
        return conexion
    except Error as e:
        print(e)
    return None

def inicializar_base_datos():
    """Crear tablas necesarias y actualizar esquema si es necesario"""
    comandos = [
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            usuario TEXT UNIQUE NOT NULL,
            clave TEXT NOT NULL,
            rol TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS mesas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero INTEGER UNIQUE NOT NULL,
            estado TEXT NOT NULL DEFAULT 'libre',
            seccion TEXT NOT NULL DEFAULT 'Principal'
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS ordenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mesa_id INTEGER NOT NULL UNIQUE,  -- CAMBIO IMPORTANTE: UNIQUE
            cliente_nombre TEXT NOT NULL,
            estado TEXT NOT NULL DEFAULT 'abierta',
            total REAL DEFAULT 0,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (mesa_id) REFERENCES mesas (id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS orden_detalles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orden_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (orden_id) REFERENCES ordenes (id),
            FOREIGN KEY (producto_id) REFERENCES productos (id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS facturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orden_id INTEGER NOT NULL,
            numero_factura TEXT UNIQUE NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cliente_nombre TEXT NOT NULL,
            total REAL NOT NULL,
            FOREIGN KEY (orden_id) REFERENCES ordenes (id))
        """
    ]
    
    # Comandos para actualizar tablas existentes (si es necesario)
    actualizaciones = [
        "ALTER TABLE mesas ADD COLUMN seccion TEXT DEFAULT 'Principal';",
        "CREATE TRIGGER IF NOT EXISTS prevent_negative_stock "
        "BEFORE UPDATE ON productos "
        "FOR EACH ROW "
        "WHEN NEW.stock < 0 "
        "BEGIN "
        "   SELECT RAISE(ABORT, 'Stock no puede ser negativo'); "
        "END;",
        # Nueva restricción para ordenes
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_mesa_orden_abierta "
        "ON ordenes(mesa_id) WHERE estado = 'abierta';"
    ]
    
    conexion = crear_conexion()
    if conexion is not None:
        try:
            cursor = conexion.cursor()
            
            # Ejecutar comandos para crear tablas
            for comando in comandos:
                try:
                    cursor.execute(comando)
                except sqlite3.OperationalError as e:
                    print(f"Error al ejecutar comando: {e}")
            
            # Intentar agregar la nueva columna si no existe
            for actualizacion in actualizaciones:
                try:
                    cursor.execute(actualizacion)
                except sqlite3.OperationalError:
                    pass  # La columna ya existe, no hay problema
            
            conexion.commit()
            
            # Crear usuario admin inicial
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    "INSERT INTO usuarios (nombre, usuario, clave, rol) VALUES (?, ?, ?, ?)",
                    ("Administrador", "admin", "admin", "admin")
                )
                conexion.commit()
                
                # Crear 10 mesas iniciales (5 en Principal, 5 en Terraza)
                for i in range(1, 11):
                    seccion = "Principal" if i <= 5 else "Terraza"
                    cursor.execute(
                        "INSERT INTO mesas (numero, seccion) VALUES (?, ?)",
                        (i, seccion)
                    )
                conexion.commit()
                
        except Error as e:
            print(f"Error inicializando BD: {e}")
        finally:
            conexion.close()

# Inicializar BD al importar
inicializar_base_datos()