WITH promociones AS (
    SELECT * FROM {{ ref('stg_promociones') }}
),

categorias AS (
    SELECT * FROM {{ ref('stg_categorias') }}
)

SELECT
    MD5(p.id_promocion::TEXT) AS dim_promocion_sk,
    p.id_promocion,
    p.promocion_nombre,
    p.fecha_inicio,
    p.fecha_fin,
    p.id_categoria,
    c.categoria_nombre,
    p.porcentaje_descuento
FROM promociones p
LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
