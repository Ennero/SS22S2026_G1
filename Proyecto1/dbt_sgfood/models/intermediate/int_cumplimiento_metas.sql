WITH ventas_mensuales AS (
    SELECT
        TO_CHAR(fecha_venta, 'YYYY-MM') AS periodo_mes,
        id_sucursal,
        SUM(importe_neto) AS ventas_reales,
        SUM(cantidad) AS unidades_reales
    FROM {{ ref('int_ventas_enriquecidas') }}
    WHERE estado_venta <> 'CANCELADA'
    GROUP BY TO_CHAR(fecha_venta, 'YYYY-MM'), id_sucursal
),

metas AS (
    SELECT * FROM {{ ref('stg_metas_ventas') }}
)

SELECT
    m.periodo_mes,
    m.id_sucursal,
    m.meta_ventas,
    m.meta_unidades,
    COALESCE(v.ventas_reales, 0) AS ventas_reales,
    COALESCE(v.unidades_reales, 0) AS unidades_reales,
    ROUND(
        CASE
            WHEN m.meta_ventas > 0 THEN (COALESCE(v.ventas_reales, 0) / m.meta_ventas) * 100
            ELSE 0
        END, 2
    ) AS pct_cumplimiento_monto,
    ROUND(
        CASE
            WHEN m.meta_unidades > 0 THEN (COALESCE(v.unidades_reales, 0)::NUMERIC / m.meta_unidades) * 100
            ELSE 0
        END, 2
    ) AS pct_cumplimiento_unidades,
    CASE
        WHEN COALESCE(v.ventas_reales, 0) >= m.meta_ventas THEN 'Meta Cumplida'
        ELSE 'Por Debajo de Meta'
    END AS estado_cumplimiento
FROM metas m
LEFT JOIN ventas_mensuales v
    ON m.periodo_mes = v.periodo_mes
    AND m.id_sucursal = v.id_sucursal
