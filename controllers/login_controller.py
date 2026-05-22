# -*- coding: utf-8 -*-
"""
controllers/login_controller.py
🔐 Controlador REAL de login conectado a PostgreSQL.
Versión CORREGIDA - Compatible con DashboardWindow
"""

import sys
import os
import traceback
from PySide6.QtWidgets import QMessageBox, QLineEdit
from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from db.usuarios import verificar_credenciales, obtener_usuario_por_usuario


class LoginControllerReal:
    def __init__(self, login_ui):
        self.ui = login_ui
        self.mostrar_contrasena = False
        self.usuario_actual = None
        self.rol_actual = None

        # Eventos UI
        self.ui.btn_ingresar.clicked.connect(self.login)
        self.ui.btn_ver_contrasena.clicked.connect(self.toggle_password)
        self.ui.txt_usuario.returnPressed.connect(self.login)
        self.ui.txt_contrasena.returnPressed.connect(self.login)

    # ----------------------------------------------------
    # Alternar visibilidad de la contraseña
    # ----------------------------------------------------
    def toggle_password(self):
        self.mostrar_contrasena = not self.mostrar_contrasena
        modo = QLineEdit.EchoMode.Normal if self.mostrar_contrasena else QLineEdit.EchoMode.Password
        icono = "assets/ojo_abierto.png" if self.mostrar_contrasena else "assets/ojo_cerrado.png"
        self.ui.txt_contrasena.setEchoMode(modo)
        self.ui.btn_ver_contrasena.setIcon(QIcon(icono))

    # ----------------------------------------------------
    # Intentar iniciar sesión
    # ----------------------------------------------------
    def login(self):
        usuario = self.ui.txt_usuario.text().strip()
        contrasena = self.ui.txt_contrasena.text().strip()

        if not usuario or not contrasena:
            self.mostrar_mensaje_error("⚠️ Por favor, complete todos los campos.")
            return

        self.ui.btn_ingresar.setEnabled(False)
        self.ui.lbl_mensaje.setText("Verificando credenciales...")
        self.ui.lbl_mensaje.setStyleSheet("color: #4CAF50; font-size: 14px;")

        QTimer.singleShot(300, lambda: self._validar_credenciales(usuario, contrasena))

    # ----------------------------------------------------
    # Validar credenciales reales
    # ----------------------------------------------------
    def _validar_credenciales(self, usuario, contrasena):
        try:
            datos_usuario = verificar_credenciales(usuario, contrasena)
            if not datos_usuario:
                self._login_fallido("❌ Usuario o contraseña incorrectos.")
                return

            self.usuario_actual = datos_usuario.get("usuario")
            self.rol_actual = datos_usuario.get("rol") or datos_usuario.get("rol_id")
            nombre = datos_usuario.get("nombre_completo", "Usuario")

            self.ui.lbl_mensaje.setText(f"✅ ¡Bienvenido, {nombre}!")
            self.ui.lbl_mensaje.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 14px;")

            QTimer.singleShot(800, lambda: self._abrir_dashboard(datos_usuario))

        except Exception as e:
            self._login_fallido(f"❌ Error al validar credenciales: {str(e)}")
            print(traceback.format_exc())

    # ----------------------------------------------------
    # Abrir dashboard principal - CORREGIDO
    # ----------------------------------------------------
    def _abrir_dashboard(self, datos_usuario: dict):
        try:
            from db.conexion import crear_conexion
            from controllers.dashboard_controller import DashboardController
            from ui.dashboard_main_ui import DashboardWindow

            # Cerrar login
            self.ui.close()

            # Crear conexión
            conexion = crear_conexion()
            if not conexion:
                QMessageBox.warning(None, "Conexión DB", 
                    "No se pudo crear conexión a la base de datos. "
                    "El Dashboard funcionará en modo limitado.")

            # ✅ CORRECCIÓN: Preparar usuario_data en el formato correcto
            usuario_data = {
                "extension": datos_usuario.get("extension", ""),
                "nombre": datos_usuario.get("nombre", "Usuario"),
                "rol": datos_usuario.get("rol", "usuario"),
                "nombre_completo": datos_usuario.get("nombre_completo", "Usuario"),
                "usuario": datos_usuario.get("usuario", "")
            }

            print(f"[DEBUG] Creando dashboard con usuario_data: {usuario_data}")

            # ✅ Instanciar dashboard CON EL FORMATO CORRECTO
            dashboard = DashboardWindow(usuario_data)

            # ✅ Instanciar y conectar el controlador
            try:
                controller = DashboardController(conexion, dashboard, usuario_data)
                dashboard.set_controller(controller)
                print("[✓] Controller conectado al dashboard")
            except Exception as e:
                print(f"[WARN] No se pudo inicializar DashboardController: {e}")
                print(traceback.format_exc())
                QMessageBox.warning(None, "Advertencia", 
                    f"Dashboard iniciado en modo limitado:\n{e}")

            # Mostrar dashboard
            dashboard.showMaximized()
            self.dashboard = dashboard
            
            print(f"[DEBUG] ✅ Dashboard abierto: {usuario_data.get('usuario')} ({usuario_data.get('rol')})")

        except ImportError as e:
            self._login_fallido(f"❌ No se pudo importar el Dashboard: {e}")
            print(traceback.format_exc())
            QMessageBox.critical(None, "Error de importación",
                f"No se encontró dashboard_main_ui.py:\n{e}\n\n"
                "Verifica que el archivo exista en la carpeta 'ui/'")

        except Exception as e:
            self._login_fallido(f"❌ Error al abrir dashboard: {e}")
            print(traceback.format_exc())
            QMessageBox.critical(None, "Error",
                f"Error inesperado al abrir dashboard:\n{e}")

    # ----------------------------------------------------
    # Mensaje de error o fallo en login
    # ----------------------------------------------------
    def _login_fallido(self, mensaje):
        self.mostrar_mensaje_error(mensaje)
        self.ui.btn_ingresar.setEnabled(True)

    # ----------------------------------------------------
    # Mostrar mensaje de error en pantalla
    # ----------------------------------------------------
    def mostrar_mensaje_error(self, mensaje):
        self.ui.lbl_mensaje.setText(mensaje)
        self.ui.lbl_mensaje.setStyleSheet("color: #ff6b6b; font-weight: bold; font-size: 14px;")
        QTimer.singleShot(4000, lambda: self.ui.lbl_mensaje.setText(""))