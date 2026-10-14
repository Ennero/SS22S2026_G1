WITH source AS (
    SELECT * FROM {{ source('raw', 'marca') }}
),

renamed AS (
    SELECT
        id_marca::INTEGER AS id_marca,
        TRIM(nombre) AS marca_nombre
    FROM source
)

SELECT * FROM renamed
