import sys
import importlib
import time
from threading import Thread
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from PySide6.QtWidgets import QApplication

# Carpeta donde están tus UIs
UI_FOLDER = "ui"

# Datos de usuario de prueba
user_data = {
    'id': 1,
    'nombre': 'Ana María Rodríguez',
    'correo': 'ana.rodriguez@asamblea.go.cr',
    'rol': 'admin'
}

# Evento para avisar que recargue
reload_flag = False

class ChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        global reload_flag
        if event.src_path.endswith(".py"):
            print(f"⚡ Detectado cambio: {event.src_path}")
            reload_flag = True

# Observador de archivos
observer = Observer()
observer.schedule(ChangeHandler(), UI_FOLDER, recursive=True)
observer.start()

# Crear la app
app = QApplication(sys.argv)

# Importar dashboard
import ui.dashboard_main_ui as dashboard_ui
window = dashboard_ui.DashboardWindow(user_data)
window.show()

def watch_reload():
    """Bucle que revisa si hay cambios y recarga la ventana"""
    global reload_flag, window, dashboard_ui
    while True:
        time.sleep(0.5)
        if reload_flag:
            try:
                print("♻️ Recargando dashboard...")
                # Cierra ventana vieja
                window.close()
                importlib.reload(dashboard_ui)
                # Crea nueva ventana
                window = dashboard_ui.DashboardWindow(user_data)
                window.show()
                reload_flag = False
            except Exception as e:
                print(f"❌ Error recargando: {e}")

# Hilo que vigila cambios
thread = Thread(target=watch_reload, daemon=True)
thread.start()

sys.exit(app.exec())
