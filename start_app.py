# -*- coding: utf-8 -*-
"""
start_app.py - Inicia servicio C# + UI Python
USAR ESTE ARCHIVO EN LUGAR DE main.py
"""
import sys
import os
import subprocess
import time
import socket
from pathlib import Path

SERVICE_EXE = Path(__file__).parent / "AsambleaService.exe"

def check_service_running():
    """Verifica si el servicio ya está corriendo"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 5555))
        sock.close()
        return result == 0
    except:
        return False

def start_service():
    """Inicia servicio Windows si no está corriendo"""
    if check_service_running():
        print("✅ Servicio ya está corriendo")
        return
    
    if SERVICE_EXE.exists():
        try:
            # Crear proceso sin ventana
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            subprocess.Popen(
                [str(SERVICE_EXE)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                startupinfo=startupinfo
            )
            print("✅ Servicio iniciado")
            time.sleep(3)  # Esperar inicio
            
            # Verificar que arrancó
            if check_service_running():
                print("✅ Servicio OK")
            else:
                print("⚠️ Servicio no responde")
                
        except Exception as e:
            print(f"⚠️ Error: {e}")
    else:
        print(f"⚠️ {SERVICE_EXE} no encontrado")
        print("Ejecutar: built_service.bat")

def main():
    # Suprimir warnings de Qt
    os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false"
    
    start_service()
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QFont
        from ui.login_ui import LoginUI
        
        app = QApplication(sys.argv)
        app.setFont(QFont("Segoe UI", 10))
        
        login = LoginUI()
        login.show()
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("Instalar: pip install PySide6 requests")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()