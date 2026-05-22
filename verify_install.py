# -*- coding: utf-8 -*-
"""
verify_install.py
Verifica que todo esté correctamente instalado
"""
import sys
import os
import subprocess
from pathlib import Path

def check(name, condition, error_msg):
    """Helper para verificar condiciones"""
    if condition:
        print(f"✅ {name}")
        return True
    else:
        print(f"❌ {name}")
        print(f"   {error_msg}")
        return False

def main():
    print("🔍 Verificando instalación...\n")
    
    all_ok = True
    
    # 1. Python
    all_ok &= check(
        "Python 3.10+",
        sys.version_info >= (3, 10),
        f"Versión actual: {sys.version}. Instalar Python 3.10+"
    )
    
    # 2. .NET SDK
    try:
        result = subprocess.run(["dotnet", "--version"], 
                              capture_output=True, text=True, timeout=5)
        version = result.stdout.strip()
        all_ok &= check(
            f".NET SDK ({version})",
            result.returncode == 0 and version.startswith("8"),
            "Instalar .NET 8 SDK desde https://dotnet.microsoft.com/download"
        )
    except:
        all_ok &= check(
            ".NET SDK",
            False,
            "dotnet no encontrado. Instalar .NET 8 SDK"
        )
    
    # 3. PostgreSQL
    try:
        result = subprocess.run(["psql", "--version"], 
                              capture_output=True, text=True, timeout=5)
        all_ok &= check(
            "PostgreSQL",
            result.returncode == 0,
            "Instalar PostgreSQL 14+"
        )
    except:
        all_ok &= check(
            "PostgreSQL",
            False,
            "psql no encontrado. Instalar PostgreSQL"
        )
    
    # 4. Dependencias Python
    try:
        import PySide6
        all_ok &= check("PySide6", True, "")
    except:
        all_ok &= check("PySide6", False, "pip install PySide6")
    
    try:
        import requests
        all_ok &= check("requests", True, "")
    except:
        all_ok &= check("requests", False, "pip install requests")
    
    try:
        import psycopg2
        all_ok &= check("psycopg2", True, "")
    except:
        all_ok &= check("psycopg2", False, "pip install psycopg2-binary")
    
    # 5. Archivos críticos
    files = {
        "WindowsService/Program.cs": "Archivo C# del servicio",
        "WindowsService/AsambleaService.csproj": "Proyecto .NET",
        "unified_schema.sql": "Schema de BD",
        "start_app.py": "Iniciador de app",
        "db/boletas.py": "Módulo boletas",
        "db/auditoria.py": "Módulo auditoría",
        "controllers/notification_controller.py": "Controlador notificaciones",
        "controllers/solicitudes_controller.py": "Controlador solicitudes"
    }
    
    for file, desc in files.items():
        all_ok &= check(
            f"{desc}",
            Path(file).exists(),
            f"Falta archivo: {file}"
        )
    
    # 6. Assets
    sounds = {
        "assets/sounds/new_boleta.wav": "Sonido nueva boleta",
        "assets/sounds/reject.wav": "Sonido rechazo",
        "assets/sounds/login_fail.wav": "Sonido login fail"
    }
    
    for file, desc in sounds.items():
        all_ok &= check(
            f"{desc}",
            Path(file).exists(),
            f"Falta: {file}"
        )
    
    # 7. Servicio compilado
    all_ok &= check(
        "Servicio compilado (AsambleaService.exe)",
        Path("AsambleaService.exe").exists(),
        "Ejecutar: built_service.bat"
    )
    
    # Resumen
    print("\n" + "="*50)
    if all_ok:
        print("✅ TODO CORRECTO - Listo para ejecutar")
        print("\nEjecutar: python start_app.py")
    else:
        print("❌ HAY PROBLEMAS - Revisar arriba")
        print("\nVer: README_MASTER.md para instrucciones")
    print("="*50)

if __name__ == "__main__":
    main()
