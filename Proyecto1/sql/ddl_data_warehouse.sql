-- =============================================================================
-- PROYECTO 1 - SEMINARIO DE SISTEMAS 2 (2S 2026)
-- EMPRESA: SG-FOOD
-- SCRIPT DDL: ARQUITECTURA DE DATA WAREHOUSE EN POSTGRESQL
-- Schemas: raw, staging, intermediate, marts
-- =============================================================================

-- 1. CREACIÓN DE SCHEMAS
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS intermediate;
CREATE SCHEMA IF NOT EXISTS marts;

-- =============================================================================
-- 2. DDL SCHEMA RAW (Tablas de Ingesta Cruda)
-- =============================================================================

-- Fuente Transaccional OLTP (SG-Food)
CREATE TABLE IF NOT EXISTS raw.sucursal (
    id_sucursal INT,
    nombre VARCHAR(100),
    ciudad VARCHAR(100),
    departamento VARCHAR(100),
    _ingested_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw.categoria (
    id_categoria INT,
    nombre VARCHAR(100),
    _ingested_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw.marca (
    id_marca INT,
    nombre VARCHAR(100),
    _ingested_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw.producto (
    id_producto INT,
    sku VARCHAR(20),
    nombre VARCHAR(150),
    id_categoria INT,
    id_marca INT,
    unidad_medida VARCHAR(30),
    costo_base NUMERIC(12,2),
    precio_lista NUMERIC(12,2),
    activo BOOLEAN,
    _ingested_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw.cliente (
    id_cliente INT,
    nit VARCHAR(20),
    nombre VARCHAR(150),
    tipo_cliente VARCHAR(40),
    municipio VARCHAR(100),
    departamento VARCHAR(100),
    fecha_alta DATE,
    _ingested_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw.venta (
    id_venta BIGINT,
    fecha DATE,
    id_cliente INT,
    id_sucursal INT,
    canal VARCHAR(30),
    metodo_pago VARCHAR(30),
    estado VARCHAR(20),
    _ingested_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw.venta_detalle (
    id_detalle BIGINT,
    id_venta BIGINT,
    id_producto INT,
    cantidad INT,
    precio_unitario NUMERIC(12,2),
    descuento NUMERIC(5,4),
    subtotal NUMERIC(14,2),
    _ingested_at TIMESTAMP
);

-- Archivos Planos CSV Complementarios
CREATE TABLE IF NOT EXISTS raw.inventario_bodega (
    fecha_corte DATE,
    id_sucursal INT,
    id_producto INT,
    stock_disponible INT,
    stock_minimo INT,
    stock_maximo INT,
    lote VARCHAR(50),
    fecha_vencimiento DATE,
    _ingested_at TIMESTAMP,
    _source_file VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS raw.proveedores_precios (
    id_proveedor INT,
    proveedor VARCHAR(150),
    id_producto INT,
    costo_proveedor NUMERIC(12,2),
    plazo_dias INT,
    fecha_vigencia DATE,
    _ingested_at TIMESTAMP,
    _source_file VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS raw.promociones (
    id_promocion INT,
    nombre VARCHAR(150),
    fecha_inicio DATE,
    fecha_fin DATE,
    id_categoria INT,
    porcentaje_descuento NUMERIC(5,4),
    _ingested_at TIMESTAMP,
    _source_file VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS raw.metas_ventas (
    periodo VARCHAR(10),
    id_sucursal INT,
    meta_ventas NUMERIC(14,2),
    meta_unidades INT,
    _ingested_at TIMESTAMP,
    _source_file VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS raw.devoluciones (
    id_devolucion INT,
    fecha DATE,
    id_venta BIGINT,
    id_producto INT,
    cantidad INT,
    motivo VARCHAR(150),
    _ingested_at TIMESTAMP,
    _source_file VARCHAR(100)
);

-- =============================================================================
-- 3. DDL SCHEMA MARTS (Modelo Dimensional de Estrella - Data Warehouse)
-- =============================================================================

-- Dimensión Sucursal
CREATE TABLE IF NOT EXISTS marts.dim_sucursal (
    dim_sucursal_sk TEXT PRIMARY KEY,
    id_sucursal INT NOT NULL,
    sucursal_nombre TEXT NOT NULL,
    ciudad TEXT,
    departamento TEXT
);

-- Dimensión Categoría
CREATE TABLE IF NOT EXISTS marts.dim_categoria (
    dim_categoria_sk TEXT PRIMARY KEY,
    id_categoria INT NOT NULL,
    categoria_nombre TEXT NOT NULL
);

-- Dimensión Marca
CREATE TABLE IF NOT EXISTS marts.dim_marca (
    dim_marca_sk TEXT PRIMARY KEY,
    id_marca INT NOT NULL,
    marca_nombre TEXT NOT NULL
);

-- Dimensión Producto
CREATE TABLE IF NOT EXISTS marts.dim_producto (
    dim_producto_sk TEXT PRIMARY KEY,
    id_producto INT NOT NULL,
    sku TEXT NOT NULL,
    producto_nombre TEXT NOT NULL,
    id_categoria INT,
    categoria_nombre TEXT,
    id_marca INT,
    marca_nombre TEXT,
    unidad_medida TEXT,
    costo_base NUMERIC,
    precio_lista NUMERIC,
    es_activo BOOLEAN
);

-- Dimensión Cliente
CREATE TABLE IF NOT EXISTS marts.dim_cliente (
    dim_cliente_sk TEXT PRIMARY KEY,
    id_cliente INT NOT NULL,
    nit TEXT,
    cliente_nombre TEXT NOT NULL,
    tipo_cliente TEXT,
    municipio TEXT,
    departamento TEXT,
    fecha_alta DATE
);

-- Dimensión Proveedor
CREATE TABLE IF NOT EXISTS marts.dim_proveedor (
    dim_proveedor_sk TEXT PRIMARY KEY,
    id_proveedor INT NOT NULL,
    proveedor_nombre TEXT NOT NULL,
    id_producto INT,
    costo_proveedor NUMERIC,
    plazo_entrega_dias INT,
    fecha_vigencia DATE
);

-- Dimensión Promoción
CREATE TABLE IF NOT EXISTS marts.dim_promocion (
    dim_promocion_sk TEXT PRIMARY KEY,
    id_promocion INT NOT NULL,
    promocion_nombre TEXT NOT NULL,
    fecha_inicio DATE,
    fecha_fin DATE,
    id_categoria INT,
    categoria_nombre TEXT,
    porcentaje_descuento NUMERIC
);

-- Dimensión Fecha
CREATE TABLE IF NOT EXISTS marts.dim_fecha (
    fecha_id INT PRIMARY KEY,
    fecha DATE NOT NULL,
    anio INT NOT NULL,
    mes INT NOT NULL,
    nombre_mes TEXT NOT NULL,
    dia INT NOT NULL,
    dia_semana INT NOT NULL,
    nombre_dia TEXT NOT NULL,
    trimestre INT NOT NULL,
    es_fin_semana BOOLEAN NOT NULL
);

-- Tabla de Hechos: Ventas (Fact Ventas)
CREATE TABLE IF NOT EXISTS marts.fct_ventas (
    fct_venta_sk TEXT PRIMARY KEY,
    id_detalle BIGINT NOT NULL,
    id_venta BIGINT NOT NULL,
    fecha_id INT,
    fecha_venta DATE,
    dim_cliente_sk TEXT,
    id_cliente INT,
    dim_sucursal_sk TEXT,
    id_sucursal INT,
    dim_producto_sk TEXT,
    id_producto INT,
    canal_venta TEXT,
    metodo_pago TEXT,
    estado_venta TEXT,
    cantidad INT NOT NULL,
    precio_unitario NUMERIC NOT NULL,
    porcentaje_descuento NUMERIC,
    importe_bruto NUMERIC,
    monto_descuento NUMERIC,
    importe_neto NUMERIC NOT NULL,
    costo_total NUMERIC,
    margen_ganancia NUMERIC,
    porcentaje_margen NUMERIC
);

-- Tabla de Hechos: Inventario (Fact Inventario)
CREATE TABLE IF NOT EXISTS marts.fct_inventario (
    fct_inventario_sk TEXT PRIMARY KEY,
    fecha_id INT,
    fecha_corte DATE,
    dim_sucursal_sk TEXT,
    id_sucursal INT,
    dim_producto_sk TEXT,
    id_producto INT,
    lote TEXT,
    fecha_vencimiento DATE,
    stock_disponible INT NOT NULL,
    stock_minimo INT NOT NULL,
    stock_maximo INT NOT NULL,
    diferencia_stock_min INT,
    estado_stock TEXT,
    dias_para_vencer INT,
    alerta_vencimiento TEXT,
    valor_inventario_costo NUMERIC
);

-- Tabla de Hechos: Devoluciones (Fact Devoluciones)
CREATE TABLE IF NOT EXISTS marts.fct_devoluciones (
    fct_devolucion_sk TEXT PRIMARY KEY,
    id_devolucion INT NOT NULL,
    fecha_id INT,
    fecha_devolucion DATE,
    id_venta BIGINT,
    dim_sucursal_sk TEXT,
    id_sucursal INT,
    dim_producto_sk TEXT,
    id_producto INT,
    cantidad_devuelta INT NOT NULL,
    motivo_devolucion TEXT,
    monto_estimado_devolucion NUMERIC
);

-- Tabla de Hechos: Rendimiento y Metas (Fact Rendimiento Metas)
CREATE TABLE IF NOT EXISTS marts.fct_rendimiento_metas (
    fct_meta_sk TEXT PRIMARY KEY,
    periodo_mes TEXT NOT NULL,
    dim_sucursal_sk TEXT,
    id_sucursal INT,
    meta_ventas NUMERIC NOT NULL,
    meta_unidades INT NOT NULL,
    ventas_reales NUMERIC NOT NULL,
    unidades_reales BIGINT NOT NULL,
    pct_cumplimiento_monto NUMERIC,
    pct_cumplimiento_unidades NUMERIC,
    estado_cumplimiento TEXT
);

-- Índices Analíticos para Acelerar Consultas y Visualización BI
CREATE INDEX IF NOT EXISTS idx_fct_ventas_fecha ON marts.fct_ventas(fecha_venta);
CREATE INDEX IF NOT EXISTS idx_fct_ventas_sucursal ON marts.fct_ventas(id_sucursal);
CREATE INDEX IF NOT EXISTS idx_fct_ventas_producto ON marts.fct_ventas(id_producto);
CREATE INDEX IF NOT EXISTS idx_fct_ventas_cliente ON marts.fct_ventas(id_cliente);
CREATE INDEX IF NOT EXISTS idx_fct_inventario_corte ON marts.fct_inventario(fecha_corte);
CREATE INDEX IF NOT EXISTS idx_fct_inventario_sucursal ON marts.fct_inventario(id_sucursal);
CREATE INDEX IF NOT EXISTS idx_fct_inventario_producto ON marts.fct_inventario(id_producto);
CREATE INDEX IF NOT EXISTS idx_fct_devoluciones_fecha ON marts.fct_devoluciones(fecha_devolucion);

-- =============================================================================
-- 4. CONSTRAINTS RELACIONALES (FOREIGN KEYS Y UNIQUE KEYS PARA ADMINER / BI)
-- =============================================================================

-- Restricciones de Unicidad en Claves de Negocio de Dimensiones
ALTER TABLE marts.dim_sucursal ADD CONSTRAINT uq_dim_sucursal_id UNIQUE (id_sucursal);
ALTER TABLE marts.dim_cliente ADD CONSTRAINT uq_dim_cliente_id UNIQUE (id_cliente);
ALTER TABLE marts.dim_categoria ADD CONSTRAINT uq_dim_categoria_id UNIQUE (id_categoria);
ALTER TABLE marts.dim_marca ADD CONSTRAINT uq_dim_marca_id UNIQUE (id_marca);
ALTER TABLE marts.dim_producto ADD CONSTRAINT uq_dim_producto_id UNIQUE (id_producto);
ALTER TABLE marts.dim_promocion ADD CONSTRAINT uq_dim_promocion_id UNIQUE (id_promocion);

-- Claves Foráneas de Jerarquía Dimensional
ALTER TABLE marts.dim_producto 
    ADD CONSTRAINT fk_dim_producto_categoria FOREIGN KEY (id_categoria) REFERENCES marts.dim_categoria(id_categoria),
    ADD CONSTRAINT fk_dim_producto_marca FOREIGN KEY (id_marca) REFERENCES marts.dim_marca(id_marca);

ALTER TABLE marts.dim_promocion 
    ADD CONSTRAINT fk_dim_promocion_categoria FOREIGN KEY (id_categoria) REFERENCES marts.dim_categoria(id_categoria);

ALTER TABLE marts.dim_proveedor 
    ADD CONSTRAINT fk_dim_proveedor_producto FOREIGN KEY (id_producto) REFERENCES marts.dim_producto(id_producto);

-- Claves Foráneas en Tablas de Hechos (Fact Tables)
ALTER TABLE marts.fct_ventas
    ADD CONSTRAINT fk_fct_ventas_sucursal FOREIGN KEY (id_sucursal) REFERENCES marts.dim_sucursal(id_sucursal),
    ADD CONSTRAINT fk_fct_ventas_cliente FOREIGN KEY (id_cliente) REFERENCES marts.dim_cliente(id_cliente),
    ADD CONSTRAINT fk_fct_ventas_producto FOREIGN KEY (id_producto) REFERENCES marts.dim_producto(id_producto),
    ADD CONSTRAINT fk_fct_ventas_fecha FOREIGN KEY (fecha_id) REFERENCES marts.dim_fecha(fecha_id);

ALTER TABLE marts.fct_inventario
    ADD CONSTRAINT fk_fct_inventario_sucursal FOREIGN KEY (id_sucursal) REFERENCES marts.dim_sucursal(id_sucursal),
    ADD CONSTRAINT fk_fct_inventario_producto FOREIGN KEY (id_producto) REFERENCES marts.dim_producto(id_producto),
    ADD CONSTRAINT fk_fct_inventario_fecha FOREIGN KEY (fecha_id) REFERENCES marts.dim_fecha(fecha_id);

ALTER TABLE marts.fct_devoluciones
    ADD CONSTRAINT fk_fct_devoluciones_sucursal FOREIGN KEY (id_sucursal) REFERENCES marts.dim_sucursal(id_sucursal),
    ADD CONSTRAINT fk_fct_devoluciones_producto FOREIGN KEY (id_producto) REFERENCES marts.dim_producto(id_producto),
    ADD CONSTRAINT fk_fct_devoluciones_fecha FOREIGN KEY (fecha_id) REFERENCES marts.dim_fecha(fecha_id);

ALTER TABLE marts.fct_rendimiento_metas
    ADD CONSTRAINT fk_fct_rendimiento_metas_sucursal FOREIGN KEY (id_sucursal) REFERENCES marts.dim_sucursal(id_sucursal);

-- =============================================================================
-- 5. TABLA DE AUDITORÍA Y OBSERVABILIDAD DEL PIPELINE (OPCIONAL / PLUS)
-- =============================================================================
CREATE TABLE IF NOT EXISTS marts.log_pipeline_auditoria (
    id_log SERIAL PRIMARY KEY,
    dag_id VARCHAR(100) NOT NULL,
    run_id VARCHAR(250) NOT NULL,
    fecha_ejecucion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duracion_segundos NUMERIC(8,2),
    estado VARCHAR(30) NOT NULL,
    tablas_oltp_procesadas INT,
    archivos_csv_procesados INT,
    modelos_dbt_ejecutados INT,
    pruebas_calidad_aprobadas INT,
    mensaje_auditoria TEXT
);

