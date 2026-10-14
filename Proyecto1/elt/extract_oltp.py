"""
elt/extract_oltp.py
Extrae las tablas del esquema transaccional 'oltp_sgfood' y las carga en el esquema 'raw'.
"""

import logging
import pandas as pd
from datetime import datetime
from sqlalchemy import text
from elt.db import get_engine, execute_sql

logger = logging.getLogger("elt.extract_oltp")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

OLTP_TABLES = [
    "sucursal",
    "categoria",
    "marca",
    "producto",
    "cliente",
    "venta",
    "venta_detalle",
]

def ensure_schemas_exist() -> None:
    """Asegura que los esquemas oltp_sgfood y raw existan en PostgreSQL."""
    execute_sql("CREATE SCHEMA IF NOT EXISTS oltp_sgfood;")
    execute_sql("CREATE SCHEMA IF NOT EXISTS raw;")

def extract_and_load_oltp() -> dict[str, int]:
    """
    Lee cada tabla de oltp_sgfood y la copia de forma controlada e idempotente a raw.
    Retorna un diccionario con el conteo de registros por tabla.
    """
    logger.info("Iniciando extracción desde OLTP (oltp_sgfood) hacia RAW (raw)...")
    ensure_schemas_exist()
    engine = get_engine()
    results = {}
    now = datetime.now()

    for table in OLTP_TABLES:
        try:
            query = f"SELECT * FROM oltp_sgfood.{table};"
            df = pd.read_sql(query, con=engine)
            row_count = len(df)
            
            # Añadir metadato de trazabilidad
            df["_ingested_at"] = now
            
            # Truncar tabla para preservar vistas dependientes en staging
            with engine.begin() as conn:
                conn.execute(text(f"CREATE TABLE IF NOT EXISTS raw.{table} (LIKE oltp_sgfood.{table} INCLUDING ALL);"))
                # Asegurar columna _ingested_at si la tabla fue creada con LIKE
                conn.execute(text(f"ALTER TABLE raw.{table} ADD COLUMN IF NOT EXISTS _ingested_at TIMESTAMP;"))
                conn.execute(text(f"TRUNCATE TABLE raw.{table};"))

            # Cargar a raw con append
            df.to_sql(
                name=table,
                schema="raw",
                con=engine,
                if_exists="append",
                index=False,
                chunksize=1000,
            )
            
            results[table] = row_count
            logger.info("[OK] [OLTP -> RAW] Tabla '%s': %d filas extraídas y cargadas en raw.%s", table, row_count, table)
        except Exception as exc:
            logger.error("[ERROR] Error al transferir tabla '%s': %s", table, exc)
            raise

    logger.info("Extracción OLTP finalizada con éxito. %d tablas procesadas.", len(results))
    return results

if __name__ == "__main__":
    extract_and_load_oltp()
