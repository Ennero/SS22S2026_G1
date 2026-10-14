WITH source AS (
    SELECT * FROM {{ source('raw', 'inventario_bodega') }}
),

renamed AS (
    SELECT
        fecha_corte::DATE AS fecha_corte,
        id_sucursal::INTEGER AS id_sucursal,
        id_producto::INTEGER AS id_producto,
        stock_disponible::INTEGER AS stock_disponible,
        stock_minimo::INTEGER AS stock_minimo,
        stock_maximo::INTEGER AS stock_maximo,
        TRIM(lote) AS lote,
        fecha_vencimiento::DATE AS fecha_vencimiento
    FROM source
)

SELECT * FROM renamed
