# -*- coding: utf-8 -*-
"""
db/boletas.py - ACTUALIZADO
Usa servicio Windows C# para operaciones DB
"""
import requests
import json
from typing import Optional, List, Dict, Any

API_BASE = "http://localhost:5555/api"

def insertar(conn, numero_boleta: str, extension: Optional[str], nombre_usuario: str, 
             paginas: int = 0, servicios: Optional[dict] = None, copias_color: int = 0,
             copias_bn: int = 0, cantidad_documentos: int = 0, empaste: Optional[dict] = None,
             observaciones: Optional[str] = None, dia: Optional[str] = None,
             operador_responsable: Optional[str] = None, meta: Optional[dict] = None) -> Optional[int]:
    """Inserta boleta vía servicio Windows"""
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
        resp = requests.post(f"{API_BASE}/boletas", json=data, timeout=10)
        resp.raise_for_status()
        return resp.json().get("id")
    except Exception as e:
        print(f"❌ Error insertar: {e}")
        return None

def listar(conn, limit: int = 500) -> List[Dict[str, Any]]:
    """Lista boletas activas"""
    try:
        resp = requests.get(f"{API_BASE}/boletas?limit={limit}", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"❌ Error listar: {e}")
        return []

def obtener_solicitudes(conn) -> List[Dict[str, Any]]:
    return listar(conn)

def obtener_por_dia(conn, dia: str) -> List[Dict[str, Any]]:
    boletas = listar(conn)
    return [b for b in boletas if b.get("dia") == dia]

def buscar(conn, q: str) -> List[Dict[str, Any]]:
    boletas = listar(conn)
    q_lower = q.lower()
    return [b for b in boletas if q_lower in str(b.get("numero_boleta", "")).lower() 
            or q_lower in str(b.get("extension", "")).lower()
            or q_lower in str(b.get("nombre_usuario", "")).lower()]

def actualizar_estado(conn, numero_boleta: str, nuevo_estado: str, operador: Optional[str] = None) -> bool:
    """Actualiza estado vía servicio"""
    try:
        data = {"estado": nuevo_estado, "operador": operador}
        resp = requests.put(f"{API_BASE}/boletas/{numero_boleta}/estado", json=data, timeout=10)
        resp.raise_for_status()
        print(f"✅ {numero_boleta} → {nuevo_estado}")
        return True
    except Exception as e:
        print(f"❌ Error actualizar: {e}")
        return False

def rechazar(conn, numero_boleta: str, extension: str, comentario: str) -> bool:
    """Rechaza boleta vía servicio"""
    try:
        resp = requests.delete(f"{API_BASE}/boletas/{numero_boleta}", timeout=10)
        resp.raise_for_status()
        print(f"✅ {numero_boleta} rechazado")
        return True
    except Exception as e:
        print(f"❌ Error rechazar: {e}")
        return False

def marcar_cerrado(conn, numero_boleta: str) -> bool:
    # Implementar si es necesario
    return True

def exportar_todas(conn) -> List[Dict[str, Any]]:
    return listar(conn, limit=10000)

def ocultar_listas(conn) -> int:
    # Implementar si es necesario
    return 0
