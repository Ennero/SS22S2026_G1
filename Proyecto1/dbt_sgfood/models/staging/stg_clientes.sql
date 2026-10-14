WITH source AS (
    SELECT * FROM {{ source('raw', 'cliente') }}
),

renamed AS (
    SELECT
        id_cliente::INTEGER AS id_cliente,
        TRIM(nit) AS nit,
        TRIM(nombre) AS cliente_nombre,
        TRIM(tipo_cliente) AS tipo_cliente,
        COALESCE(NULLIF(TRIM(municipio), ''), 'No especificado') AS municipio,
        COALESCE(NULLIF(TRIM(departamento), ''), 'No especificado') AS departamento,
        fecha_alta::DATE AS fecha_alta
    FROM source
)

SELECT * FROM renamed
