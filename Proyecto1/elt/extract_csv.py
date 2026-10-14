"""
elt/extract_csv.py
Extrae archivos CSV externos y los carga en el esquema 'raw' de PostgreSQL.
"""

import os
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd
from sqlalchemy import text
from elt.db import get_engine, execute_sql

logger = logging.getLogger("elt.extract_csv")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

def get_data_dir() -> Path:
    """Encuentra y retorna el directorio donde residen los archivos de datos."""
    env_dir = os.getenv("DATA_DIR")
    candidates = []
    if env_dir:
        candidates.append(Path(env_dir))
    candidates.extend([
        Path("/opt/airflow/Data"),
        Path(__file__).resolve().parent.parent / "Data",
        Path("Data"),
    ])
    for path in candidates:
        if path.exists() and path.is_dir():
            return path
    raise FileNotFoundError("No se encontró el directorio de datos 'Data'. Verifique las rutas configuradas.")

CSV_FILES_MAPPING = {
    "inventario_bodega.csv": "inventario_bodega",
    "proveedores_precios.csv": "proveedores_precios",
    "promociones.csv": "promociones",
    "metas_ventas.csv": "metas_ventas",
    "devoluciones.csv": "devoluciones",
}

def extract_and_load_csvs() -> dict[str, int]:
    """
    Lee cada archivo CSV externo y lo carga de forma idempotente en el esquema 'raw'.
    Retorna un diccionario con el número de filas cargadas por tabla.
    """
    data_dir = get_data_dir()
    logger.info("Directorio de datos identificado: %s", data_dir)
    
    execute_sql("CREATE SCHEMA IF NOT EXISTS raw;")
    engine = get_engine()
    results = {}
    now = datetime.now()

    for csv_file, table_name in CSV_FILES_MAPPING.items():
        file_path = data_dir / csv_file
        if not file_path.exists():
            logger.warning("El archivo '%s' no existe en %s. Omitiendo...", csv_file, data_dir)
            continue

        try:
            # Lectura del CSV preservando tipos para staging de dbt
            df = pd.read_csv(file_path, encoding="utf-8")
            row_count = len(df)
            
            # Añadir metadatos de trazabilidad
            df["_ingested_at"] = now
            df["_source_file"] = csv_file
            
            # Truncar tabla si ya existe para preservar vistas dependientes en staging
            with engine.begin() as conn:
                table_exists = conn.execute(
                    text(f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'raw' AND table_name = '{table_name}');")
                ).scalar()
                if table_exists:
                    conn.execute(text(f"TRUNCATE TABLE raw.{table_name};"))

            # Cargar a raw con append
            df.to_sql(
                name=table_name,
                schema="raw",
                con=engine,
                if_exists="append",
                index=False,
                chunksize=1000,
            )
            
            results[table_name] = row_count
            logger.info("[OK] [CSV -> RAW] Archivo '%s' -> raw.%s: %d filas cargadas", csv_file, table_name, row_count)
        except Exception as exc:
            logger.error("[ERROR] Error al cargar CSV '%s': %s", csv_file, exc)
            raise

    logger.info("Extracción de CSVs finalizada con éxito. %d tablas cargadas en raw.", len(results))
    return results

if __name__ == "__main__":
    extract_and_load_csvs()
