@echo off
echo   Compilando Servicio Windows C#
echo.

REM Verificar que .NET SDK está instalado
dotnet --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: .NET SDK no encontrado
    echo Instalar desde: https://dotnet.microsoft.com/download/dotnet/8.0
    pause
    exit /b 1
)

echo .NET SDK encontrado
echo.

REM Ir a carpeta del servicio
cd WindowsService

REM Compilar servicio
echo Compilando
dotnet publish -c Release -r win-x64 --self-contained true /p:PublishSingleFile=true

if %errorlevel% == 0 (
    echo.
    echo   Compilación Exitosa
    echo.
    
    REM Copiar ejecutable a raíz
    echo Copiando ejecutable
    copy /Y bin\Release\net8.0-windows\win-x64\publish\AsambleaService.exe ..\AsambleaService.exe
    
    if %errorlevel% == 0 (
        echo Copiado a: AsambleaService.exe
    ) else (
        echo Error copiando ejecutable
    )
    
    echo.
    echo   Verificando Assets
    
    REM Verificar assets
    if not exist "..\assets\sounds" (
        echo ADVERTENCIA: Falta carpeta assets\sounds\
        echo Crear carpeta y agregar archivos .wav
    ) else (
        echo Carpeta assets\sounds existe
        
        REM Verificar archivos WAV
        if exist "..\assets\sounds\new_boleta.wav" (
            echo    new_boleta.wav
        ) else (
            echo    new_boleta.wav faltante
        )
        
        if exist "..\assets\sounds\reject.wav" (
            echo    reject.wav
        ) else (
            echo    reject.wav faltante
        )
        
        if exist "..\assets\sounds\login_fail.wav" (
            echo    login_fail.wav
        ) else (
            echo    login_fail.wav faltante
        )
    )
    
    echo.
    echo   LISTO
    echo.
    echo Ejecutar: start_app.py
    echo O verificar: verify_install.py
    echo.
    
) else (
    echo.
    echo   ERROR EN COMPILACIÓN
    echo.
    echo Verificar:
    echo   1. .NET 8 SDK instalado correctamente
    echo   2. Archivos Program.cs y .csproj existen
    echo   3. No hay errores de sintaxis en Program.cs
    echo.
)

cd ..
pause