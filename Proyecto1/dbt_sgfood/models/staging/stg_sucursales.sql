WITH source AS (
    SELECT * FROM {{ source('raw', 'sucursal') }}
),

renamed AS (
    SELECT
        id_sucursal::INTEGER AS id_sucursal,
        TRIM(nombre) AS sucursal_nombre,
        TRIM(ciudad) AS ciudad,
        TRIM(departamento) AS departamento
    FROM source
)

SELECT * FROM renamed
