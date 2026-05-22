# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QWidget,
    QVBoxLayout, QHBoxLayout, QToolButton, QGraphicsDropShadowEffect, QMessageBox
)
from PySide6.QtGui import QPixmap, QCursor, QIcon, QColor, QPainter, QBrush
from PySide6.QtCore import Qt, QSize, QTimer
import sys
import os


# ===============================
# === DATOS DE PRUEBA (SOLO PARA DESARROLLO) ===
# ===============================
DATOS_PRUEBA = {
    "admin": {
        "password": "admin123",
        "rol": "admin",
        "nombre": "Administrador del Sistema"
    },
    "operador": {
        "password": "operador123",
        "rol": "operador",
        "nombre": "Juan Pérez Operador"
    },
    "usuario": {
        "password": "usuario123",
        "rol": "usuario",
        "nombre": "María García Usuario"
    },
    "encargado": {
        "password": "encargado123",
        "rol": "encargado",
        "nombre": "Carlos Rodríguez Encargado"
    }
}


# ===============================
# === CONTROLADOR DE LOGIN (MODO PRUEBA) ===
# ===============================
class LoginController:
    """
    Controlador interno con datos de prueba.
    Se usa cuando no existe login_controller.py externo.
    """
    def __init__(self, ui):
        self.ui = ui
        self.ui.btn_ingresar.clicked.connect(self.login)
        self.ui.btn_ver_contrasena.clicked.connect(self.toggle_password)
        self.mostrar_contrasena = False
        self.modo_prueba = True

    def toggle_password(self):
        """Alterna la visibilidad de la contraseña."""
        if self.mostrar_contrasena:
            self.ui.txt_contrasena.setEchoMode(QLineEdit.EchoMode.Password)
            self.ui.btn_ver_contrasena.setIcon(QIcon("assets/ojo_cerrado.png"))
        else:
            self.ui.txt_contrasena.setEchoMode(QLineEdit.EchoMode.Normal)
            self.ui.btn_ver_contrasena.setIcon(QIcon("assets/ojo_abierto.png"))
        self.mostrar_contrasena = not self.mostrar_contrasena

    def login(self):
        """Procesa el login con datos de prueba."""
        usuario = self.ui.txt_usuario.text().strip().lower()
        contrasena = self.ui.txt_contrasena.text().strip()

        if not usuario or not contrasena:
            self.ui.lbl_mensaje.setText("Por favor, complete todos los campos.")
            self.ui.lbl_mensaje.setStyleSheet("color: #ff6b6b;")
            return

        self.ui.btn_ingresar.setEnabled(False)
        self.ui.lbl_mensaje.setText("Verificando credenciales...")
        self.ui.lbl_mensaje.setStyleSheet("color: #4CAF50;")
        
        # Simular delay de red
        QTimer.singleShot(500, lambda: self._validar_prueba(usuario, contrasena))
    
    def _validar_prueba(self, usuario, contrasena):
        """Valida contra datos de prueba."""
        if usuario not in DATOS_PRUEBA:
            self.ui.lbl_mensaje.setText("❌ Usuario no encontrado.")
            self.ui.lbl_mensaje.setStyleSheet("color: #ff6b6b; font-weight: bold;")
            self.ui.btn_ingresar.setEnabled(True)
            return
        
        if DATOS_PRUEBA[usuario]["password"] != contrasena:
            self.ui.lbl_mensaje.setText("❌ Contraseña incorrecta.")
            self.ui.lbl_mensaje.setStyleSheet("color: #ff6b6b; font-weight: bold;")
            self.ui.btn_ingresar.setEnabled(True)
            return
        
        # ✅ Login exitoso
        nombre = DATOS_PRUEBA[usuario]["nombre"]
        rol = DATOS_PRUEBA[usuario]["rol"]
        self.ui.lbl_mensaje.setText(f"✅ ¡Bienvenido, {nombre}!")
        self.ui.lbl_mensaje.setStyleSheet("color: #4CAF50; font-weight: bold;")
        
        # Abrir dashboard
        QTimer.singleShot(800, lambda: self._abrir_dashboard(usuario, rol, nombre))
    
    def _abrir_dashboard(self, usuario, rol, nombre):
        """Intenta abrir el dashboard."""
        try:
            # Agregar ruta del dashboard al path si es necesario
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
            
            from dashboard_main_ui import DashboardWindow
            
            self.dashboard = DashboardWindow(usuario=usuario, rol=rol, nombre_completo=nombre)
            # Mostrar dashboard sin parpadeos
            self.ui.hide()
            QTimer.singleShot(250, lambda: (
                self.dashboard.show(),
                self.ui.close()
            ))

            
        except ImportError as e:
            self.ui.lbl_mensaje.setText("Dashboard no encontrado")
            self.ui.lbl_mensaje.setStyleSheet("color: #ff9800;")
            self.ui.btn_ingresar.setEnabled(True)

            QMessageBox.warning(
                self.ui,
                "Dashboard no encontrado",
                f"No se pudo importar dashboard_main_ui.py\n\nError: {str(e)}\n\nAsegúrate de que el archivo exista en la misma carpeta."
            )
            
        except Exception as e:
            self.ui.lbl_mensaje.setText(f"❌ Error: {str(e)}")
            self.ui.lbl_mensaje.setStyleSheet("color: #ff6b6b;")
            self.ui.btn_ingresar.setEnabled(True)
            
            QMessageBox.critical(
                self.ui,
                "Error al abrir dashboard",
                f"Error inesperado:\n{str(e)}"
            )


# ===============================
# === CONTENEDOR GLASS ==========
# ===============================
class GlassContainer(QWidget):
    """Panel con efecto vidrio real."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 160))
        self.setGraphicsEffect(shadow)

        self.setMinimumSize(420, 300)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor(50, 50, 50, 70)
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 18, 18)


# ===============================
# === INTERFAZ DE LOGIN =========
# ===============================
class LoginUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Acceso")
        self.resize(1200, 800)
        self.setWindowState(Qt.WindowState.WindowMaximized)

        # Imagen de fondo
        self.background = QPixmap("assets/login.png")

        # Widget central
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Contenedor glass
        contenedor = GlassContainer()
        cont_layout = QVBoxLayout(contenedor)
        cont_layout.setSpacing(18)
        cont_layout.setContentsMargins(40, 40, 40, 40)

        # Título
        lbl_titulo = QLabel("Iniciar Sesión")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_titulo.setStyleSheet("font-size: 22px; font-weight: 700;")
        cont_layout.addWidget(lbl_titulo)

        # Campo usuario
        self.txt_usuario = QLineEdit()
        self.txt_usuario.setPlaceholderText("Usuario")
        self.txt_usuario.setMinimumHeight(46)
        cont_layout.addWidget(self.txt_usuario)

        # Campo contraseña + botón ver
        pwd_wrap = QWidget()
        pwd_layout = QHBoxLayout(pwd_wrap)
        pwd_layout.setContentsMargins(0, 0, 0, 0)
        pwd_layout.setSpacing(0)

        self.txt_contrasena = QLineEdit()
        self.txt_contrasena.setPlaceholderText("Contraseña")
        self.txt_contrasena.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_contrasena.setMinimumHeight(46)
        self.txt_contrasena.setStyleSheet("padding-right: 40px;")

        self.btn_ver_contrasena = QToolButton(self.txt_contrasena)
        self.btn_ver_contrasena.setIcon(QIcon("assets/ojo_cerrado.png"))

        boton_size = 25
        self.btn_ver_contrasena.setFixedSize(boton_size, boton_size)
        self.btn_ver_contrasena.setIconSize(QSize(boton_size - 6, boton_size - 6))
        self.btn_ver_contrasena.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_ver_contrasena.setStyleSheet("""
            QToolButton {
                border: none;
                background-color: rgba(0, 0, 0, 0.25);
                border-radius: 6px;
            }
            QToolButton:hover {
                background-color: rgba(255,255,255,0.15);
            }
        """)

        def ajustar_boton():
            x = self.txt_contrasena.width() - self.btn_ver_contrasena.width() - 6
            y = (self.txt_contrasena.height() - self.btn_ver_contrasena.height()) // 2
            self.btn_ver_contrasena.move(x, y)
            self.btn_ver_contrasena.raise_()

        self.txt_contrasena.resizeEvent = lambda e: ajustar_boton()
        ajustar_boton()

        pwd_layout.addWidget(self.txt_contrasena)
        cont_layout.addWidget(pwd_wrap)

        # Botón ingresar
        self.btn_ingresar = QPushButton("Ingresar")
        self.btn_ingresar.setObjectName("btn_ingresar")
        self.btn_ingresar.setMinimumHeight(46)
        self.btn_ingresar.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        cont_layout.addWidget(self.btn_ingresar)

        # Mensaje
        self.lbl_mensaje = QLabel("")
        self.lbl_mensaje.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_mensaje.setWordWrap(True)
        cont_layout.addWidget(self.lbl_mensaje)

        cont_layout.addStretch()

        # Centrar contenedor
        center_row = QHBoxLayout()
        center_row.addStretch()
        center_row.addWidget(contenedor)
        center_row.addStretch()
        main_layout.addStretch()
        main_layout.addLayout(center_row)
        main_layout.addStretch()

        # Estilos
        self.setStyleSheet("""
        QLineEdit {
            background-color: rgba(0,0,0,0.28);
            border: 1px solid rgba(255,255,255,0.15);
            border-radius: 10px;
            padding: 10px 14px;
            font-size: 15px;
            color: white;
        }
        QLineEdit:focus {
            border: 1px solid #e01430;
            background-color: rgba(0,0,0,0.45);
        }
        QPushButton#btn_ingresar {
            background-color: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #ce1126, stop:1 #e01430);
            border: none;
            border-radius: 10px;
            color: white;
            font-size: 15px;
            font-weight: 600;
        }
        QPushButton#btn_ingresar:hover {
            background-color: #ff1744;
        }
        QPushButton#btn_ingresar:disabled {
            background-color: rgba(100, 100, 100, 0.5);
        }
        QLabel {
            background-color: transparent;
            color: white;
        }
        """)

        # Intentar usar el controlador real
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.dirname(current_dir)  # sube desde /ui a la raíz
            controllers_path = os.path.join(base_dir, 'controllers')

            if controllers_path not in sys.path:
                sys.path.insert(0, controllers_path)

            from login_controller import LoginControllerReal
            self.controller = LoginControllerReal(self)
            print("✅ Controlador real cargado desde /controllers/login_controller.py")

        except Exception as e:
            print(f"⚠️ No se pudo cargar controlador real: {e}")
            from login_controller import LoginControllerReal
            self.controller = LoginControllerReal(self)
            self.controller.modo_prueba = True
            print("⚠️ Usando controlador en modo DEMO (datos de prueba)")

    def paintEvent(self, event):
        """Pinta la imagen de fondo detrás del contenedor glass."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        if not self.background.isNull():
            scaled = self.background.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)


# ===============================
# === EJECUCIÓN =================
# ===============================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginUI()
    window.show()
    sys.exit(app.exec())