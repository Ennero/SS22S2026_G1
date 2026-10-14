WITH source AS (
    SELECT * FROM {{ source('raw', 'promociones') }}
),

renamed AS (
    SELECT
        id_promocion::INTEGER AS id_promocion,
        TRIM(nombre) AS promocion_nombre,
        fecha_inicio::DATE AS fecha_inicio,
        fecha_fin::DATE AS fecha_fin,
        id_categoria::INTEGER AS id_categoria,
        porcentaje_descuento::NUMERIC(5,4) AS porcentaje_descuento
    FROM source
)

SELECT * FROM renamed
