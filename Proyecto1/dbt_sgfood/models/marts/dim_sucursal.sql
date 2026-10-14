WITH sucursales AS (
    SELECT * FROM {{ ref('stg_sucursales') }}
)

SELECT
    MD5(id_sucursal::TEXT) AS dim_sucursal_sk,
    id_sucursal,
    sucursal_nombre,
    ciudad,
    departamento
FROM sucursales
