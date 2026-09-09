-- ============================================================
-- sql/ddl/create_model.sql
-- Modelo Multidimensional (Esquema Estrella) — VuelosDW
-- SQL Server 2022
--
-- Convenciones:
--   - Todas las tablas en el esquema dbo.
--   - PK autoincrementales IDENTITY(1,1) en tablas de dimensión.
--   - FactVuelos usa IDENTITY para id_vuelo.
--   - FK con ON DELETE NO ACTION / ON UPDATE NO ACTION.
--   - Índices no agrupados en FK de FactVuelos para acelerar JOINs.
--   - Script idempotente: usa IF OBJECT_ID(…) IS NULL antes de CREATE.
-- ============================================================

USE [VuelosDW];
GO

-- ============================================================
-- DIMENSIONES
-- ============================================================

-- ------------------------------------------------------------
-- DimFecha
-- ------------------------------------------------------------
IF OBJECT_ID(N'dbo.DimFecha', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.DimFecha (
        id_fecha        INT             NOT NULL,
        fecha           DATE            NOT NULL,
        dia             TINYINT         NOT NULL,
        mes             TINYINT         NOT NULL,
        anio            SMALLINT        NOT NULL,
        trimestre       TINYINT         NOT NULL,
        dia_semana      TINYINT         NOT NULL,   -- 0=Lunes … 6=Domingo
        nombre_dia      NVARCHAR(20)    NOT NULL,
        nombre_mes      NVARCHAR(20)    NOT NULL,
        es_fin_semana   BIT             NOT NULL DEFAULT 0,

        CONSTRAINT PK_DimFecha PRIMARY KEY CLUSTERED (id_fecha),
        CONSTRAINT UQ_DimFecha_fecha UNIQUE (fecha)
    );
    PRINT 'DimFecha creada.';
END
GO

-- ------------------------------------------------------------
-- DimPasajero
-- ------------------------------------------------------------
IF OBJECT_ID(N'dbo.DimPasajero', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.DimPasajero (
        id_pasajero     INT             NOT NULL,
        passenger_uuid  NVARCHAR(50)    NOT NULL,
        genero          NVARCHAR(10)    NOT NULL,   -- M / F / OTRO
        edad            TINYINT         NULL,
        rango_etario    NVARCHAR(10)    NULL,        -- <18 / 18-25 / ...
        nacionalidad    NVARCHAR(30)    NULL,        -- Código ISO 2 o DESCONOCIDO

        CONSTRAINT PK_DimPasajero PRIMARY KEY CLUSTERED (id_pasajero),
        CONSTRAINT UQ_DimPasajero_uuid UNIQUE (passenger_uuid)
    );
    PRINT 'DimPasajero creada.';
END
GO

-- ------------------------------------------------------------
-- DimAerolinea
-- ------------------------------------------------------------
IF OBJECT_ID(N'dbo.DimAerolinea', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.DimAerolinea (
        id_aerolinea        INT             NOT NULL,
        codigo_iata         NVARCHAR(5)     NOT NULL,
        nombre_aerolinea    NVARCHAR(100)   NOT NULL,

        CONSTRAINT PK_DimAerolinea PRIMARY KEY CLUSTERED (id_aerolinea),
        CONSTRAINT UQ_DimAerolinea_iata UNIQUE (codigo_iata)
    );
    PRINT 'DimAerolinea creada.';
END
GO

-- ------------------------------------------------------------
-- DimAeropuerto
-- Enriquecida con nombre del aeropuerto, ciudad y país para
-- habilitar jerarquía geográfica (País -> Ciudad -> Aeropuerto)
-- ------------------------------------------------------------
IF OBJECT_ID(N'dbo.DimAeropuerto', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.DimAeropuerto (
        id_aeropuerto       INT             NOT NULL,
        codigo_iata         NVARCHAR(5)     NOT NULL,
        nombre_aeropuerto   NVARCHAR(100)   NOT NULL,
        ciudad              NVARCHAR(50)    NOT NULL,
        pais                NVARCHAR(50)    NOT NULL,

        CONSTRAINT PK_DimAeropuerto PRIMARY KEY CLUSTERED (id_aeropuerto),
        CONSTRAINT UQ_DimAeropuerto_iata UNIQUE (codigo_iata)
    );
    PRINT 'DimAeropuerto creada.';
END
ELSE
BEGIN
    IF COL_LENGTH('dbo.DimAeropuerto', 'nombre_aeropuerto') IS NULL
        ALTER TABLE dbo.DimAeropuerto ADD nombre_aeropuerto NVARCHAR(100) NOT NULL DEFAULT 'DESCONOCIDO';
    IF COL_LENGTH('dbo.DimAeropuerto', 'ciudad') IS NULL
        ALTER TABLE dbo.DimAeropuerto ADD ciudad NVARCHAR(50) NOT NULL DEFAULT 'DESCONOCIDO';
    IF COL_LENGTH('dbo.DimAeropuerto', 'pais') IS NULL
        ALTER TABLE dbo.DimAeropuerto ADD pais NVARCHAR(50) NOT NULL DEFAULT 'DESCONOCIDO';
END
GO

-- ------------------------------------------------------------
-- DimClase  (dimensión adicional respecto al modelo propuesto)
-- Justificación: el dataset incluye cabin_class y aircraft_type,
-- datos descriptivos de cada vuelo, no atributos de aerolínea.
-- ------------------------------------------------------------
IF OBJECT_ID(N'dbo.DimClase', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.DimClase (
        id_clase        INT             NOT NULL,
        clase_cabina    NVARCHAR(30)    NOT NULL,
        tipo_aeronave   NVARCHAR(10)    NULL,

        CONSTRAINT PK_DimClase PRIMARY KEY CLUSTERED (id_clase)
    );
    PRINT 'DimClase creada.';
END
GO

-- ------------------------------------------------------------
-- DimEstado  (dimensión adicional respecto al modelo propuesto)
-- Justificación: el dataset incluye 4 estados de vuelo distintos
-- (ON_TIME, CANCELLED, DELAYED, DIVERTED), lo que agrega valor
-- analítico como dimensión.
-- ------------------------------------------------------------
IF OBJECT_ID(N'dbo.DimEstado', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.DimEstado (
        id_estado           INT             NOT NULL,
        estado_vuelo        NVARCHAR(20)    NOT NULL,
        descripcion_estado  NVARCHAR(100)   NULL,

        CONSTRAINT PK_DimEstado PRIMARY KEY CLUSTERED (id_estado),
        CONSTRAINT UQ_DimEstado_estado UNIQUE (estado_vuelo)
    );
    PRINT 'DimEstado creada.';
END
GO

-- ============================================================
-- TABLA DE HECHOS
-- ============================================================

-- ------------------------------------------------------------
-- FactVuelos
-- Grano: un registro por vuelo reservado/realizado.
-- Métricas: duracion_minutos, precio_usd, retraso_minutos, total_equipaje, dias_anticipacion.
-- Atributos degenerados: numero_vuelo, canal_venta, metodo_pago.
-- ------------------------------------------------------------
IF OBJECT_ID(N'dbo.FactVuelos', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.FactVuelos (
        id_vuelo            INT             NOT NULL IDENTITY(1,1),
        id_fecha            INT             NOT NULL,
        id_pasajero         INT             NOT NULL,
        id_aerolinea        INT             NOT NULL,
        id_origen           INT             NOT NULL,
        id_destino          INT             NOT NULL,
        id_clase            INT             NOT NULL,
        id_estado           INT             NOT NULL,
        numero_vuelo        NVARCHAR(20)    NULL,       -- Atributo degenerado
        duracion_minutos    INT             NULL,
        precio_usd          DECIMAL(10, 2)  NULL,
        retraso_minutos     INT             NULL DEFAULT 0,
        total_equipaje      TINYINT         NULL DEFAULT 0,
        canal_venta         NVARCHAR(30)    NULL,
        metodo_pago         NVARCHAR(30)    NULL,
        dias_anticipacion   INT             NULL DEFAULT 0,

        CONSTRAINT PK_FactVuelos PRIMARY KEY CLUSTERED (id_vuelo),

        CONSTRAINT FK_FactVuelos_Fecha
            FOREIGN KEY (id_fecha)      REFERENCES dbo.DimFecha      (id_fecha),
        CONSTRAINT FK_FactVuelos_Pasajero
            FOREIGN KEY (id_pasajero)   REFERENCES dbo.DimPasajero   (id_pasajero),
        CONSTRAINT FK_FactVuelos_Aerolinea
            FOREIGN KEY (id_aerolinea)  REFERENCES dbo.DimAerolinea  (id_aerolinea),
        CONSTRAINT FK_FactVuelos_Origen
            FOREIGN KEY (id_origen)     REFERENCES dbo.DimAeropuerto (id_aeropuerto),
        CONSTRAINT FK_FactVuelos_Destino
            FOREIGN KEY (id_destino)    REFERENCES dbo.DimAeropuerto (id_aeropuerto),
        CONSTRAINT FK_FactVuelos_Clase
            FOREIGN KEY (id_clase)      REFERENCES dbo.DimClase      (id_clase),
        CONSTRAINT FK_FactVuelos_Estado
            FOREIGN KEY (id_estado)     REFERENCES dbo.DimEstado     (id_estado)
    );
    PRINT 'FactVuelos creada.';
END
ELSE
BEGIN
    IF COL_LENGTH('dbo.FactVuelos', 'dias_anticipacion') IS NULL
        ALTER TABLE dbo.FactVuelos ADD dias_anticipacion INT NULL DEFAULT 0;
END
GO

-- ============================================================
-- ÍNDICES NO AGRUPADOS (FK y columnas de filtro frecuentes)
-- ============================================================

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'IX_FactVuelos_Fecha' AND object_id = OBJECT_ID('dbo.FactVuelos')
)
    CREATE NONCLUSTERED INDEX IX_FactVuelos_Fecha
        ON dbo.FactVuelos (id_fecha);
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'IX_FactVuelos_Aerolinea' AND object_id = OBJECT_ID('dbo.FactVuelos')
)
    CREATE NONCLUSTERED INDEX IX_FactVuelos_Aerolinea
        ON dbo.FactVuelos (id_aerolinea);
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'IX_FactVuelos_Origen_Destino' AND object_id = OBJECT_ID('dbo.FactVuelos')
)
    CREATE NONCLUSTERED INDEX IX_FactVuelos_Origen_Destino
        ON dbo.FactVuelos (id_origen, id_destino);
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'IX_FactVuelos_Pasajero' AND object_id = OBJECT_ID('dbo.FactVuelos')
)
    CREATE NONCLUSTERED INDEX IX_FactVuelos_Pasajero
        ON dbo.FactVuelos (id_pasajero);
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'IX_FactVuelos_Estado' AND object_id = OBJECT_ID('dbo.FactVuelos')
)
    CREATE NONCLUSTERED INDEX IX_FactVuelos_Estado
        ON dbo.FactVuelos (id_estado);
GO

PRINT 'DDL completado exitosamente.';
GO
