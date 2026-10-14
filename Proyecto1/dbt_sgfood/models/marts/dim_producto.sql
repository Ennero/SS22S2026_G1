WITH productos AS (
    SELECT * FROM {{ ref('stg_productos') }}
),

categorias AS (
    SELECT * FROM {{ ref('stg_categorias') }}
),

marcas AS (
    SELECT * FROM {{ ref('stg_marcas') }}
)

SELECT
    MD5(p.id_producto::TEXT) AS dim_producto_sk,
    p.id_producto,
    p.sku,
    p.producto_nombre,
    p.id_categoria,
    c.categoria_nombre,
    p.id_marca,
    m.marca_nombre,
    p.unidad_medida,
    p.costo_base,
    p.precio_lista,
    p.es_activo
FROM productos p
LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
LEFT JOIN marcas m ON p.id_marca = m.id_marca
