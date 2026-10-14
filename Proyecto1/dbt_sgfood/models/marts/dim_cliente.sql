WITH clientes AS (
    SELECT * FROM {{ ref('stg_clientes') }}
)

SELECT
    MD5(id_cliente::TEXT) AS dim_cliente_sk,
    id_cliente,
    nit,
    cliente_nombre,
    tipo_cliente,
    municipio,
    departamento,
    fecha_alta
FROM clientes
