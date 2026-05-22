# -*- coding: utf-8 -*-
"""
usuarios.py — Versión adaptada al formato Claudie.
Incluye soporte para campo 'extension', roles y verificación de sesión.
"""

import logging
from typing import Optional, Dict, List
from psycopg2.extras import RealDictCursor
from db.conexion import crear_conexion

# Configuración de logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# =====================================================
# 🔐 Verificar credenciales (login)
# =====================================================
def verificar_credenciales(usuario: str, password: str) -> Optional[Dict]:
    """
    Verifica si las credenciales son correctas.
    Retorna un diccionario con los datos del usuario si existe y está activo.
    """
    conn = crear_conexion()
    if not conn:
        log.error("❌ No se pudo conectar a la base de datos.")
        return None

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    u.usuario,
                    u.nombre_completo,
                    u.extension,
                    u.rol_id,
                    r.nombre AS rol
                FROM usuarios u
                LEFT JOIN roles r ON r.id = u.rol_id
                WHERE u.usuario = %s
                  AND u.activo = TRUE
                  AND (
                        u.password = %s
                        OR u.password = crypt(%s, u.password)
                      )
                LIMIT 1
            """, (usuario, password, password))
            
            row = cur.fetchone()
            if row:
                log.info(f"✅ Usuario '{usuario}' autenticado correctamente.")
                return dict(row)
            else:
                log.warning(f"⚠️ Credenciales inválidas para '{usuario}'.")
                return None

    except Exception as e:
        log.exception(f"Error al verificar credenciales: {e}")
        return None
    finally:
        try:
            conn.close()
        except Exception:
            pass


# =====================================================
# 📋 Obtener información del usuario por nombre
# =====================================================
def obtener_usuario_por_usuario(usuario: str) -> Optional[Dict]:
    """
    Obtiene los datos completos de un usuario por su nombre.
    """
    conn = crear_conexion()
    if not conn:
        return None

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    u.usuario,
                    u.nombre_completo,
                    u.extension,
                    u.rol_id,
                    r.nombre AS rol,
                    u.activo,
                    u.creado_ts
                FROM usuarios u
                LEFT JOIN roles r ON r.id = u.rol_id
                WHERE u.usuario = %s
                LIMIT 1
            """, (usuario,))
            row = cur.fetchone()
            return dict(row) if row else None
    except Exception as e:
        log.exception(f"Error al obtener usuario: {e}")
        return None
    finally:
        try:
            conn.close()
        except Exception:
            pass


# =====================================================
# ➕ Crear nuevo usuario
# =====================================================
def crear_usuario(usuario: str, password: str, rol_id: int, nombre_completo: str, extension: Optional[str] = None) -> bool:
    """
    Crea un nuevo usuario activo.
    Compatible con PostgreSQL (pgcrypto).
    """
    conn = crear_conexion()
    if not conn:
        return False

    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO usuarios (usuario, nombre_completo, extension, rol_id, password, activo)
                VALUES (%s, %s, %s, %s, crypt(%s, gen_salt('bf')), TRUE)
            """, (usuario, nombre_completo, extension, rol_id, password))
            conn.commit()
            log.info(f"✅ Usuario '{usuario}' creado correctamente.")
            return True
    except Exception as e:
        log.exception(f"Error al crear usuario: {e}")
        try:
            conn.rollback()
        except Exception:
            pass
        return False
    finally:
        try:
            conn.close()
        except Exception:
            pass


# =====================================================
# 📜 Listar todos los usuarios
# =====================================================
def listar_usuarios() -> List[Dict]:
    """
    Devuelve una lista de todos los usuarios y sus roles.
    """
    conn = crear_conexion()
    if not conn:
        return []

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    u.usuario,
                    u.nombre_completo,
                    u.extension,
                    r.nombre AS rol,
                    u.activo,
                    u.creado_ts
                FROM usuarios u
                LEFT JOIN roles r ON r.id = u.rol_id
                ORDER BY u.creado_ts DESC
            """)
            return cur.fetchall()
    except Exception as e:
        log.exception(f"Error al listar usuarios: {e}")
        return []
    finally:
        try:
            conn.close()
        except Exception:
            pass
