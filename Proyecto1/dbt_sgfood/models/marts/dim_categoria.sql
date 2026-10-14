WITH categorias AS (
    SELECT * FROM {{ ref('stg_categorias') }}
)

SELECT
    MD5(id_categoria::TEXT) AS dim_categoria_sk,
    id_categoria,
    categoria_nombre
FROM categorias
