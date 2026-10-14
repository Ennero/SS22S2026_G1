"""
elt/db.py
Módulo de conexión a PostgreSQL para el proceso ELT de SG-Food.
"""

import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("elt.db")

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "sgfood_dw")

def get_connection_url(db_name: str = POSTGRES_DB) -> str:
    """Retorna la URL de conexión SQLAlchemy para PostgreSQL."""
    return f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{db_name}"

def get_engine(db_name: str = POSTGRES_DB) -> Engine:
    """Crea y retorna un Engine de SQLAlchemy."""
    url = get_connection_url(db_name)
    return create_engine(url, pool_pre_ping=True)

def execute_sql(sql_query: str, db_name: str = POSTGRES_DB) -> None:
    """Ejecuta una sentencia SQL en la base de datos."""
    engine = get_engine(db_name)
    with engine.begin() as conn:
        conn.execute(text(sql_query))

def test_connection() -> bool:
    """Verifica si la base de datos responde correctamente."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1;")).scalar()
            logger.info("Conexión exitosa a PostgreSQL: %s (resultado: %s)", POSTGRES_DB, result)
            return True
    except Exception as exc:
        logger.error("Error al conectar a PostgreSQL: %s", exc)
        return False

if __name__ == "__main__":
    test_connection()
