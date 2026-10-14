WITH inventario AS (
    SELECT * FROM {{ ref('stg_inventario') }}
),

productos AS (
    SELECT * FROM {{ ref('stg_productos') }}
)

SELECT
    i.fecha_corte,
    i.id_sucursal,
    i.id_producto,
    i.lote,
    i.fecha_vencimiento,
    i.stock_disponible,
    i.stock_minimo,
    i.stock_maximo,
    (i.stock_disponible - i.stock_minimo) AS diferencia_stock_min,
    CASE
        WHEN i.stock_disponible = 0 THEN 'Agotado'
        WHEN i.stock_disponible < i.stock_minimo THEN 'Crítico'
        WHEN i.stock_disponible > i.stock_maximo THEN 'Sobrestock'
        ELSE 'Normal'
    END AS estado_stock,
    (i.fecha_vencimiento - i.fecha_corte) AS dias_para_vencer,
    CASE
        WHEN i.fecha_vencimiento < i.fecha_corte THEN 'Vencido'
        WHEN i.fecha_vencimiento <= (i.fecha_corte + INTERVAL '30 days') THEN 'Próximo a Vencer'
        ELSE 'Vigente'
    END AS alerta_vencimiento,
    ROUND(i.stock_disponible * p.costo_base, 2) AS valor_inventario_costo
FROM inventario i
JOIN productos p ON i.id_producto = p.id_producto
