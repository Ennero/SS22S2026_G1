WITH source AS (
    SELECT * FROM {{ source('raw', 'venta') }}
),

renamed AS (
    SELECT
        id_venta::BIGINT AS id_venta,
        fecha::DATE AS fecha_venta,
        id_cliente::INTEGER AS id_cliente,
        id_sucursal::INTEGER AS id_sucursal,
        TRIM(canal) AS canal_venta,
        TRIM(metodo_pago) AS metodo_pago,
        UPPER(TRIM(estado)) AS estado_venta
    FROM source
)

SELECT * FROM renamed
