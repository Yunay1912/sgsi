# -*- coding: utf-8 -*-
"""
api_client.py
Cliente Python para comunicación con servicios C#
"""

import requests
import json
from typing import Optional, List, Dict, Any

class AsambleaApiClient:
    def __init__(self, base_url: str = "http://localhost:5000/api"):
        self.base_url = base_url
        self.session = requests.Session()

    # ==================== BOLETAS ====================
    
    def crear_boleta(self, numero_boleta: str, extension: Optional[str], 
                     nombre_usuario: str, **kwargs) -> Optional[int]:
        """Crea boleta en BD vía API C#"""
        try:
            data = {
                "numeroBoleta": numero_boleta,
                "extension": extension,
                "nombreUsuario": nombre_usuario,
                "paginas": kwargs.get("paginas", 0),
                "servicios": kwargs.get("servicios", {}),
                "copiasColor": kwargs.get("copias_color", 0),
                "copiasBN": kwargs.get("copias_bn", 0),
                "cantidadDocumentos": kwargs.get("cantidad_documentos", 0),
                "empaste": kwargs.get("empaste", {}),
                "observaciones": kwargs.get("observaciones"),
                "dia": kwargs.get("dia"),
                "meta": kwargs.get("meta", {})
            }
            
            resp = self.session.post(f"{self.base_url}/boletas", json=data, timeout=10)
            resp.raise_for_status()
            print(f"✅ Boleta {numero_boleta} creada vía API C#")
            return resp.json()
        except Exception as e:
            print(f"❌ Error API crear_boleta: {e}")
            return None

    def listar_boletas(self, limit: int = 500) -> List[Dict[str, Any]]:
        """Lista boletas activas"""
        try:
            resp = self.session.get(f"{self.base_url}/boletas?limit={limit}", timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"❌ Error API listar_boletas: {e}")
            return []

    def actualizar_estado(self, numero_boleta: str, nuevo_estado: str, 
                         operador: Optional[str] = None) -> bool:
        """Actualiza estado de boleta"""
        try:
            data = {"nuevoEstado": nuevo_estado, "operador": operador}
            resp = self.session.put(
                f"{self.base_url}/boletas/{numero_boleta}/estado", 
                json=data, 
                timeout=10
            )
            resp.raise_for_status()
            print(f"✅ Estado actualizado: {numero_boleta} → {nuevo_estado}")
            return True
        except Exception as e:
            print(f"❌ Error API actualizar_estado: {e}")
            return False

    def rechazar_boleta(self, numero_boleta: str, extension: str, 
                       comentario: str) -> bool:
        """Rechaza y elimina boleta"""
        try:
            data = {"extension": extension, "comentario": comentario}
            resp = self.session.delete(
                f"{self.base_url}/boletas/{numero_boleta}", 
                json=data, 
                timeout=10
            )
            resp.raise_for_status()
            print(f"✅ Boleta {numero_boleta} rechazada")
            return True
        except Exception as e:
            print(f"❌ Error API rechazar_boleta: {e}")
            return False

    def marcar_cerrado(self, numero_boleta: str) -> bool:
        """Marca boleta como cerrada"""
        try:
            resp = self.session.post(
                f"{self.base_url}/boletas/{numero_boleta}/cerrar", 
                timeout=10
            )
            resp.raise_for_status()
            return True
        except Exception as e:
            print(f"❌ Error API marcar_cerrado: {e}")
            return False

    # ==================== NOTIFICACIONES ====================
    
    def play_sound(self, sound_key: str):
        """Reproduce sonido Windows nativo"""
        try:
            self.session.post(
                f"{self.base_url}/notificaciones/sound",
                json={"soundKey": sound_key},
                timeout=5
            )
        except Exception as e:
            print(f"❌ Error API play_sound: {e}")

    def show_toast(self, title: str, message: str):
        """Muestra notificación Toast Windows"""
        try:
            self.session.post(
                f"{self.base_url}/notificaciones/toast",
                json={"title": title, "message": message},
                timeout=5
            )
        except Exception as e:
            print(f"❌ Error API show_toast: {e}")

    def notificar_login_fail(self):
        """Notifica fallo de login"""
        try:
            self.session.post(f"{self.base_url}/notificaciones/login-fail", timeout=5)
        except Exception as e:
            print(f"❌ Error API login_fail: {e}")

    # ==================== AUDITORÍA ====================
    
    def registrar_auditoria(self, extension: Optional[str], accion: str, 
                           detalle: Optional[str] = None) -> Optional[int]:
        """Registra evento en auditoría"""
        try:
            data = {"extension": extension, "accion": accion, "detalle": detalle}
            resp = self.session.post(f"{self.base_url}/auditoria", json=data, timeout=5)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"❌ Error API auditoria: {e}")
            return None
