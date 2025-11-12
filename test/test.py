import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import datetime
import random

# --- 1. SIMULACIÓN DE LA BASE DE DATOS Y DATOS ---

def crear_datos_simulados(nombre_db="ventas.db"):
    """Crea una base de datos SQLite con datos de ventas por día."""
    conexion = sqlite3.connect(nombre_db)
    cursor = conexion.cursor()
    
    # Crear la tabla si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            fecha TEXT,
            monto REAL
        )
    """)
    conexion.commit()
    
    # Simular 30 días de datos
    hoy = datetime.date.today()
    datos = []
    for i in range(30):
        fecha = (hoy - datetime.timedelta(days=i)).isoformat()
        monto = round(random.uniform(500, 2500), 2)
        datos.append((fecha, monto))
    
    # Insertar datos (borrando los viejos para asegurar la simulación)
    cursor.execute("DELETE FROM ventas")
    cursor.executemany("INSERT INTO ventas (fecha, monto) VALUES (?, ?)", datos)
    conexion.commit()
    conexion.close()
    print(f"Base de datos '{nombre_db}' creada con 30 días de datos.")


# --- 2. FUNCIÓN PRINCIPAL DE GRÁFICOS ---

def generar_grafico_ventas(nombre_db="ventas.db"):
    """Carga los datos de ventas y genera un gráfico de línea."""
    
    # 1. Conexión a la Base de Datos
    conexion = sqlite3.connect(nombre_db)
    
    # 2. Cargar datos con Pandas
    # Usamos read_sql_query para leer directamente los datos en un DataFrame
    df = pd.read_sql_query("SELECT * FROM ventas ORDER BY fecha ASC", conexion)
    
    conexion.close()

    if df.empty:
        print("No hay datos para graficar.")
        return

    # 3. Preparación de Fechas (el paso clave)
    # Convertir la columna 'fecha' a tipo datetime de Pandas
    df['fecha'] = pd.to_datetime(df['fecha'])
    
    # Establecer la columna 'fecha' como índice del DataFrame
    df.set_index('fecha', inplace=True)
    
    # 4. Generación del Gráfico
    plt.figure(figsize=(10, 6)) # Define el tamaño de la figura
    
    # Plotea la columna 'monto'. Pandas usa Matplotlib internamente
    df['monto'].plot(kind='line', marker='o', linestyle='-') 
    
    plt.title("Evolución de Ventas Diarias")
    plt.xlabel("Fecha")
    plt.ylabel("Monto de Ventas ($)")
    plt.grid(True)
    
    # Mejorar la visualización de las etiquetas de fecha en el eje X
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout() # Ajusta el layout para que las etiquetas no se corten
    
    # 5. Mostrar el gráfico
    plt.show()

# --- 3. EJECUCIÓN DEL PROGRAMA ---

if __name__ == "__main__":
    # Simular la creación de datos de prueba
    crear_datos_simulados()
    
    # Generar y mostrar el gráfico
    generar_grafico_ventas()