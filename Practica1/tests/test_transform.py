"""
tests/test_transform.py
-----------------------
Pruebas unitarias para los módulos transform/cleaner.py
y transform/standardizer.py.

Ejecutar con: pytest tests/ -v
"""

import pandas as pd
import pytest
import sys
from pathlib import Path

# Añadir raíz del proyecto al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from transform.cleaner import clean, _parse_datetime, _clean_price, GENDER_MAP
from transform.standardizer import (
    build_dim_fecha,
    build_dim_pasajero,
    build_dim_aerolinea,
    build_dim_aeropuerto,
    build_dim_clase,
    build_dim_estado,
)


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_raw_df():
    """DataFrame crudo mínimo para probar el pipeline de limpieza."""
    return pd.DataFrame({
        "record_id": ["1", "2", "3", "4"],
        "airline_code": ["AA", "av", "FR", "DL"],
        "airline_name": ["American Airlines", "AVIANCA", "Ryanair", "Delta"],
        "flight_number": ["AA100", "AV200", "FR300", "DL400"],
        "origin_airport": ["MEX", "BOG", "MAD", "JFK"],
        "destination_airport": ["jfk", "MEX", "BOG", "lax"],
        "departure_datetime": [
            "20/01/2024 10:00",
            "15/06/2024 08:30",
            "01/01/2025 23:59",
            "invalid_date",        # ← debe rechazarse
        ],
        "arrival_datetime": [
            "20/01/2024 14:00",
            None,
            "02/01/2025 06:00",
            None,
        ],
        "duration_min": ["240", None, "360", "120"],
        "status": ["ON_TIME", "CANCELLED", "ON_TIME", "DELAYED"],
        "delay_min": ["0", None, "0", "45"],
        "aircraft_type": ["B738", "A320", "B737", "A321"],
        "cabin_class": ["ECONOMY", "BUSINESS", "ECONOMY", "FIRST"],
        "seat": ["12A", None, "3B", "1F"],
        "passenger_id": [
            "uuid-0001",
            "uuid-0002",
            "uuid-0003",
            "uuid-0004",
        ],
        "passenger_gender": ["M", "Femenino", "x", "Masculino"],
        "passenger_age": ["30", "25", None, "40"],
        "passenger_nationality": ["MX", "CO", "ES", None],
        "booking_datetime": [
            "10/01/2024 09:00",
            "01/06/2024 12:00",
            "15/12/2024 18:00",
            "03-15-2025 01:58 PM",
        ],
        "sales_channel": ["APP", "WEB", None, "AEROPUERTO"],
        "payment_method": ["TARJETA", "EFECTIVO", "TRANSFERENCIA", "PAYPAL"],
        "ticket_price": ["150,50", "200.00", "99.99", "300"],
        "currency": ["USD", "USD", "EUR", "USD"],
        "ticket_price_usd_est": ["150.50", "200.00", "107.50", "300.00"],
        "bags_total": ["1", "2", "0", "1"],
        "bags_checked": ["1", "1", "0", "0"],
    })


@pytest.fixture
def clean_df(sample_raw_df):
    """DataFrame limpio resultante de clean()."""
    df_clean, _ = clean(sample_raw_df)
    return df_clean


# ─── Tests: _parse_datetime ──────────────────────────────────────────────────

class TestParseDatetime:
    def test_format_dd_mm_yyyy_hhmm(self):
        result = _parse_datetime("20/01/2024 10:14")
        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 20

    def test_format_us_am_pm(self):
        result = _parse_datetime("03-15-2025 01:58 PM")
        assert result is not None
        assert result.year == 2025
        assert result.month == 3
        assert result.day == 15

    def test_invalid_returns_none(self):
        result = _parse_datetime("not_a_date")
        assert result is None

    def test_none_input(self):
        result = _parse_datetime(None)
        assert result is None

    def test_empty_string(self):
        result = _parse_datetime("")
        assert result is None


# ─── Tests: _clean_price ─────────────────────────────────────────────────────

class TestCleanPrice:
    def test_comma_decimal(self):
        assert _clean_price("77,60") == pytest.approx(77.60)

    def test_dot_decimal(self):
        assert _clean_price("138.8") == pytest.approx(138.8)

    def test_integer_string(self):
        assert _clean_price("300") == pytest.approx(300.0)

    def test_none_returns_none(self):
        assert _clean_price(None) is None

    def test_empty_returns_none(self):
        assert _clean_price("") is None


# ─── Tests: GENDER_MAP ───────────────────────────────────────────────────────

class TestGenderMap:
    def test_male_variants(self):
        for variant in ("m", "masculino", "male"):
            assert GENDER_MAP[variant] == "M", f"Fallo con variante: {variant}"

    def test_female_variants(self):
        for variant in ("f", "femenino", "female"):
            assert GENDER_MAP[variant] == "F", f"Fallo con variante: {variant}"

    def test_other_variants(self):
        for variant in ("x", "nobinario", "nb", "otro", "other"):
            assert GENDER_MAP[variant] == "OTRO", f"Fallo con variante: {variant}"


# ─── Tests: clean() ──────────────────────────────────────────────────────────

class TestClean:
    def test_returns_tuple(self, sample_raw_df):
        result = clean(sample_raw_df)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_invalid_date_row_rejected(self, sample_raw_df):
        """La fila con departure_datetime='invalid_date' debe ser rechazada."""
        df_clean, df_rejected = clean(sample_raw_df)
        assert any("departure_datetime" in str(r) for r in df_rejected.get("rejection_reason", []))

    def test_gender_homologation(self, clean_df):
        assert set(clean_df["passenger_gender"].unique()).issubset({"M", "F", "OTRO"})

    def test_airport_codes_uppercase(self, clean_df):
        assert all(c == c.upper() for c in clean_df["destination_airport"].dropna())
        assert all(c == c.upper() for c in clean_df["origin_airport"].dropna())

    def test_no_exact_duplicates(self, sample_raw_df):
        df_dup = pd.concat([sample_raw_df, sample_raw_df.iloc[:1]], ignore_index=True)
        df_clean, _ = clean(df_dup)
        # No debe haber duplicados exactos (record_id duplicado)
        assert df_clean["record_id"].duplicated().sum() == 0

    def test_rango_etario_column_exists(self, clean_df):
        assert "rango_etario" in clean_df.columns

    def test_cancelled_duration_filled(self, clean_df):
        cancelled = clean_df[clean_df["status"] == "CANCELLED"]
        assert cancelled["duration_min"].isna().sum() == 0


# ─── Tests: build_dim_fecha ──────────────────────────────────────────────────

class TestBuildDimFecha:
    def test_has_required_columns(self, clean_df):
        dim = build_dim_fecha(clean_df)
        required = {"id_fecha", "fecha", "dia", "mes", "anio", "trimestre",
                    "dia_semana", "nombre_dia", "nombre_mes", "es_fin_semana"}
        assert required.issubset(set(dim.columns))

    def test_no_duplicate_dates(self, clean_df):
        dim = build_dim_fecha(clean_df)
        assert dim["fecha"].duplicated().sum() == 0

    def test_surrogate_key_sequential(self, clean_df):
        dim = build_dim_fecha(clean_df)
        assert list(dim["id_fecha"]) == list(range(1, len(dim) + 1))


# ─── Tests: build_dim_pasajero ───────────────────────────────────────────────

class TestBuildDimPasajero:
    def test_unique_passengers(self, clean_df):
        dim = build_dim_pasajero(clean_df)
        assert dim["passenger_uuid"].duplicated().sum() == 0

    def test_gender_values_valid(self, clean_df):
        dim = build_dim_pasajero(clean_df)
        assert set(dim["genero"].unique()).issubset({"M", "F", "OTRO"})


# ─── Tests: build_dim_aerolinea ──────────────────────────────────────────────

class TestBuildDimAerolinea:
    def test_unique_iata(self, clean_df):
        dim = build_dim_aerolinea(clean_df)
        assert dim["codigo_iata"].duplicated().sum() == 0

    def test_has_nombre_aerolinea(self, clean_df):
        dim = build_dim_aerolinea(clean_df)
        assert "nombre_aerolinea" in dim.columns


# ─── Tests: build_dim_aeropuerto ─────────────────────────────────────────────

class TestBuildDimAeropuerto:
    def test_includes_origins_and_dests(self, clean_df):
        dim = build_dim_aeropuerto(clean_df)
        all_codes = (
            set(clean_df["origin_airport"].dropna().str.upper())
            | set(clean_df["destination_airport"].dropna().str.upper())
        )
        dim_codes = set(dim["codigo_iata"])
        assert all_codes.issubset(dim_codes)

    def test_no_duplicates(self, clean_df):
        dim = build_dim_aeropuerto(clean_df)
        assert dim["codigo_iata"].duplicated().sum() == 0
