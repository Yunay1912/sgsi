# db/conexion.py
# -*- coding: utf-8 -*-
"""
Conexión a PostgreSQL para asamblea_app.

Provee:
- crear_conexion(): retorna una conexión psycopg2 o None (si falla).
- obtener_cursor(conn, dict_cursor=True): retorna cursor (RealDictCursor si dict_cursor True).
"""

import os
import traceback
from typing import Optional

# Intento de usar python-dotenv si existe (permite un .env local)
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# leer primero variable de entorno, luego config/settings.py si existe
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    try:
        from config import settings as _s
        DATABASE_URL = getattr(_s, "DATABASE_URL", None)
    except Exception:
        DATABASE_URL = None

def crear_conexion():
    """
    Intenta crear y retornar una conexión psycopg2.
    Retorna None si no puede (y muestra una advertencia).
    """
    try:
        if not DATABASE_URL:
            print("[WARN] No se encontró DATABASE_URL en variables de entorno ni en config/settings.py")
            print("Usa: export DATABASE_URL='postgresql://user:pass@host:port/dbname' (o setx en Windows)")
            return None

        import psycopg2
        # conectar con autocommit False; controller manejará commits
        conn = psycopg2.connect(DATABASE_URL)
        # Opcional: aumentar timeout o application_name si lo deseas
        conn.autocommit = False
        print("[INFO] Conexión a PostgreSQL establecida.")
        return conn
    except Exception as e:
        traceback.print_exc()
        print(f"[WARN] crear_conexion() devolvió None.")
        return None


def obtener_cursor(conn, dict_cursor: bool = True):
    """
    Retorna un cursor. Si dict_cursor=True -> RealDictCursor (columnas como dict).
    Caller debe cerrar cursor (cursor.close()) y manejar commit/rollback en la conexión.
    """
    if conn is None:
        raise RuntimeError("La conexión es None. Llama a crear_conexion() primero.")
    try:
        if dict_cursor:
            from psycopg2.extras import RealDictCursor
            return conn.cursor(cursor_factory=RealDictCursor)
        else:
            return conn.cursor()
    except Exception:
        # relanzar para que quien lo llame capture e imprima
        raise
