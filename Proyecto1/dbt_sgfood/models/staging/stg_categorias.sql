WITH source AS (
    SELECT * FROM {{ source('raw', 'categoria') }}
),

renamed AS (
    SELECT
        id_categoria::INTEGER AS id_categoria,
        TRIM(nombre) AS categoria_nombre
    FROM source
)

SELECT * FROM renamed
