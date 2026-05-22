-- unified_schema.sql
-- Schema completo para Asamblea App
-- ============================================

BEGIN;

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================
-- ROLES
-- ============================================
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT,
    creado_ts TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- ============================================
-- USUARIOS
-- ============================================
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(100) NOT NULL UNIQUE,
    nombre_completo VARCHAR(200) NOT NULL,
    extension VARCHAR(32),
    rol_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE RESTRICT,
    password TEXT NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    creado_ts TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_usuarios_extension ON usuarios(extension);
CREATE INDEX IF NOT EXISTS idx_usuarios_activo ON usuarios(activo);

-- ============================================
-- AUDITORÍA
-- ============================================
CREATE TABLE IF NOT EXISTS auditoria (
    id BIGSERIAL PRIMARY KEY,
    fecha TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    extension VARCHAR(32),
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
    accion VARCHAR(120) NOT NULL,
    detalle TEXT
);

CREATE INDEX IF NOT EXISTS idx_auditoria_extension ON auditoria(extension);
CREATE INDEX IF NOT EXISTS idx_auditoria_fecha ON auditoria(fecha);

-- ============================================
-- BOLETAS (ACTUALIZADA CON NUEVAS COLUMNAS)
-- ============================================
CREATE TABLE IF NOT EXISTS boletas (
    id SERIAL PRIMARY KEY,
    numero_boleta VARCHAR(64) NOT NULL UNIQUE,
    extension VARCHAR(32),
    nombre_usuario VARCHAR(200),
    creado_por VARCHAR(100),
    paginas INTEGER DEFAULT 0,
    estado VARCHAR(30) DEFAULT 'Pendiente',
    servicios JSONB DEFAULT '{}'::jsonb,
    copias_color INTEGER DEFAULT 0,
    copias_bn INTEGER DEFAULT 0,
    total_copias INTEGER DEFAULT 0,
    cantidad_documentos INTEGER DEFAULT 0,
    empaste JSONB DEFAULT '{}'::jsonb,
    observaciones TEXT,
    firma_paths JSONB DEFAULT '{}'::jsonb,
    fecha_solicitud TIMESTAMP WITH TIME ZONE DEFAULT now(),
    fecha_procesado TIMESTAMP WITH TIME ZONE,
    dia VARCHAR(20),
    operador_responsable VARCHAR(80),
    cerrado BOOLEAN DEFAULT FALSE,
    listo_para_cierre BOOLEAN DEFAULT FALSE,
    enviado_cierre_por VARCHAR(80),
    fecha_envio_cierre TIMESTAMP WITH TIME ZONE,
    revisado_por_encargado VARCHAR(80),
    fecha_revision_encargado TIMESTAMP WITH TIME ZONE,
    archivado_calendario BOOLEAN DEFAULT FALSE,
    fecha_archivo DATE,
    modificaciones JSONB DEFAULT '[]'::jsonb,
    meta JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_boletas_extension ON boletas(extension);
CREATE INDEX IF NOT EXISTS idx_boletas_estado ON boletas(estado);
CREATE INDEX IF NOT EXISTS idx_boletas_dia ON boletas(dia);
CREATE INDEX IF NOT EXISTS idx_boletas_cerrado ON boletas(cerrado);
CREATE INDEX IF NOT EXISTS idx_boletas_listo_cierre ON boletas(listo_para_cierre);
CREATE INDEX IF NOT EXISTS idx_boletas_fecha_solicitud ON boletas(fecha_solicitud);
CREATE INDEX IF NOT EXISTS idx_boletas_fecha_archivo ON boletas(fecha_archivo);

-- ============================================
-- NOTIFICACIONES (ACTUALIZADA)
-- ============================================
CREATE TABLE IF NOT EXISTS notificaciones (
    id BIGSERIAL PRIMARY KEY,
    extension VARCHAR(32) NOT NULL,
    tipo VARCHAR(80) NOT NULL,
    numero_boleta VARCHAR(64),
    mensaje TEXT NOT NULL,
    leido BOOLEAN DEFAULT FALSE,
    reproducido BOOLEAN DEFAULT FALSE,
    creado_ts TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_notif_extension ON notificaciones(extension);
CREATE INDEX IF NOT EXISTS idx_notif_leido ON notificaciones(leido);
CREATE INDEX IF NOT EXISTS idx_notif_tipo ON notificaciones(tipo);

-- ============================================
-- CONFIGURACIÓN DE USUARIO
-- ============================================
CREATE TABLE IF NOT EXISTS configuracion_usuario (
    id SERIAL PRIMARY KEY,
    extension VARCHAR(32) NOT NULL UNIQUE,
    notificaciones_activas BOOLEAN DEFAULT TRUE,
    sonido_nueva_boleta BOOLEAN DEFAULT TRUE,
    sonido_rechazo BOOLEAN DEFAULT TRUE,
    control_operador_activo BOOLEAN DEFAULT FALSE,
    ultima_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_config_extension ON configuracion_usuario(extension);

-- ============================================
-- CALENDARIO BOLETAS ARCHIVADAS
-- ============================================
CREATE TABLE IF NOT EXISTS calendario_boletas (
    id SERIAL PRIMARY KEY,
    fecha_archivo DATE NOT NULL,
    numero_boleta VARCHAR(64) NOT NULL,
    extension VARCHAR(32),
    nombre_usuario VARCHAR(200),
    paginas INTEGER,
    estado VARCHAR(30),
    operador_responsable VARCHAR(80),
    revisado_por VARCHAR(80),
    datos_completos JSONB,
    archivado_por VARCHAR(80),
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_calendario_fecha ON calendario_boletas(fecha_archivo);
CREATE INDEX IF NOT EXISTS idx_calendario_numero ON calendario_boletas(numero_boleta);

-- ============================================
-- DATOS INICIALES
-- ============================================
INSERT INTO roles (nombre, descripcion) VALUES
    ('admin', 'Administrador del sistema'),
    ('operador', 'Operador de litografía'),
    ('usuario', 'Usuario solicitante'),
    ('encargado', 'Encargado/Coordinador')
ON CONFLICT (nombre) DO NOTHING;

-- Usuario admin por defecto
INSERT INTO usuarios (usuario, nombre_completo, extension, rol_id, password, activo)
SELECT 'admin', 'Administrador Sistema', '100', r.id, crypt('admin123', gen_salt('bf')), TRUE
FROM roles r WHERE r.nombre='admin'
ON CONFLICT (usuario) DO NOTHING;

INSERT INTO usuarios (usuario, nombre_completo, extension, rol_id, password, activo)
SELECT 'operador', 'Juan Pérez', '101', r.id, crypt('operador123', gen_salt('bf')), TRUE
FROM roles r WHERE r.nombre='operador'
ON CONFLICT (usuario) DO NOTHING;

INSERT INTO usuarios (usuario, nombre_completo, extension, rol_id, password, activo)
SELECT 'usuario', 'María García', '201', r.id, crypt('usuario123', gen_salt('bf')), TRUE
FROM roles r WHERE r.nombre='usuario'
ON CONFLICT (usuario) DO NOTHING;

INSERT INTO usuarios (usuario, nombre_completo, extension, rol_id, password, activo)
SELECT 'encargado', 'Carlos Rodríguez', '301', r.id, crypt('encargado123', gen_salt('bf')), TRUE
FROM roles r WHERE r.nombre='encargado'
ON CONFLICT (usuario) DO NOTHING;

COMMIT;
