"""
elt/quality_checker.py
Validador de calidad y consistencia para el esquema 'raw' y fuentes de datos.
"""

import logging
from sqlalchemy import text
from elt.db import get_engine

logger = logging.getLogger("elt.quality_checker")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

EXPECTED_RAW_TABLES = [
    "sucursal",
    "categoria",
    "marca",
    "producto",
    "cliente",
    "venta",
    "venta_detalle",
    "inventario_bodega",
    "proveedores_precios",
    "promociones",
    "metas_ventas",
    "devoluciones",
]

def check_raw_tables_populated() -> dict[str, int]:
    """Verifica que todas las tablas del esquema raw existan y contengan registros."""
    engine = get_engine()
    results = {}
    logger.info("Validando tablas en el esquema 'raw'...")

    with engine.connect() as conn:
        for table in EXPECTED_RAW_TABLES:
            try:
                query = text(f"SELECT COUNT(*) FROM raw.{table};")
                count = conn.execute(query).scalar()
                results[table] = count
                if count == 0:
                    logger.warning("ALERTA: La tabla raw.%s existe pero tiene 0 registros.", table)
                else:
                    logger.info("[OK] raw.%s: %d registros confirmados", table, count)
            except Exception as exc:
                logger.error("[ERROR] Error al verificar raw.%s: %s", table, exc)
                results[table] = -1

    return results

def evaluate_quality_rules() -> dict[str, str]:
    """
    Evalúa reglas de calidad inspiradas en 'casos_calidad_opcionales.csv':
    - Precios no negativos
    - Descuentos entre 0 y 1
    - Cantidades mayores a 0
    - Fechas válidas
    """
    engine = get_engine()
    checks = {}
    logger.info("Ejecutando auditoría de reglas de calidad sobre datos raw...")

    queries = {
        "precios_negativos_producto": "SELECT COUNT(*) FROM raw.producto WHERE precio_lista < 0 OR costo_base < 0;",
        "descuentos_invalidos_venta": "SELECT COUNT(*) FROM raw.venta_detalle WHERE descuento < 0 OR descuento > 1;",
        "cantidades_cero_o_negativas": "SELECT COUNT(*) FROM raw.venta_detalle WHERE cantidad <= 0;",
        "stock_negativo_inventario": "SELECT COUNT(*) FROM raw.inventario_bodega WHERE stock_disponible < 0;",
        "fechas_vencimiento_invalidas": "SELECT COUNT(*) FROM raw.inventario_bodega WHERE fecha_vencimiento < fecha_corte;",
    }

    with engine.connect() as conn:
        for check_name, query_str in queries.items():
            try:
                anomalies = conn.execute(text(query_str)).scalar()
                status = "PASSED (0 anomalías)" if anomalies == 0 else f"FLAGGED ({anomalies} anomalías detectadas)"
                checks[check_name] = status
                logger.info("Auditoría '%s': %s", check_name, status)
            except Exception as exc:
                checks[check_name] = f"ERROR ({exc})"
                logger.warning("No se pudo ejecutar regla '%s': %s", check_name, exc)

    return checks

if __name__ == "__main__":
    check_raw_tables_populated()
    evaluate_quality_rules()
