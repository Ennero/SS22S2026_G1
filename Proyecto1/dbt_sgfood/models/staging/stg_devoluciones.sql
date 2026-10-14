WITH source AS (
    SELECT * FROM {{ source('raw', 'devoluciones') }}
),

renamed AS (
    SELECT
        id_devolucion::INTEGER AS id_devolucion,
        fecha::DATE AS fecha_devolucion,
        id_venta::BIGINT AS id_venta,
        id_producto::INTEGER AS id_producto,
        cantidad::INTEGER AS cantidad_devuelta,
        TRIM(motivo) AS motivo_devolucion
    FROM source
)

SELECT * FROM renamed
