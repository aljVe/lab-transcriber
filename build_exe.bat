@echo off
REM Script para compilar Lab Transcriber a ejecutable .exe
REM Versión: 1.3.6

echo ========================================
echo  Lab Transcriber - Build Script v1.3.6
echo ========================================
echo.

REM Verificar que existe config.json
if not exist "config.json" (
    echo ERROR: No se encuentra config.json en el directorio actual
    echo Por favor, asegurate de ejecutar este script desde la carpeta del proyecto
    pause
    exit /b 1
)

echo [1/4] Verificando PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller no esta instalado. Instalando...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: No se pudo instalar PyInstaller
        pause
        exit /b 1
    )
) else (
    echo PyInstaller ya esta instalado
)

echo.
echo [2/4] Verificando dependencias...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias
    pause
    exit /b 1
)

echo.
echo [3/4] Compilando ejecutable con PyInstaller...
echo Esto puede tardar varios minutos...
pyinstaller LabTranscriber.spec --clean
if errorlevel 1 (
    echo ERROR: Fallo la compilacion
    pause
    exit /b 1
)

echo.
echo [4/4] Copiando config.json a la carpeta dist...
copy /Y config.json dist\config.json >nul
if errorlevel 1 (
    echo ADVERTENCIA: No se pudo copiar config.json automaticamente
    echo Por favor, copia config.json manualmente a la carpeta dist\
)

echo.
echo ========================================
echo  COMPILACION COMPLETADA
echo ========================================
echo.
echo El ejecutable se encuentra en: dist\LabTranscriber_v136.exe
echo No olvides copiar config.json junto al ejecutable si lo mueves
echo.
pause
