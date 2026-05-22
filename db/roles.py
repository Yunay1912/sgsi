# -*- coding: utf-8 -*-
"""
db/roles.py
CRUD para tabla 'roles'.
"""
import logging
from db.conexion import crear_conexion
from psycopg2.extras import RealDictCursor

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def crear_rol(name, description=None):
    conn = crear_conexion()
    if not conn:
        return False
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO roles (name, description) VALUES (%s, %s) ON CONFLICT (name) DO NOTHING",
                (name, description)
            )
            conn.commit()
            log.info(f"Rol '{name}' creado correctamente.")
            return True
    except Exception as e:
        conn.rollback()
        log.exception(f"Error creando rol '{name}': {e}")
        return False
    finally:
        conn.close()


def listar_roles():
    conn = crear_conexion()
    if not conn:
        return []
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, name, description, created_at FROM roles ORDER BY id ASC")
            return cur.fetchall()
    except Exception as e:
        log.exception(f"Error al listar roles: {e}")
        return []
    finally:
        conn.close()


def obtener_rol_por_nombre(name):
    conn = crear_conexion()
    if not conn:
        return None
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM roles WHERE name = %s", (name,))
            return cur.fetchone()
    except Exception as e:
        log.exception(f"Error al obtener rol '{name}': {e}")
        return None
    finally:
        conn.close()


def eliminar_rol(rol_id):
    conn = crear_conexion()
    if not conn:
        return False
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM roles WHERE id = %s", (rol_id,))
            conn.commit()
            return True
    except Exception as e:
        conn.rollback()
        log.exception(f"Error al eliminar rol: {e}")
        return False
    finally:
        conn.close()
