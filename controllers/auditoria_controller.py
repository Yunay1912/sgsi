# -*- coding: utf-8 -*-
"""
controllers/auditoria_controller.py

Controller de conveniencia para registrar y consultar auditoría desde la capa de aplicación.
Instanciar con la conexión (psycopg2) y opcionalmente la UI para mostrar mensajes.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import traceback

try:
    from db import auditoria as auditoria_db
except Exception:
    auditoria_db = None

class AuditoriaController:
    def __init__(self, conexion, ui=None):
        self.conexion = conexion
        self.ui = ui
        # fallback en memoria si no hay DB
        self._fallback = []

    def listar(self) -> List[Dict[str, Any]]:
        try:
            if auditoria_db and hasattr(auditoria_db, "obtener_todos"):
                return auditoria_db.obtener_todos(self.conexion)
            return list(self._fallback)
        except Exception:
            traceback.print_exc()
            return list(self._fallback)

    def buscar_por_extension(self, extension: str) -> List[Dict[str, Any]]:
        try:
            if auditoria_db and hasattr(auditoria_db, "buscar_por_extension"):
                return auditoria_db.buscar_por_extension(self.conexion, extension)
            return [r for r in self._fallback if str(r.get("extension","")).lower() == extension.lower()]
        except Exception:
            traceback.print_exc()
            return []

    def registrar(self, extension: Optional[str], accion: str, detalle: Optional[str] = "") -> Optional[int]:
        """
        Registra la acción en DB (si existe) o en fallback.
        Retorna id en DB o None si fallback.
        """
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            if auditoria_db and hasattr(auditoria_db, "insertar_registro"):
                return auditoria_db.insertar_registro(self.conexion, fecha, extension, accion, detalle)
            # fallback: almacenar en memoria
            rec = {"fecha": fecha, "extension": extension, "accion": accion, "detalle": detalle}
            self._fallback.insert(0, rec)
            # opcional: mantener tope
            if len(self._fallback) > 2000:
                self._fallback = self._fallback[:2000]
            return None
        except Exception:
            traceback.print_exc()
            return None
