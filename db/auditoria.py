# -*- coding: utf-8 -*-
"""
db/auditoria.py - ACTUALIZADO
Usa servicio Windows C#
"""
import requests
from typing import List, Dict, Any, Optional

API_BASE = "http://localhost:5555/api"

def obtener_todos(conn) -> List[Dict[str, Any]]:
    # Implementar si necesario
    return []

def buscar_por_extension(conn, extension: str) -> List[Dict[str, Any]]:
    return []

def insertar_registro(conn, fecha: str, extension: Optional[str], accion: str, detalle: Optional[str] = None) -> Optional[int]:
    """Registra auditoría vía servicio"""
    try:
        data = {"extension": extension, "accion": accion, "detalle": detalle}
        resp = requests.post(f"{API_BASE}/auditoria", json=data, timeout=5)
        resp.raise_for_status()
        return resp.json().get("id")
    except Exception as e:
        print(f"⚠️ Auditoría: {e}")
        return None