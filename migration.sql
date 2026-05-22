-- migration.sql
-- Migración para actualizar BD existente a nueva versión
-- ============================================

BEGIN;

-- ============================================
-- 1. Actualizar tabla boletas con nuevas columnas
-- ============================================
ALTER TABLE boletas ADD COLUMN IF NOT EXISTS listo_para_cierre BOOLEAN DEFAULT FALSE;
ALTER TABLE boletas ADD COLUMN IF NOT EXISTS enviado_cierre_por VARCHAR(80);
ALTER TABLE boletas ADD COLUMN IF NOT EXISTS fecha_envio_cierre TIMESTAMP WITH TIME ZONE;
ALTER TABLE boletas ADD COLUMN IF NOT EXISTS revisado_por_encargado VARCHAR(80);
ALTER TABLE boletas ADD COLUMN IF NOT EXISTS fecha_revision_encargado TIMESTAMP WITH TIME ZONE;
ALTER TABLE boletas ADD COLUMN IF NOT EXISTS archivado_calendario BOOLEAN DEFAULT FALSE;
ALTER TABLE boletas ADD COLUMN IF NOT EXISTS fecha_archivo DATE;
ALTER TABLE boletas ADD COLUMN IF NOT EXISTS modificaciones JSONB DEFAULT '[]'::jsonb;

-- Agregar índices para las nuevas columnas
CREATE INDEX IF NOT EXISTS idx_boletas_listo_cierre ON boletas(listo_para_cierre);
CREATE INDEX IF NOT EXISTS idx_boletas_fecha_archivo ON boletas(fecha_archivo);

-- ============================================
-- 2. Crear tabla configuracion_usuario
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
-- 3. Crear tabla calendario_boletas
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
-- 4. Actualizar tabla notificaciones
-- ============================================
ALTER TABLE notificaciones ADD COLUMN IF NOT EXISTS reproducido BOOLEAN DEFAULT FALSE;
ALTER TABLE notificaciones ADD COLUMN IF NOT EXISTS numero_boleta VARCHAR(64);

CREATE INDEX IF NOT EXISTS idx_notif_reproducido ON notificaciones(reproducido);
CREATE INDEX IF NOT EXISTS idx_notif_tipo ON notificaciones(tipo);

-- ============================================
-- 5. Crear configuración inicial para usuarios existentes
-- ============================================
INSERT INTO configuracion_usuario (extension, notificaciones_activas, sonido_nueva_boleta, sonido_rechazo)
SELECT DISTINCT extension, TRUE, TRUE, TRUE 
FROM usuarios 
WHERE extension IS NOT NULL
ON CONFLICT (extension) DO NOTHING;

COMMIT;

-- ============================================
-- Verificar cambios
-- ============================================
SELECT 'Migración completada exitosamente' as status;

-- Ver nuevas columnas en boletas
\d boletas

-- Ver nuevas tablas
\dt configuracion_usuario
\dt calendario_boletas
