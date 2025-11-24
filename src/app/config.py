# src/app/config.py
from pathlib import Path
import os
import sys


def resource_path(*relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, *relative_path)


# Ruta base del proyecto (dos niveles arriba de src/app/config.py -> proyecto/)
BASE_DIR: Path = Path(__file__).resolve().parents[2]

# Ruta a la base de datos (por defecto en la raíz del proyecto)
DB_PATH: Path = BASE_DIR / "restaurante.db"

# Carpeta de recursos (qss, iconos, imágenes)
#RESOURCES_DIR: Path = BASE_DIR / "resources"

# Parámetros de configuración
DEBUG: bool = os.environ.get("APP_DEBUG", "1") not in ("0", "False", "false")
LOG_LEVEL: str = os.environ.get("APP_LOG_LEVEL", "DEBUG" if DEBUG else "INFO")

# Opciones de UI / defaults
DEFAULT_WINDOW_SIZE = (1024, 768)
APP_NAME = "Sistema Restaurante"

def get_env_bool(name: str, default: bool) -> bool:
    val = os.environ.get(name)
    if val is None:
        return default
    return val not in ("0", "False", "false")

# Función utilitaria para obtener rutas dentro de resources
#def resource_path(*parts: str) -> Path:
#    return RESOURCES_DIR.joinpath(*parts)