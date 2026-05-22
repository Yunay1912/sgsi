# -*- coding: utf-8 -*-
"""
controllers/solicitudes_controller.py - ACTUALIZADO
Gestión completa de solicitudes con notificaciones y auditoría
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import traceback
import requests

API_BASE = "http://localhost:5555/api"

class SolicitudesController:
    def __init__(self, conexion, ui=None, auditoria_ctrl=None, notification_ctrl=None):
        self.conexion = conexion  # Mantener para compatibilidad
        self.ui = ui
        self.auditoria = auditoria_ctrl
        self.notification = notification_ctrl
    
    def listar(self) -> List[Dict[str, Any]]:
        """Lista boletas activas vía API"""
        try:
            resp = requests.get(f"{API_BASE}/boletas", timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"❌ Error listar: {e}")
            return []

    def obtener_solicitudes(self) -> List[Dict[str, Any]]:
        return self.listar()

    def obtener_por_dia(self, dia: str) -> List[Dict[str, Any]]:
        boletas = self.listar()
        return [b for b in boletas if b.get("dia") == dia]

    def buscar(self, q: str) -> List[Dict[str, Any]]:
        boletas = self.listar()
        q_lower = q.lower()
        return [b for b in boletas if q_lower in str(b.get("numero_boleta", "")).lower() 
                or q_lower in str(b.get("extension", "")).lower()
                or q_lower in str(b.get("nombre_usuario", "")).lower()]
    
    def crear_solicitud(self, numero_boleta: str, extension: Optional[str],
                        nombre_usuario: str, paginas: int = 0, servicios: Optional[dict] = None,
                        copias_color: int = 0, copias_bn: int = 0, cantidad_documentos: int = 0,
                        empaste: Optional[dict] = None, observaciones: Optional[str] = None,
                        dia: Optional[str] = None, meta: Optional[dict] = None) -> Optional[int]:
        """Crea boleta y notifica automáticamente a operadores y admin"""
        try:
            data = {
                "numeroBoleta": numero_boleta,
                "extension": extension,
                "nombreUsuario": nombre_usuario,
                "paginas": paginas,
                "servicios": servicios or {},
                "copiasColor": copias_color,
                "copiasBN": copias_bn,
                "cantidadDocumentos": cantidad_documentos,
                "empaste": empaste or {},
                "observaciones": observaciones,
                "dia": dia,
                "meta": meta or {}
            }
            
            # Crear boleta vía API
            resp = requests.post(f"{API_BASE}/boletas", json=data, timeout=10)
            resp.raise_for_status()
            boleta_id = resp.json().get("id")
            
            if boleta_id:
                # Auditoría
                try:
                    requests.post(f"{API_BASE}/auditoria", 
                                json={"extension": extension or "unknown", 
                                     "accion": "crear_boleta",
                                     "detalle": f"{numero_boleta} creado por {nombre_usuario}"}, 
                                timeout=5)
                except:
                    pass
                
                # ✅ NOTIFICAR AUTOMÁTICAMENTE A OPERADORES Y ADMIN
                try:
                    requests.post(f"{API_BASE}/notificaciones/notify-operators",
                                json={
                                    "numeroBoleta": numero_boleta,
                                    "mensaje": f"Nueva boleta de {nombre_usuario}"
                                }, timeout=5)
                    print(f"✅ Notificados operadores y admin: {numero_boleta}")
                except Exception as e:
                    print(f"⚠️ Error notificando: {e}")
                
                # Notificación local (opcional)
                if self.notification:
                    self.notification.notificar_nueva_boleta(numero_boleta, extension, meta)
            
            return boleta_id
        except Exception as e:
            print(f"❌ Error crear solicitud: {e}")
            traceback.print_exc()
            return None
    
    def actualizar_estado(self, numero_boleta: str, nuevo_estado: str, 
                         operador: Optional[str] = None, 
                         motivo_modificacion: Optional[str] = None) -> bool:
        """Actualiza estado con auditoría de modificaciones"""
        try:
            data = {"estado": nuevo_estado, "operador": operador}
            resp = requests.put(f"{API_BASE}/boletas/{numero_boleta}/estado", 
                              json=data, timeout=10)
            resp.raise_for_status()
            
            # ✅ REGISTRAR MODIFICACIÓN SI HAY MOTIVO
            if motivo_modificacion:
                try:
                    modificacion = {
                        "fecha": datetime.now().isoformat(),
                        "usuario": operador,
                        "accion": f"estado → {nuevo_estado}",
                        "motivo": motivo_modificacion
                    }
                    # Guardar en campo modificaciones JSONB
                    requests.post(f"{API_BASE}/boletas/{numero_boleta}/registrar-modificacion",
                                json=modificacion, timeout=5)
                except:
                    pass
            
            # Auditoría
            try:
                requests.post(f"{API_BASE}/auditoria",
                            json={
                                "extension": operador or "unknown",
                                "accion": "cambio_estado",
                                "detalle": f"{numero_boleta} → {nuevo_estado}" + 
                                          (f" (Motivo: {motivo_modificacion})" if motivo_modificacion else "")
                            }, timeout=5)
            except:
                pass
            
            # Notificar cambio de estado
            if nuevo_estado.lower() == "listo":
                try:
                    # Obtener extensión del solicitante
                    boletas = self.listar()
                    boleta = next((b for b in boletas if b.get("numero_boleta") == numero_boleta), None)
                    if boleta and boleta.get("extension"):
                        requests.post(f"{API_BASE}/notificaciones/toast",
                                    json={
                                        "title": "Boleta Lista",
                                        "message": f"{numero_boleta} está lista para recoger"
                                    }, timeout=3)
                except:
                    pass
            
            print(f"✅ Estado actualizado: {numero_boleta} → {nuevo_estado}")
            return True
            
        except Exception as e:
            print(f"❌ Error actualizar estado: {e}")
            return False
    
    def rechazar_boleta(self, numero_boleta: str, extension: Optional[str], 
                       comentario: str) -> bool:
        """Rechaza boleta con notificación de sonido"""
        try:
            resp = requests.delete(f"{API_BASE}/boletas/{numero_boleta}", timeout=10)
            resp.raise_for_status()
            
            # Auditoría
            try:
                requests.post(f"{API_BASE}/auditoria",
                            json={
                                "extension": extension or "unknown",
                                "accion": "rechazar_boleta",
                                "detalle": f"{numero_boleta}: {comentario}"
                            }, timeout=5)
            except:
                pass
            
            # ✅ SONIDO DE RECHAZO (automático en API C#)
            # El endpoint DELETE ya reproduce reject.wav
            
            # Toast notification
            try:
                requests.post(f"{API_BASE}/notificaciones/toast",
                            json={
                                "title": "Boleta Rechazada",
                                "message": f"{numero_boleta}: {comentario}"
                            }, timeout=3)
            except:
                pass
            
            print(f"✅ Rechazado: {numero_boleta}")
            return True
            
        except Exception as e:
            print(f"❌ Error rechazar: {e}")
            return False
    
    def enviar_a_cierre(self, numero_boleta: str, enviado_por: str) -> bool:
        """Envía boleta a cierre (disponible para encargado)"""
        try:
            resp = requests.post(f"{API_BASE}/boletas/{numero_boleta}/enviar-cierre",
                                json={"enviadoPor": enviado_por}, timeout=10)
            resp.raise_for_status()
            
            # Auditoría
            try:
                requests.post(f"{API_BASE}/auditoria",
                            json={
                                "extension": enviado_por,
                                "accion": "enviar_cierre",
                                "detalle": f"{numero_boleta} enviado a cierre"
                            }, timeout=5)
            except:
                pass
            
            print(f"✅ Enviado a cierre: {numero_boleta}")
            return True
            
        except Exception as e:
            print(f"❌ Error enviar a cierre: {e}")
            return False