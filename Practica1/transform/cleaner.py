"""
transform/cleaner.py
--------------------
Módulo de limpieza general del ETL.

Responsabilidades:
- Eliminar duplicados exactos.
- Normalizar texto en campos categóricos (trim, uppercase donde corresponda).
- Homologar valores equivalentes de género (M/Masculino/male → 'M', etc.).
- Parsear fechas en múltiples formatos conocidos a datetime.
- Convertir tipos numéricos (precio, duración, edad).
- Registrar en log cada fila rechazada con su motivo.
- Retornar el DataFrame limpio y el DataFrame de rechazados.

Este módulo NO crea dimensiones ni llaves subrogadas; eso lo hace standardizer.py.
"""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd

from config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Mapeo de normalización de género
# ---------------------------------------------------------------------------
GENDER_MAP: dict[str, str] = {
    "m": "M",
    "masculino": "M",
    "male": "M",
    "f": "F",
    "femenino": "F",
    "female": "F",
    "x": "OTRO",
    "nobinario": "OTRO",
    "no_binario": "OTRO",
    "nb": "OTRO",
    "otro": "OTRO",
    "other": "OTRO",
}

# ---------------------------------------------------------------------------
# Formatos de fecha aceptados (en orden de prioridad)
# ---------------------------------------------------------------------------
DATE_FORMATS = [
    "%d/%m/%Y %H:%M",       # 20/01/2024 10:14  ← formato predominante
    "%m-%d-%Y %I:%M %p",    # 03-15-2025 01:58 PM
    "%Y-%m-%d %H:%M:%S",    # 2024-01-20 10:14:00
    "%Y-%m-%dT%H:%M:%S",    # ISO 8601
    "%d/%m/%Y",             # solo fecha
    "%m/%d/%Y",
    "%Y-%m-%d",
]


def _parse_datetime(value: str) -> pd.Timestamp | None:
    """
    Intenta parsear un string de fecha usando los formatos conocidos.
    Devuelve None si ninguno funciona.
    """
    if pd.isna(value) or str(value).strip() == "":
        return None
    value = str(value).strip()
    for fmt in DATE_FORMATS:
        try:
            return pd.Timestamp(datetime.strptime(value, fmt))
        except ValueError:
            continue
    # Fallback: pandas inferencia automática
    try:
        return pd.Timestamp(pd.to_datetime(value, infer_datetime_format=True))
    except Exception:
        return None


def _clean_price(value: str) -> float | None:
    """
    Limpia un string de precio que puede usar coma como separador decimal
    (ej. '77,60') o punto (ej. '77.60').
    """
    if pd.isna(value) or str(value).strip() == "":
        return None
    cleaned = str(value).strip().replace(",", ".")
    # Eliminar caracteres no numéricos excepto punto y signo menos
    cleaned = re.sub(r"[^\d.\-]", "", cleaned)
    try:
        return float(cleaned)
    except ValueError:
        return None


def clean(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Aplica todas las reglas de limpieza al DataFrame crudo.

    Parameters
    ----------
    df : pd.DataFrame
        Dataset crudo tal como salió del módulo extract.

    Returns
    -------
    df_clean : pd.DataFrame
        DataFrame limpio, listo para standardizer.
    df_rejected : pd.DataFrame
        Filas rechazadas con columna 'rejection_reason'.
    """
    logger.info("[TRANSFORM/clean] Inicio. Filas entrantes: %d", len(df))

    rejected_records: list[dict] = []

    # --- 1. Copia de trabajo ---
    df = df.copy()

    # --- 2. Eliminar duplicados exactos ---
    n_before = len(df)
    df = df.drop_duplicates()
    n_dup = n_before - len(df)
    if n_dup > 0:
        logger.warning("[TRANSFORM/clean] Duplicados exactos eliminados: %d", n_dup)

    # --- 3. Normalizar texto en columnas clave ---
    text_cols_upper = [
        "airline_code",
        "origin_airport",
        "destination_airport",
        "status",
        "cabin_class",
        "sales_channel",
        "payment_method",
        "currency",
        "passenger_nationality",
    ]
    for col in text_cols_upper:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper()
            df[col] = df[col].replace({"NAN": np.nan, "NONE": np.nan, "": np.nan})

    text_cols_title = ["airline_name", "passenger_nationality"]
    # airline_name: homologar a Title Case para unificar variantes
    if "airline_name" in df.columns:
        df["airline_name"] = (
            df["airline_name"].astype(str).str.strip().str.title()
        )
        # Normalizar variantes conocidas
        airline_name_map = {
            "Aeromexico": "Aeromexico",
            "American Airlines": "American Airlines",
            "Avianca": "Avianca",
            "British Airways": "British Airways",
            "Copa Airlines": "Copa Airlines",
            "Delta": "Delta",
            "Iberia": "Iberia",
            "Jetblue": "JetBlue",
            "Latam": "LATAM",
            "Ryanair": "Ryanair",
            "Southwest": "Southwest",
            "United": "United",
        }
        df["airline_name"] = df["airline_name"].map(
            lambda x: airline_name_map.get(x, x)
        )

    # --- 4. Homologar género ---
    if "passenger_gender" in df.columns:
        df["passenger_gender"] = (
            df["passenger_gender"]
            .astype(str)
            .str.strip()
            .str.lower()
            .map(lambda x: GENDER_MAP.get(x, "OTRO"))
        )
        logger.info(
            "[TRANSFORM/clean] Distribución de género tras homologación:\n%s",
            df["passenger_gender"].value_counts().to_string(),
        )

    # --- 5. Parsear fechas ---
    for date_col in ["departure_datetime", "arrival_datetime", "booking_datetime"]:
        if date_col in df.columns:
            df[date_col] = df[date_col].apply(_parse_datetime)
            n_invalid = df[date_col].isna().sum()
            logger.info(
                "[TRANSFORM/clean] %s → %d nulos tras parseo", date_col, n_invalid
            )

    # --- 6. Convertir numéricos ---
    if "ticket_price" in df.columns:
        df["ticket_price_clean"] = df["ticket_price"].apply(_clean_price)

    if "ticket_price_usd_est" in df.columns:
        df["ticket_price_usd_est"] = pd.to_numeric(
            df["ticket_price_usd_est"], errors="coerce"
        )

    for num_col in ["duration_min", "delay_min", "passenger_age", "bags_total", "bags_checked"]:
        if num_col in df.columns:
            df[num_col] = pd.to_numeric(df[num_col], errors="coerce")

    # --- 7. Validar y rechazar filas críticas ---
    mask_no_departure = df["departure_datetime"].isna()
    _reject(df, rejected_records, mask_no_departure, "departure_datetime inválida o ausente")

    mask_no_passenger = df["passenger_id"].isna() | (df["passenger_id"].astype(str).str.strip() == "")
    _reject(df, rejected_records, mask_no_passenger & ~mask_no_departure, "passenger_id ausente")

    mask_no_origin = df["origin_airport"].isna() | (df["origin_airport"].astype(str).str.strip().isin(["", "NAN"]))
    _reject(df, rejected_records, mask_no_origin & ~mask_no_departure & ~mask_no_passenger, "origin_airport ausente")

    mask_no_dest = df["destination_airport"].isna() | (df["destination_airport"].astype(str).str.strip().isin(["", "NAN"]))
    _reject(df, rejected_records, mask_no_dest & ~mask_no_departure & ~mask_no_passenger & ~mask_no_origin, "destination_airport ausente")

    # Precio USD obligatorio (es la métrica principal)
    mask_no_price = df["ticket_price_usd_est"].isna()
    _reject(df, rejected_records, mask_no_price & ~mask_no_departure & ~mask_no_passenger & ~mask_no_origin & ~mask_no_dest, "ticket_price_usd_est ausente")

    # Construir máscara acumulada de rechazos
    all_rejected_masks = (
        mask_no_departure
        | mask_no_passenger
        | mask_no_origin
        | mask_no_dest
        | mask_no_price
    )
    df_clean = df[~all_rejected_masks].copy()
    df_rejected = pd.DataFrame(rejected_records)

    # --- 8. Rellenar nulos no críticos en vuelos cancelados/desviados ---
    cancelled_mask = df_clean["status"].isin(["CANCELLED", "DIVERTED"])
    df_clean.loc[cancelled_mask, "duration_min"] = df_clean.loc[
        cancelled_mask, "duration_min"
    ].fillna(0)
    df_clean.loc[cancelled_mask, "delay_min"] = df_clean.loc[
        cancelled_mask, "delay_min"
    ].fillna(0)

    # Rellenar delay_min = 0 para ON_TIME
    on_time_mask = df_clean["status"] == "ON_TIME"
    df_clean.loc[on_time_mask, "delay_min"] = df_clean.loc[
        on_time_mask, "delay_min"
    ].fillna(0)

    # Edad: rellenar con mediana
    median_age = df_clean["passenger_age"].median()
    df_clean["passenger_age"] = df_clean["passenger_age"].fillna(median_age).astype(int)

    # Nacionalidad desconocida
    df_clean["passenger_nationality"] = df_clean["passenger_nationality"].fillna("DESCONOCIDO")

    # Canal de venta desconocido
    df_clean["sales_channel"] = df_clean["sales_channel"].fillna("DESCONOCIDO")

    # --- 9. Añadir rango etario calculado (incluye edad 0 para infantes) ---
    df_clean["rango_etario"] = pd.cut(
        df_clean["passenger_age"],
        bins=[-1, 17, 25, 35, 50, 65, 120],
        labels=["<18", "18-25", "26-35", "36-50", "51-65", "65+"],
        right=True,
    ).astype(str)

    # --- 9b. Días de anticipación de reserva ---
    if "departure_datetime" in df_clean.columns and "booking_datetime" in df_clean.columns:
        diff_days = (
            df_clean["departure_datetime"] - df_clean["booking_datetime"]
        ).dt.total_seconds() / 86400.0
        df_clean["dias_anticipacion"] = diff_days.fillna(0).clip(lower=0).round().astype(int)
    else:
        df_clean["dias_anticipacion"] = 0

    # --- 10. Guardar CSV procesado ---
    _save_processed(df_clean)

    logger.info(
        "[TRANSFORM/clean] Fin. Filas limpias: %d | Rechazadas: %d",
        len(df_clean),
        len(df_rejected),
    )

    return df_clean, df_rejected


def _reject(
    df: pd.DataFrame,
    rejected_list: list,
    mask: pd.Series,
    reason: str,
) -> None:
    """Añade a la lista de rechazados las filas que cumplan la máscara."""
    subset = df[mask].copy()
    if len(subset) > 0:
        subset["rejection_reason"] = reason
        rejected_list.extend(subset.to_dict(orient="records"))
        logger.warning(
            "[TRANSFORM/clean] Rechazadas %d filas — motivo: %s", len(subset), reason
        )


def _save_processed(df: pd.DataFrame) -> None:
    """Guarda el DataFrame limpio en data/processed/ para debug."""
    try:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = settings.PROCESSED_DIR / f"vuelos_clean_{ts}.csv"
        df.to_csv(out_path, index=False, encoding="utf-8")
        logger.info("[TRANSFORM/clean] DataFrame limpio guardado en: %s", out_path)
    except Exception as exc:
        logger.warning("[TRANSFORM/clean] No se pudo guardar archivo procesado: %s", exc)
