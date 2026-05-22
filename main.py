# -*- coding: utf-8 -*-
"""
main.py
Arranque de la aplicación desktop.
Intenta crear la conexión a la DB (db/conexion.crear_conexion) y levantar el login UI.
Diseñado para ser tolerante a módulos faltantes durante desarrollo.
"""
import sys
import os
import traceback
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

def _crear_conexion_safe():
    """
    Intenta importar y ejecutar db.conexion.crear_conexion().
    Si falla, devuelve None y muestra aviso en consola.
    """
    try:
        from db.conexion import crear_conexion
        conn = crear_conexion()
        if conn:
            print("[INFO] Conexión a la base de datos creada.")
        else:
            print("[WARN] crear_conexion() devolvió None.")
        return conn
    except Exception as e:
        print("[WARN] No se pudo crear conexión usando db/conexion.py (fallback).")
        traceback.print_exc()
        return None

def _obtener_login_widget(conexion):
    """
    Intenta importar la UI de login (preferible: ui/login_ui.py -> clase LoginUI).
    Si no existe, intenta buscar un LoginWindow en controllers.login_controller.
    """
    try:
        # preferimos la UI separada
        from ui.login_ui import LoginUI
        win = LoginUI()
        # Si el controlador real necesita la conexión, login_ui internamente lo cargará
        return win
    except Exception:
        try:
            # fallback: algunos proyectos exponen una ventana desde controllers
            from controllers.login_controller import LoginWindow
            win = LoginWindow(conexion)
            return win
        except Exception:
            traceback.print_exc()
            return None

def main():
    conexion = _crear_conexion_safe()

    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))

    login_window = _obtener_login_widget(conexion)
    if not login_window:
        print("❌ No se encontró la UI de login (ui/login_ui.py) ni LoginWindow en controllers/login_controller.")
        print("Asegúrate de tener 'ui/login_ui.py' con la clase LoginUI o 'controllers/login_controller.py' con LoginWindow.")
        return

    # Si la UI/Controller aceptan una conexión, intentar inyectarla
    try:
        # muchos diseños esperan que el controller reciba la conexión o que la UI espere la creación interna
        if hasattr(login_window, "set_conexion"):
            try:
                login_window.set_conexion(conexion)
            except Exception:
                pass
        # mostrar ventana (si es QMainWindow/QWidget)
        login_window.show()
        sys.exit(app.exec())
    except Exception as e:
        traceback.print_exc()
        print("Error al mostrar la ventana de login:", e)

if __name__ == "__main__":
    main()
    
    