# db/test_dashboard_controller.py
import sys
from PySide6.QtWidgets import QApplication
from controllers.dashboard_controller import DashboardWindow

if __name__ == "__main__":
    # Cambia el rol aquí para probar: "usuario", "operador", "encargado", "admin", "jefa"
    role = "admin"

    app = QApplication(sys.argv)
    user = {
        "extension": "2101",
        "usuario": "Carlos Rojas",
        "rol": role
    }
    w = DashboardWindow(user)
    w.show()
    sys.exit(app.exec())
