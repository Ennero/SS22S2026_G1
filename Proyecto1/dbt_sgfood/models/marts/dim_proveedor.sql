WITH proveedores AS (
    SELECT * FROM {{ ref('stg_proveedores_precios') }}
)

SELECT
    MD5(CONCAT(id_proveedor::TEXT, '-', id_producto::TEXT, '-', fecha_vigencia::TEXT)) AS dim_proveedor_sk,
    id_proveedor,
    proveedor_nombre,
    id_producto,
    costo_proveedor,
    plazo_entrega_dias,
    fecha_vigencia
FROM proveedores
