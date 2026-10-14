WITH source AS (
    SELECT * FROM {{ source('raw', 'venta_detalle') }}
),

renamed AS (
    SELECT
        id_detalle::BIGINT AS id_detalle,
        id_venta::BIGINT AS id_venta,
        id_producto::INTEGER AS id_producto,
        cantidad::INTEGER AS cantidad,
        precio_unitario::NUMERIC(12,2) AS precio_unitario,
        descuento::NUMERIC(5,4) AS porcentaje_descuento,
        subtotal::NUMERIC(14,2) AS subtotal
    FROM source
)

SELECT * FROM renamed
