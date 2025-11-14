# src/app/logging_config.py
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from .config import BASE_DIR, LOG_LEVEL

LOG_FILE = Path(BASE_DIR) / "logs" / "app.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

def configure_logging():
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    logging.root.setLevel(level)

    fmt = "%(asctime)s %(levelname)s %(name)s: %(message)s"
    formatter = logging.Formatter(fmt)

    # Consola (stdout)
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    console.setLevel(level)

    # Archivo rotativo
    file_handler = RotatingFileHandler(str(LOG_FILE), maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    # Limpiar handlers previos (evita duplicados en desarrollo)
    for h in list(logging.root.handlers):
        logging.root.removeHandler(h)

    logging.root.addHandler(console)
    logging.root.addHandler(file_handler)

    # Opcional: niveles más verbosos para librerías específicas
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)