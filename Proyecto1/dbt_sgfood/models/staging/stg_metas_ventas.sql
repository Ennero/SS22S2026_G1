WITH source AS (
    SELECT * FROM {{ source('raw', 'metas_ventas') }}
),

renamed AS (
    SELECT
        TRIM(periodo) AS periodo_mes,
        id_sucursal::INTEGER AS id_sucursal,
        meta_ventas::NUMERIC(14,2) AS meta_ventas,
        meta_unidades::INTEGER AS meta_unidades
    FROM source
)

SELECT * FROM renamed
