"""
config/settings.py
------------------
Carga variables de entorno desde .env y construye los objetos de configuración
necesarios para la conexión a SQL Server y el pipeline ETL.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Cargar .env desde la raíz del proyecto
_BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(_BASE_DIR / ".env")


# ---------------------------------------------------------------------------
# Parámetros de conexión a SQL Server
# ---------------------------------------------------------------------------
DB_SERVER: str = os.getenv("DB_SERVER", "localhost,1433")
DB_NAME: str = os.getenv("DB_NAME", "VuelosDW")
DB_USER: str = os.getenv("DB_USER", "sa")
DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
DB_DRIVER: str = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")

# ---------------------------------------------------------------------------
# Rutas de datos
# ---------------------------------------------------------------------------
RAW_DATA_PATH: Path = _BASE_DIR / os.getenv("RAW_DATA_PATH", "dataset_vuelos_crudo.csv")
RAW_SNAPSHOT_DIR: Path = _BASE_DIR / "data" / "raw"
PROCESSED_DIR: Path = _BASE_DIR / "data" / "processed"
LOGS_DIR: Path = _BASE_DIR / "logs"
SQL_DDL_PATH: Path = _BASE_DIR / "sql" / "ddl" / "create_model.sql"

# Crear directorios si no existen
for _dir in (RAW_SNAPSHOT_DIR, PROCESSED_DIR, LOGS_DIR):
    _dir.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()


def get_sqlalchemy_url() -> str:
    """
    Construye la URL de conexión para SQLAlchemy usando pyodbc.

    Usa TrustServerCertificate=yes para entornos de desarrollo Docker
    (el certificado de SQL Server en contenedor es auto-firmado).
    """
    if not DB_PASSWORD:
        raise EnvironmentError(
            "DB_PASSWORD no está definida. Crea un archivo .env basado en .env.example."
        )
    # Escapar parámetros con %2B para que SQLAlchemy no los malinterprete
    odbc_str = (
        f"DRIVER={{{DB_DRIVER}}};"
        f"SERVER={DB_SERVER};"
        f"DATABASE={DB_NAME};"
        f"UID={DB_USER};"
        f"PWD={DB_PASSWORD};"
        f"TrustServerCertificate=yes;"
        f"Encrypt=yes;"
    )
    import urllib.parse
    return "mssql+pyodbc:///?odbc_connect=" + urllib.parse.quote_plus(odbc_str)


def get_pyodbc_conn_str() -> str:
    """
    Devuelve el connection string de pyodbc puro (para uso directo sin SQLAlchemy).
    """
    if not DB_PASSWORD:
        raise EnvironmentError(
            "DB_PASSWORD no está definida. Crea un archivo .env basado en .env.example."
        )
    return (
        f"DRIVER={{{DB_DRIVER}}};"
        f"SERVER={DB_SERVER};"
        f"DATABASE=master;"
        f"UID={DB_USER};"
        f"PWD={DB_PASSWORD};"
        f"TrustServerCertificate=yes;"
        f"Encrypt=yes;"
    )
