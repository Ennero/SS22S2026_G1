@echo off
title Iniciar Entorno Practica 2 - VuelosDW
echo ===================================================
echo   Seminario de Sistemas 2 - Practica 2
echo   Iniciando SQL Server y cargando datos ETL
echo ===================================================
echo.

:: 1. Verificar si Docker esta corriendo
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Desktop no esta iniciado o no responde.
    echo Por favor abre "Docker Desktop" desde el menu Inicio de Windows,
    echo espera a que el icono de la ballena este en verde y vuelve a ejecutar este script.
    echo.
    pause
    exit /b 1
)

:: 2. Levantar SQL Server en Docker
echo [1/3] Levantando SQL Server 2022 en Docker...
docker compose up -d sqlserver

:: 3. Esperar que el healthcheck este listo
echo [2/3] Esperando inicializacion de SQL Server (20 segundos)...
timeout /t 20 /nobreak >nul

:: 4. Ejecutar el pipeline ETL
echo [3/3] Ejecutando pipeline ETL para poblar VuelosDW...
docker compose run --rm etl

echo.
echo ===================================================
echo   Carga completada con exito!
echo   Ya puedes abrir "VuelosDW.pbip" en Power BI Desktop.
echo ===================================================
pause
