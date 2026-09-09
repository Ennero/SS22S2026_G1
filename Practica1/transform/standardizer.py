"""
transform/standardizer.py
--------------------------
Módulo de estandarización y construcción del modelo dimensional.

Responsabilidades:
- Generar llaves subrogadas autoincrementales para cada dimensión.
- Construir cada DataFrame de dimensión (DimFecha, DimPasajero, DimAerolinea,
  DimAeropuerto, DimClase, DimEstado).
- Construir el DataFrame de la tabla de hechos (FactVuelos), resolviendo las
  FK contra cada dimensión.
- Validar integridad referencial antes de devolver los hechos.

Este módulo recibe el DataFrame LIMPIO de cleaner.py y devuelve un diccionario
de DataFrames listos para cargar en SQL Server.
"""

import logging
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _assign_surrogate_key(df: pd.DataFrame, key_col: str) -> pd.DataFrame:
    """
    Asigna una llave subrogada entera secuencial (1-based) al DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Tabla de dimensión ya deduplicada.
    key_col : str
        Nombre de la columna PK a generar.

    Returns
    -------
    pd.DataFrame con la columna key_col en la primera posición.
    """
    df = df.reset_index(drop=True).copy()
    df.insert(0, key_col, range(1, len(df) + 1))
    return df


# ---------------------------------------------------------------------------
# DimFecha
# ---------------------------------------------------------------------------

def build_dim_fecha(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construye DimFecha a partir de departure_datetime.

    Columnas resultantes:
        id_fecha, fecha, dia, mes, anio, trimestre, dia_semana,
        nombre_dia, nombre_mes, es_fin_semana
    """
    logger.info("[TRANSFORM/standardizer] Construyendo DimFecha...")
    dates = df["departure_datetime"].dropna().dt.normalize().unique()
    dim = pd.DataFrame({"fecha": pd.DatetimeIndex(dates)})
    dim = dim.drop_duplicates(subset=["fecha"]).sort_values("fecha")

    dim["dia"] = dim["fecha"].dt.day.astype(int)
    dim["mes"] = dim["fecha"].dt.month.astype(int)
    dim["anio"] = dim["fecha"].dt.year.astype(int)
    dim["trimestre"] = dim["fecha"].dt.quarter.astype(int)
    dim["dia_semana"] = dim["fecha"].dt.dayofweek.astype(int)  # 0=Lunes
    dim["nombre_dia"] = dim["fecha"].dt.day_name()
    dim["nombre_mes"] = dim["fecha"].dt.month_name()
    dim["es_fin_semana"] = (dim["dia_semana"] >= 5).astype(int)

    dim = _assign_surrogate_key(dim, "id_fecha")
    logger.info("[TRANSFORM/standardizer] DimFecha: %d filas", len(dim))
    return dim


# ---------------------------------------------------------------------------
# DimPasajero
# ---------------------------------------------------------------------------

def build_dim_pasajero(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construye DimPasajero con un registro único por passenger_id (UUID).

    Columnas resultantes:
        id_pasajero, passenger_uuid, genero, edad, rango_etario, nacionalidad
    """
    logger.info("[TRANSFORM/standardizer] Construyendo DimPasajero...")
    cols = ["passenger_id", "passenger_gender", "passenger_age",
            "rango_etario", "passenger_nationality"]
    dim = (
        df[cols]
        .drop_duplicates(subset=["passenger_id"])
        .copy()
    )
    dim = dim.rename(columns={
        "passenger_id": "passenger_uuid",
        "passenger_gender": "genero",
        "passenger_age": "edad",
        "passenger_nationality": "nacionalidad",
    })
    dim["edad"] = dim["edad"].astype(int)
    dim = _assign_surrogate_key(dim, "id_pasajero")
    logger.info("[TRANSFORM/standardizer] DimPasajero: %d filas", len(dim))
    return dim


# ---------------------------------------------------------------------------
# DimAerolinea
# ---------------------------------------------------------------------------

def build_dim_aerolinea(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construye DimAerolinea con un registro único por airline_code (IATA).

    Columnas resultantes:
        id_aerolinea, codigo_iata, nombre_aerolinea
    """
    logger.info("[TRANSFORM/standardizer] Construyendo DimAerolinea...")
    dim = (
        df[["airline_code", "airline_name"]]
        .drop_duplicates(subset=["airline_code"])
        .copy()
    )
    dim = dim.rename(columns={
        "airline_code": "codigo_iata",
        "airline_name": "nombre_aerolinea",
    })
    dim = _assign_surrogate_key(dim, "id_aerolinea")
    logger.info("[TRANSFORM/standardizer] DimAerolinea: %d filas", len(dim))
    return dim


# ---------------------------------------------------------------------------
# DimAeropuerto
# ---------------------------------------------------------------------------

AIRPORT_METADATA: dict[str, tuple[str, str, str]] = {
    "BCN": ("Aeropuerto Josep Tarradellas Barcelona-El Prat", "Barcelona", "España"),
    "BOG": ("Aeropuerto Internacional El Dorado", "Bogotá", "Colombia"),
    "CUN": ("Aeropuerto Internacional de Cancún", "Cancún", "México"),
    "GUA": ("Aeropuerto Internacional La Aurora", "Ciudad de Guatemala", "Guatemala"),
    "HAV": ("Aeropuerto Internacional José Martí", "La Habana", "Cuba"),
    "JFK": ("Aeropuerto Internacional John F. Kennedy", "Nueva York", "Estados Unidos"),
    "LAX": ("Aeropuerto Internacional de Los Ángeles", "Los Ángeles", "Estados Unidos"),
    "LIM": ("Aeropuerto Internacional Jorge Chávez", "Lima", "Perú"),
    "MAD": ("Aeropuerto Adolfo Suárez Madrid-Barajas", "Madrid", "España"),
    "MEX": ("Aeropuerto Internacional Benito Juárez", "Ciudad de México", "México"),
    "MIA": ("Aeropuerto Internacional de Miami", "Miami", "Estados Unidos"),
    "PTY": ("Aeropuerto Internacional de Tocumen", "Ciudad de Panamá", "Panamá"),
    "SAL": ("Aeropuerto Internacional San Óscar Arnulfo Romero", "San Salvador", "El Salvador"),
    "SAP": ("Aeropuerto Internacional Ramón Villeda Morales", "San Pedro Sula", "Honduras"),
    "SJO": ("Aeropuerto Internacional Juan Santamaría", "San José", "Costa Rica"),
}


def build_dim_aeropuerto(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construye DimAeropuerto enriquecida con nombre, ciudad y país
    a partir de los códigos IATA presentes en el dataset.

    Columnas resultantes:
        id_aeropuerto, codigo_iata, nombre_aeropuerto, ciudad, pais
    """
    logger.info("[TRANSFORM/standardizer] Construyendo DimAeropuerto...")
    origins = df[["origin_airport"]].rename(columns={"origin_airport": "codigo_iata"})
    dests = df[["destination_airport"]].rename(columns={"destination_airport": "codigo_iata"})
    dim = (
        pd.concat([origins, dests], ignore_index=True)
        .drop_duplicates()
        .dropna()
        .sort_values("codigo_iata")
        .reset_index(drop=True)
    )

    dim["nombre_aeropuerto"] = dim["codigo_iata"].map(
        lambda x: AIRPORT_METADATA.get(x, (f"Aeropuerto {x}", "Desconocido", "Desconocido"))[0]
    )
    dim["ciudad"] = dim["codigo_iata"].map(
        lambda x: AIRPORT_METADATA.get(x, (f"Aeropuerto {x}", "Desconocido", "Desconocido"))[1]
    )
    dim["pais"] = dim["codigo_iata"].map(
        lambda x: AIRPORT_METADATA.get(x, (f"Aeropuerto {x}", "Desconocido", "Desconocido"))[2]
    )

    dim = _assign_surrogate_key(dim, "id_aeropuerto")
    logger.info("[TRANSFORM/standardizer] DimAeropuerto: %d filas", len(dim))
    return dim


# ---------------------------------------------------------------------------
# DimClase
# ---------------------------------------------------------------------------

def build_dim_clase(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construye DimClase combinando clase de cabina y tipo de aeronave.

    Columnas resultantes:
        id_clase, clase_cabina, tipo_aeronave
    """
    logger.info("[TRANSFORM/standardizer] Construyendo DimClase...")
    dim = (
        df[["cabin_class", "aircraft_type"]]
        .drop_duplicates()
        .dropna(subset=["cabin_class"])
        .sort_values(["cabin_class", "aircraft_type"])
        .reset_index(drop=True)
    )
    dim = dim.rename(columns={
        "cabin_class": "clase_cabina",
        "aircraft_type": "tipo_aeronave",
    })
    dim = _assign_surrogate_key(dim, "id_clase")
    logger.info("[TRANSFORM/standardizer] DimClase: %d filas", len(dim))
    return dim


# ---------------------------------------------------------------------------
# DimEstado
# ---------------------------------------------------------------------------

def build_dim_estado(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construye DimEstado a partir de los valores únicos de status.

    Columnas resultantes:
        id_estado, estado_vuelo, descripcion_estado
    """
    logger.info("[TRANSFORM/standardizer] Construyendo DimEstado...")
    status_descriptions = {
        "ON_TIME": "Vuelo a tiempo",
        "CANCELLED": "Vuelo cancelado",
        "DELAYED": "Vuelo con retraso",
        "DIVERTED": "Vuelo desviado",
    }
    estados = df["status"].dropna().unique()
    dim = pd.DataFrame({
        "estado_vuelo": sorted(estados),
    })
    dim["descripcion_estado"] = dim["estado_vuelo"].map(
        lambda x: status_descriptions.get(x, x)
    )
    dim = _assign_surrogate_key(dim, "id_estado")
    logger.info("[TRANSFORM/standardizer] DimEstado: %d filas", len(dim))
    return dim


# ---------------------------------------------------------------------------
# FactVuelos
# ---------------------------------------------------------------------------

def build_fact_vuelos(
    df: pd.DataFrame,
    dim_fecha: pd.DataFrame,
    dim_pasajero: pd.DataFrame,
    dim_aerolinea: pd.DataFrame,
    dim_aeropuerto: pd.DataFrame,
    dim_clase: pd.DataFrame,
    dim_estado: pd.DataFrame,
) -> pd.DataFrame:
    """
    Construye FactVuelos resolviendo FK contra cada dimensión.

    Parámetros
    ----------
    df : pd.DataFrame
        Dataset limpio de cleaner.py.
    dim_* : pd.DataFrame
        DataFrames de cada dimensión (ya con llaves subrogadas).

    Devuelve
    --------
    pd.DataFrame con las columnas de FactVuelos, sin id_vuelo
    (ese es IDENTITY en SQL Server).
    """
    logger.info("[TRANSFORM/standardizer] Construyendo FactVuelos...")
    fact = df.copy()

    # -- Resolver id_fecha --
    fecha_solo = fact["departure_datetime"].dt.normalize()
    dim_fecha_lookup = dim_fecha[["id_fecha", "fecha"]].copy()
    dim_fecha_lookup["fecha"] = pd.to_datetime(dim_fecha_lookup["fecha"])
    fact = fact.merge(
        dim_fecha_lookup.rename(columns={"fecha": "_fecha_join"}),
        left_on=fecha_solo,
        right_on="_fecha_join",
        how="left",
    ).drop(columns=["_fecha_join", "key_0"], errors="ignore")

    # -- Resolver id_pasajero --
    dim_pas_lookup = dim_pasajero[["id_pasajero", "passenger_uuid"]]
    fact = fact.merge(
        dim_pas_lookup,
        left_on="passenger_id",
        right_on="passenger_uuid",
        how="left",
    )

    # -- Resolver id_aerolinea --
    dim_aero_lookup = dim_aerolinea[["id_aerolinea", "codigo_iata"]]
    fact = fact.merge(
        dim_aero_lookup,
        left_on="airline_code",
        right_on="codigo_iata",
        how="left",
    )

    # -- Resolver id_origen --
    dim_aeropuerto_lookup = dim_aeropuerto[["id_aeropuerto", "codigo_iata"]]
    fact = fact.merge(
        dim_aeropuerto_lookup.rename(columns={"id_aeropuerto": "id_origen", "codigo_iata": "_orig_iata"}),
        left_on="origin_airport",
        right_on="_orig_iata",
        how="left",
    ).drop(columns=["_orig_iata"], errors="ignore")

    # -- Resolver id_destino --
    fact = fact.merge(
        dim_aeropuerto_lookup.rename(columns={"id_aeropuerto": "id_destino", "codigo_iata": "_dest_iata"}),
        left_on="destination_airport",
        right_on="_dest_iata",
        how="left",
    ).drop(columns=["_dest_iata"], errors="ignore")

    # -- Resolver id_clase --
    dim_clase_lookup = dim_clase[["id_clase", "clase_cabina", "tipo_aeronave"]]
    fact = fact.merge(
        dim_clase_lookup,
        left_on=["cabin_class", "aircraft_type"],
        right_on=["clase_cabina", "tipo_aeronave"],
        how="left",
    )

    # -- Resolver id_estado --
    dim_estado_lookup = dim_estado[["id_estado", "estado_vuelo"]]
    fact = fact.merge(
        dim_estado_lookup,
        left_on="status",
        right_on="estado_vuelo",
        how="left",
    )

    # -- Seleccionar y renombrar columnas finales --
    selected_cols = [
        "id_fecha",
        "id_pasajero",
        "id_aerolinea",
        "id_origen",
        "id_destino",
        "id_clase",
        "id_estado",
        "flight_number",
        "duration_min",
        "ticket_price_usd_est",
        "delay_min",
        "bags_total",
        "sales_channel",
        "payment_method",
    ]
    if "dias_anticipacion" in fact.columns:
        selected_cols.append("dias_anticipacion")

    fact_final = fact[selected_cols].rename(columns={
        "flight_number": "numero_vuelo",
        "duration_min": "duracion_minutos",
        "ticket_price_usd_est": "precio_usd",
        "delay_min": "retraso_minutos",
        "bags_total": "total_equipaje",
        "sales_channel": "canal_venta",
        "payment_method": "metodo_pago",
    }).copy()

    if "dias_anticipacion" not in fact_final.columns:
        fact_final["dias_anticipacion"] = 0

    # -- Convertir FK a Int (nullable) --
    fk_cols = ["id_fecha", "id_pasajero", "id_aerolinea", "id_origen", "id_destino", "id_clase", "id_estado"]
    for col in fk_cols:
        fact_final[col] = pd.to_numeric(fact_final[col], errors="coerce")

    # -- Validar integridad referencial --
    n_total = len(fact_final)
    mask_fk_null = fact_final[fk_cols].isnull().any(axis=1)
    n_invalid_fk = mask_fk_null.sum()
    if n_invalid_fk > 0:
        logger.warning(
            "[TRANSFORM/standardizer] %d filas con FK nulas (se excluyen de FactVuelos).",
            n_invalid_fk,
        )
        fact_final = fact_final[~mask_fk_null]

    # Convertir FK a int64 tras filtrar nulos
    for col in fk_cols:
        fact_final[col] = fact_final[col].astype("int64")

    fact_final["duracion_minutos"] = fact_final["duracion_minutos"].fillna(0).astype(int)
    fact_final["retraso_minutos"] = fact_final["retraso_minutos"].fillna(0).astype(int)
    fact_final["total_equipaje"] = fact_final["total_equipaje"].fillna(0).astype(int)
    fact_final["dias_anticipacion"] = fact_final["dias_anticipacion"].fillna(0).astype(int)

    logger.info(
        "[TRANSFORM/standardizer] FactVuelos: %d filas (%d excluidas por FK nulas)",
        len(fact_final),
        n_invalid_fk,
    )
    return fact_final


# ---------------------------------------------------------------------------
# Punto de entrada principal
# ---------------------------------------------------------------------------

def standardize(df_clean: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """
    Orquesta la construcción de todas las tablas del modelo estrella.

    Parameters
    ----------
    df_clean : pd.DataFrame
        DataFrame limpio de cleaner.py.

    Returns
    -------
    dict con claves: 'dim_fecha', 'dim_pasajero', 'dim_aerolinea',
                     'dim_aeropuerto', 'dim_clase', 'dim_estado', 'fact_vuelos'
    """
    dim_fecha = build_dim_fecha(df_clean)
    dim_pasajero = build_dim_pasajero(df_clean)
    dim_aerolinea = build_dim_aerolinea(df_clean)
    dim_aeropuerto = build_dim_aeropuerto(df_clean)
    dim_clase = build_dim_clase(df_clean)
    dim_estado = build_dim_estado(df_clean)

    fact_vuelos = build_fact_vuelos(
        df_clean,
        dim_fecha,
        dim_pasajero,
        dim_aerolinea,
        dim_aeropuerto,
        dim_clase,
        dim_estado,
    )

    return {
        "dim_fecha": dim_fecha,
        "dim_pasajero": dim_pasajero,
        "dim_aerolinea": dim_aerolinea,
        "dim_aeropuerto": dim_aeropuerto,
        "dim_clase": dim_clase,
        "dim_estado": dim_estado,
        "fact_vuelos": fact_vuelos,
    }
