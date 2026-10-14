-- =============================================================================
-- PROYECTO 1 - SEMINARIO DE SISTEMAS 2 (2S 2026)
-- EMPRESA: SG-FOOD
-- SCRIPT DE CONSTRAINTS: PRIMARY KEYS Y FOREIGN KEYS EN SCHEMA MARTS
-- Proposito: Habilitar navegabilidad de claves foraneas (hipervinculos clicables)
--            y diagramas relacionales (vista de Esquema) en Adminer, DBeaver y herramientas BI.
-- =============================================================================

DO $$
BEGIN
    -- 1. PRIMARY KEYS & UNIQUE CONSTRAINTS EN TABLAS DIMENSIONALES
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'pk_dim_sucursal') THEN
        ALTER TABLE marts.dim_sucursal ADD CONSTRAINT pk_dim_sucursal PRIMARY KEY (id_sucursal);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_dim_sucursal_sk') THEN
        ALTER TABLE marts.dim_sucursal ADD CONSTRAINT uq_dim_sucursal_sk UNIQUE (dim_sucursal_sk);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'pk_dim_cliente') THEN
        ALTER TABLE marts.dim_cliente ADD CONSTRAINT pk_dim_cliente PRIMARY KEY (id_cliente);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_dim_cliente_sk') THEN
        ALTER TABLE marts.dim_cliente ADD CONSTRAINT uq_dim_cliente_sk UNIQUE (dim_cliente_sk);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'pk_dim_categoria') THEN
        ALTER TABLE marts.dim_categoria ADD CONSTRAINT pk_dim_categoria PRIMARY KEY (id_categoria);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_dim_categoria_sk') THEN
        ALTER TABLE marts.dim_categoria ADD CONSTRAINT uq_dim_categoria_sk UNIQUE (dim_categoria_sk);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'pk_dim_marca') THEN
        ALTER TABLE marts.dim_marca ADD CONSTRAINT pk_dim_marca PRIMARY KEY (id_marca);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_dim_marca_sk') THEN
        ALTER TABLE marts.dim_marca ADD CONSTRAINT uq_dim_marca_sk UNIQUE (dim_marca_sk);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'pk_dim_producto') THEN
        ALTER TABLE marts.dim_producto ADD CONSTRAINT pk_dim_producto PRIMARY KEY (id_producto);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_dim_producto_sk') THEN
        ALTER TABLE marts.dim_producto ADD CONSTRAINT uq_dim_producto_sk UNIQUE (dim_producto_sk);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'pk_dim_fecha') THEN
        ALTER TABLE marts.dim_fecha ADD CONSTRAINT pk_dim_fecha PRIMARY KEY (fecha_id);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'pk_dim_promocion') THEN
        ALTER TABLE marts.dim_promocion ADD CONSTRAINT pk_dim_promocion PRIMARY KEY (id_promocion);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_dim_promocion_sk') THEN
        ALTER TABLE marts.dim_promocion ADD CONSTRAINT uq_dim_promocion_sk UNIQUE (dim_promocion_sk);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'pk_dim_proveedor') THEN
        ALTER TABLE marts.dim_proveedor ADD CONSTRAINT pk_dim_proveedor PRIMARY KEY (dim_proveedor_sk);
    END IF;

    -- 2. PRIMARY KEYS EN TABLAS DE HECHOS (FACT TABLES)
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'pk_fct_ventas') THEN
        ALTER TABLE marts.fct_ventas ADD CONSTRAINT pk_fct_ventas PRIMARY KEY (fct_venta_sk);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'pk_fct_inventario') THEN
        ALTER TABLE marts.fct_inventario ADD CONSTRAINT pk_fct_inventario PRIMARY KEY (fct_inventario_sk);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'pk_fct_devoluciones') THEN
        ALTER TABLE marts.fct_devoluciones ADD CONSTRAINT pk_fct_devoluciones PRIMARY KEY (fct_devolucion_sk);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'pk_fct_rendimiento_metas') THEN
        ALTER TABLE marts.fct_rendimiento_metas ADD CONSTRAINT pk_fct_rendimiento_metas PRIMARY KEY (fct_meta_sk);
    END IF;

    -- 3. FOREIGN KEYS ENTRE TABLAS DIMENSIONALES
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_dim_producto_categoria') THEN
        ALTER TABLE marts.dim_producto 
            ADD CONSTRAINT fk_dim_producto_categoria FOREIGN KEY (id_categoria) REFERENCES marts.dim_categoria(id_categoria);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_dim_producto_marca') THEN
        ALTER TABLE marts.dim_producto 
            ADD CONSTRAINT fk_dim_producto_marca FOREIGN KEY (id_marca) REFERENCES marts.dim_marca(id_marca);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_dim_promocion_categoria') THEN
        ALTER TABLE marts.dim_promocion 
            ADD CONSTRAINT fk_dim_promocion_categoria FOREIGN KEY (id_categoria) REFERENCES marts.dim_categoria(id_categoria);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_dim_proveedor_producto') THEN
        ALTER TABLE marts.dim_proveedor 
            ADD CONSTRAINT fk_dim_proveedor_producto FOREIGN KEY (id_producto) REFERENCES marts.dim_producto(id_producto);
    END IF;

    -- 4. FOREIGN KEYS EN TABLAS DE HECHOS
    -- fct_ventas
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_fct_ventas_sucursal') THEN
        ALTER TABLE marts.fct_ventas
            ADD CONSTRAINT fk_fct_ventas_sucursal FOREIGN KEY (id_sucursal) REFERENCES marts.dim_sucursal(id_sucursal);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_fct_ventas_cliente') THEN
        ALTER TABLE marts.fct_ventas
            ADD CONSTRAINT fk_fct_ventas_cliente FOREIGN KEY (id_cliente) REFERENCES marts.dim_cliente(id_cliente);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_fct_ventas_producto') THEN
        ALTER TABLE marts.fct_ventas
            ADD CONSTRAINT fk_fct_ventas_producto FOREIGN KEY (id_producto) REFERENCES marts.dim_producto(id_producto);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_fct_ventas_fecha') THEN
        ALTER TABLE marts.fct_ventas
            ADD CONSTRAINT fk_fct_ventas_fecha FOREIGN KEY (fecha_id) REFERENCES marts.dim_fecha(fecha_id);
    END IF;

    -- fct_inventario
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_fct_inventario_sucursal') THEN
        ALTER TABLE marts.fct_inventario
            ADD CONSTRAINT fk_fct_inventario_sucursal FOREIGN KEY (id_sucursal) REFERENCES marts.dim_sucursal(id_sucursal);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_fct_inventario_producto') THEN
        ALTER TABLE marts.fct_inventario
            ADD CONSTRAINT fk_fct_inventario_producto FOREIGN KEY (id_producto) REFERENCES marts.dim_producto(id_producto);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_fct_inventario_fecha') THEN
        ALTER TABLE marts.fct_inventario
            ADD CONSTRAINT fk_fct_inventario_fecha FOREIGN KEY (fecha_id) REFERENCES marts.dim_fecha(fecha_id);
    END IF;

    -- fct_devoluciones
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_fct_devoluciones_sucursal') THEN
        ALTER TABLE marts.fct_devoluciones
            ADD CONSTRAINT fk_fct_devoluciones_sucursal FOREIGN KEY (id_sucursal) REFERENCES marts.dim_sucursal(id_sucursal);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_fct_devoluciones_producto') THEN
        ALTER TABLE marts.fct_devoluciones
            ADD CONSTRAINT fk_fct_devoluciones_producto FOREIGN KEY (id_producto) REFERENCES marts.dim_producto(id_producto);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_fct_devoluciones_fecha') THEN
        ALTER TABLE marts.fct_devoluciones
            ADD CONSTRAINT fk_fct_devoluciones_fecha FOREIGN KEY (fecha_id) REFERENCES marts.dim_fecha(fecha_id);
    END IF;

    -- fct_rendimiento_metas
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_fct_rendimiento_metas_sucursal') THEN
        ALTER TABLE marts.fct_rendimiento_metas
            ADD CONSTRAINT fk_fct_rendimiento_metas_sucursal FOREIGN KEY (id_sucursal) REFERENCES marts.dim_sucursal(id_sucursal);
    END IF;

END $$;
