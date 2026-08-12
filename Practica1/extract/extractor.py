"""
extract/extractor.py
--------------------
Módulo de extracción del ETL.

Responsabilidades:
- Leer el dataset crudo (CSV) y validar que tenga el esquema mínimo esperado.
- Guardar un snapshot en data/raw/ para trazabilidad.
- Loguear filas leídas, tamaño del archivo y cualquier anomalía inicial.

El módulo NO realiza ninguna transformación: entrega el DataFrame tal cual
viene del archivo fuente (datos crudos).
"""

import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

from config import settings

logger = logging.getLogger(__name__)

# Columnas mínimas que deben existir en el CSV fuente
REQUIRED_COLUMNS = {
    "record_id",
    "airline_code",
    "airline_name",
    "flight_number",
    "origin_airport",
    "destination_airport",
    "departure_datetime",
    "status",
    "passenger_id",
    "passenger_gender",
    "ticket_price_usd_est",
}


def extract_csv(path: Optional[Path] = None) -> pd.DataFrame:
    """
    Lee el dataset de vuelos crudos desde un archivo CSV.

    Parameters
    ----------
    path : Path, optional
        Ruta al CSV. Si es None, usa RAW_DATA_PATH de settings.

    Returns
    -------
    pd.DataFrame
        DataFrame con el contenido crudo del CSV.

    Raises
    ------
    FileNotFoundError
        Si el archivo no existe en la ruta indicada.
    ValueError
        Si el CSV no contiene las columnas mínimas requeridas.
    """
    source_path = Path(path) if path else settings.RAW_DATA_PATH

    logger.info("[EXTRACT] Iniciando lectura de fuente: %s", source_path)

    if not source_path.exists():
        msg = f"[EXTRACT] Archivo no encontrado: {source_path}"
        logger.error(msg)
        raise FileNotFoundError(msg)

    file_size_kb = source_path.stat().st_size / 1024
    logger.info("[EXTRACT] Tamaño del archivo: %.1f KB", file_size_kb)

    try:
        # dtype=str preserva todos los valores tal cual para validar en transform
        df = pd.read_csv(source_path, dtype=str, encoding="utf-8")
    except UnicodeDecodeError:
        logger.warning(
            "[EXTRACT] Error de encoding UTF-8. Reintentando con latin-1..."
        )
        df = pd.read_csv(source_path, dtype=str, encoding="latin-1")

    logger.info(
        "[EXTRACT] Archivo leído: %d filas × %d columnas", len(df), len(df.columns)
    )

    # Validar esquema mínimo
    missing_cols = REQUIRED_COLUMNS - set(df.columns)
    if missing_cols:
        msg = f"[EXTRACT] Columnas requeridas faltantes: {missing_cols}"
        logger.error(msg)
        raise ValueError(msg)

    logger.info("[EXTRACT] Esquema mínimo validado OK.")

    # Guardar snapshot en data/raw/
    _save_raw_snapshot(df, source_path)

    return df


def _save_raw_snapshot(df: pd.DataFrame, source_path: Path) -> None:
    """
    Guarda una copia del dataset crudo en data/raw/ con timestamp
    para trazabilidad.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_name = f"{source_path.stem}_{timestamp}.csv"
    snapshot_path = settings.RAW_SNAPSHOT_DIR / snapshot_name

    try:
        df.to_csv(snapshot_path, index=False, encoding="utf-8")
        logger.info("[EXTRACT] Snapshot guardado en: %s", snapshot_path)
    except Exception as exc:
        # El snapshot es opcional: loguear pero no interrumpir el proceso
        logger.warning("[EXTRACT] No se pudo guardar snapshot: %s", exc)
