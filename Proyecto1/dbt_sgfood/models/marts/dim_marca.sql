WITH marcas AS (
    SELECT * FROM {{ ref('stg_marcas') }}
)

SELECT
    MD5(id_marca::TEXT) AS dim_marca_sk,
    id_marca,
    marca_nombre
FROM marcas
