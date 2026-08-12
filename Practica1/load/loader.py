"""
load/loader.py
--------------
Módulo de carga del ETL.

Responsabilidades:
- Conectarse a SQL Server mediante SQLAlchemy + pyodbc.
- Crear la base de datos VuelosDW si no existe.
- Ejecutar el DDL del modelo estrella (idempotente con IF NOT EXISTS).
- Cargar primero las dimensiones, luego la tabla de hechos.
- Garantizar idempotencia: TRUNCATE + INSERT en cada ejecución.
- Loguear filas cargadas y cualquier error.
"""

import logging
from pathlib import Path
from typing import Optional

import pandas as pd
import pyodbc
import sqlalchemy as sa
from sqlalchemy import create_engine, text

from config import settings

logger = logging.getLogger(__name__)

# Orden de carga: dimensiones primero, luego hechos
LOAD_ORDER = [
    ("DimFecha",      "dim_fecha"),
    ("DimPasajero",   "dim_pasajero"),
    ("DimAerolinea",  "dim_aerolinea"),
    ("DimAeropuerto", "dim_aeropuerto"),
    ("DimClase",      "dim_clase"),
    ("DimEstado",     "dim_estado"),
    ("FactVuelos",    "fact_vuelos"),
]


# ---------------------------------------------------------------------------
# Conexión y creación de BD
# ---------------------------------------------------------------------------

def _create_database_if_not_exists() -> None:
    """
    Crea la base de datos VuelosDW en SQL Server si no existe.
    Se conecta a 'master' primero (sin autocommit de transacción implícita).
    """
    conn_str = settings.get_pyodbc_conn_str()
    try:
        with pyodbc.connect(conn_str, autocommit=True) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"IF DB_ID('{settings.DB_NAME}') IS NULL "
                f"CREATE DATABASE [{settings.DB_NAME}]"
            )
            logger.info("[LOAD] Base de datos '%s' lista.", settings.DB_NAME)
    except pyodbc.Error as exc:
        logger.error("[LOAD] Error al crear la base de datos: %s", exc)
        raise


def get_engine() -> sa.Engine:
    """
    Crea y devuelve un engine de SQLAlchemy para VuelosDW.
    """
    url = settings.get_sqlalchemy_url()
    engine = create_engine(url, fast_executemany=True)
    return engine


# ---------------------------------------------------------------------------
# Ejecución del DDL
# ---------------------------------------------------------------------------

def execute_ddl(engine: sa.Engine) -> None:
    """
    Lee y ejecuta el script DDL create_model.sql para crear las tablas
    del modelo estrella. El script usa IF NOT EXISTS / IF OBJECT_ID para
    ser idempotente.
    """
    ddl_path = settings.SQL_DDL_PATH
    if not ddl_path.exists():
        raise FileNotFoundError(f"[LOAD] DDL no encontrado: {ddl_path}")

    ddl_sql = ddl_path.read_text(encoding="utf-8")

    # SQL Server no soporta múltiples statements en un solo execute() con pyodbc.
    # Separar por el delimitador GO (mayúsculas o minúsculas).
    import re
    statements = re.split(r"^\s*GO\s*$", ddl_sql, flags=re.MULTILINE | re.IGNORECASE)

    with engine.begin() as conn:
        for stmt in statements:
            stmt = stmt.strip()
            if stmt:
                try:
                    conn.execute(text(stmt))
                except Exception as exc:
                    logger.error("[LOAD] Error ejecutando DDL statement: %s\n%s", exc, stmt[:200])
                    raise

    logger.info("[LOAD] DDL ejecutado correctamente.")


# ---------------------------------------------------------------------------
# Carga idempotente
# ---------------------------------------------------------------------------

def truncate_table(engine: sa.Engine, table_name: str) -> None:
    """
    Vacia una tabla. Usa DELETE en lugar de TRUNCATE para evitar problemas con las constraints FK.
    """
    with engine.begin() as conn:
        conn.execute(text(f"DELETE FROM [{table_name}]"))
    logger.info("[LOAD] Tabla %s vaciada.", table_name)


def load_table(
    df: pd.DataFrame,
    table_name: str,
    engine: sa.Engine,
    chunk_size: int = 1000,
) -> None:
    """
    Carga un DataFrame en la tabla SQL Server indicada usando pandas.to_sql.

    Parámetros
    ----------
    df : pd.DataFrame
    table_name : str
    engine : sqlalchemy.Engine
    chunk_size : int
        Número de filas por batch insert.
    """
    n_rows = len(df)
    logger.info("[LOAD] Cargando %d filas en %s...", n_rows, table_name)

    try:
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists="append",  # La tabla ya existe (creada por DDL)
            index=False,
            chunksize=chunk_size,
        )
        logger.info("[LOAD] %s → %d filas cargadas OK.", table_name, n_rows)
    except Exception as exc:
        logger.error("[LOAD] Error cargando %s: %s", table_name, exc)
        raise


# ---------------------------------------------------------------------------
# Punto de entrada principal
# ---------------------------------------------------------------------------

def load(tables: dict[str, pd.DataFrame]) -> None:
    """
    Orquesta la carga completa al modelo estrella en SQL Server.

    Parameters
    ----------
    tables : dict
        Diccionario con claves 'dim_fecha', 'dim_pasajero', etc. y
        valores pd.DataFrame (salida de standardizer.standardize()).
    """
    logger.info("[LOAD] Iniciando fase de carga en SQL Server...")

    # 1. Crear BD si no existe
    _create_database_if_not_exists()

    # 2. Crear engine hacia VuelosDW
    engine = get_engine()

    # 3. Ejecutar DDL
    execute_ddl(engine)

    # 3.5 Vaciamos las tablas en orden inverso (FactVuelos primero) para evitar errores de FK
    for sql_table, _ in reversed(LOAD_ORDER):
        try:
            truncate_table(engine, sql_table)
        except Exception as exc:
            logger.warning("[LOAD] No se pudo limpiar la tabla %s: %s", sql_table, exc)

    # 4. Cargar en orden (dimensiones → hechos)
    for sql_table, df_key in LOAD_ORDER:
        if df_key not in tables:
            logger.warning("[LOAD] No se encontró '%s' en el diccionario de tablas. Omitiendo.", df_key)
            continue

        df = tables[df_key]
        try:
            load_table(df, sql_table, engine)
        except Exception as exc:
            logger.error(
                "[LOAD] Fallo al cargar tabla %s. Abortando carga. Error: %s",
                sql_table,
                exc,
            )
            raise

    logger.info("[LOAD] Carga completa finalizada. %d tablas cargadas.", len(LOAD_ORDER))
    engine.dispose()
