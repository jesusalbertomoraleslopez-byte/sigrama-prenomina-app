@echo off
chcp 65001 > nul
title Sincronización Automática de Asistencias - Sigrama
echo ======================================================================
echo    SIGRAMA METALES - SINCRONIZACIÓN DE ASISTENCIAS DESDE OUTLOOK
echo ======================================================================
echo Buscando reportes del checador en Outlook (noreply@sigrama.com.mx)...

set "PYTHON_EXE=C:\Users\albertol\AppData\Local\Programs\Python\Python312\python.exe"
set "SCRIPT_PY=%~dp0sincronizar_asistencias_outlook.py"

"%PYTHON_EXE%" "%SCRIPT_PY%"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [OK] Proceso terminado correctamente.
) else (
    echo.
    echo [ERROR] Ocurrió un detalle durante la ejecución. Revisa sync_outlook.log
)

echo ======================================================================
timeout /t 5
