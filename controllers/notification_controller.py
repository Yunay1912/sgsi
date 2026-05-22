# -*- coding: utf-8 -*-
"""
controllers/notification_controller.py - ACTUALIZADO
Usa API C# para notificaciones nativas Windows
"""
import requests

API_BASE = "http://localhost:5555/api"

class NotificationController:
    def __init__(self, ui=None, settings_path=None):
        self.ui = ui
        self.settings = self._load_settings()

    def _load_settings(self):
        """Cargar configuración desde BD via API"""
        return {
            "notificaciones_activas": True,
            "sonido_nueva_boleta": True,
            "sonido_rechazo": True
        }

    def _play(self, key: str):
        """Reproduce sonido vía API C#"""
        if not self.settings.get(f"sonido_{key.replace('_', '_')}", True):
            return
        
        try:
            requests.post(f"{API_BASE}/notificaciones/sound", 
                         json={"key": key}, timeout=3)
        except Exception as e:
            print(f"⚠️ Sound: {e}")

    def _show_ui_notification(self, title: str, message: str):
        """Toast Windows nativo"""
        if not self.settings.get("notificaciones_activas", True):
            return
        
        try:
            requests.post(f"{API_BASE}/notificaciones/toast", 
                         json={"title": title, "message": message}, timeout=3)
        except Exception as e:
            print(f"⚠️ Toast: {e}")

    def notificar_nueva_boleta(self, numero_boleta: str, extension: str = None, meta: dict = None):
        """Notifica nueva boleta con sonido"""
        self._play("new_boleta")
        self._show_ui_notification("Nueva Boleta", 
                                   f"{numero_boleta} de {extension or 'usuario'}")

    def notificar_rechazo(self, extension: str, numero_boleta: str, comentario: str):
        """Notifica rechazo con sonido"""
        self._play("reject")
        self._show_ui_notification("Rechazada", f"{numero_boleta}: {comentario}")

    def notificar_cambio_estado(self, extension: str, numero_boleta: str, nuevo_estado: str):
        """Notifica cambio de estado"""
        if nuevo_estado.lower() == "listo":
            self._play("new_boleta")
        self._show_ui_notification(f"Estado: {nuevo_estado}", 
                                   f"{numero_boleta} → {nuevo_estado}")

    def notificar_login_fail(self, usuario: str):
        """Notifica fallo de login"""
        self._play("login_fail")

    def actualizar_configuracion(self, extension: str, config: dict):
        """Actualiza configuración de notificaciones"""
        self.settings.update(config)

    def save_settings(self):
        """Guarda configuración en BD"""
        pass