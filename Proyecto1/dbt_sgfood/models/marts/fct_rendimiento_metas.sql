WITH cumplimiento AS (
    SELECT * FROM {{ ref('int_cumplimiento_metas') }}
)

SELECT
    MD5(CONCAT(c.periodo_mes, '-', c.id_sucursal::TEXT)) AS fct_meta_sk,
    c.periodo_mes,
    MD5(c.id_sucursal::TEXT) AS dim_sucursal_sk,
    c.id_sucursal,
    c.meta_ventas,
    c.meta_unidades,
    c.ventas_reales,
    c.unidades_reales,
    c.pct_cumplimiento_monto,
    c.pct_cumplimiento_unidades,
    c.estado_cumplimiento
FROM cumplimiento c
