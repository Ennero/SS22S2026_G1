"""
main.py
-------
Orquestador principal del pipeline ETL.

Uso:
    python main.py

El script ejecuta las tres fases en orden:
    1. EXTRACT  — Lee el CSV crudo.
    2. TRANSFORM — Limpia y construye el modelo dimensional.
    3. LOAD     — Carga a SQL Server.

Logging:
    - Consola: nivel INFO.
    - Archivo: logs/etl_YYYYMMDD.log — nivel DEBUG.

Idempotencia:
    Ejecutar el script más de una vez no duplica datos (TRUNCATE + INSERT).

Salida de error:
    Si cualquier fase falla, el proceso termina con sys.exit(1) y el error
    queda registrado en el log con contexto completo.
"""

import logging
import sys
import traceback
from datetime import datetime
from pathlib import Path

# ── Configurar logging antes de importar módulos propios ──────────────────
from config import settings

_LOG_FILE = settings.LOGS_DIR / f"etl_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)-8s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(_LOG_FILE, encoding="utf-8"),
    ],
)

logger = logging.getLogger("main")

# ── Importar módulos del pipeline ─────────────────────────────────────────
from extract.extractor import extract_csv
from transform.cleaner import clean
from transform.standardizer import standardize
from load.loader import load


def run_etl() -> None:
    """
    Ejecuta el pipeline ETL completo: Extract → Transform → Load.
    """
    start_time = datetime.now()
    logger.info("=" * 60)
    logger.info("ETL VUELOS — Inicio: %s", start_time.strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("=" * 60)

    # ------------------------------------------------------------------
    # FASE 1: EXTRACT
    # ------------------------------------------------------------------
    logger.info("──── FASE 1: EXTRACT ────")
    try:
        df_raw = extract_csv()
        logger.info("[EXTRACT] ✓ %d filas extraídas.", len(df_raw))
    except Exception as exc:
        logger.error("[EXTRACT] ✗ Error fatal:\n%s", traceback.format_exc())
        sys.exit(1)

    # ------------------------------------------------------------------
    # FASE 2: TRANSFORM
    # ------------------------------------------------------------------
    logger.info("──── FASE 2: TRANSFORM ────")
    try:
        # 2a. Limpieza
        df_clean, df_rejected = clean(df_raw)
        logger.info(
            "[TRANSFORM/clean] ✓ Limpias: %d | Rechazadas: %d",
            len(df_clean),
            len(df_rejected),
        )
        if len(df_rejected) > 0:
            rejected_path = settings.PROCESSED_DIR / f"rechazadas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df_rejected.to_csv(rejected_path, index=False, encoding="utf-8")
            logger.info("[TRANSFORM/clean] Rechazadas guardadas en: %s", rejected_path)

        # 2b. Estandarización / construcción del modelo dimensional
        tables = standardize(df_clean)
        for name, df_dim in tables.items():
            logger.info("[TRANSFORM/std] ✓ %-20s → %d filas", name, len(df_dim))

    except Exception as exc:
        logger.error("[TRANSFORM] ✗ Error fatal:\n%s", traceback.format_exc())
        sys.exit(1)

    # ------------------------------------------------------------------
    # FASE 3: LOAD
    # ------------------------------------------------------------------
    logger.info("──── FASE 3: LOAD ────")
    try:
        load(tables)
        logger.info("[LOAD] ✓ Carga completada en SQL Server.")
    except Exception as exc:
        logger.error("[LOAD] ✗ Error fatal:\n%s", traceback.format_exc())
        sys.exit(1)

    # ------------------------------------------------------------------
    # Resumen final
    # ------------------------------------------------------------------
    elapsed = datetime.now() - start_time
    logger.info("=" * 60)
    logger.info(
        "ETL VUELOS — FIN. Duración total: %s",
        str(elapsed).split(".")[0],
    )
    logger.info("=" * 60)


if __name__ == "__main__":
    run_etl()
