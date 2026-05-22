-- db/asamblea_db.sql
-- Esquema real para Asamblea_App (Postgres)
BEGIN;

-- Extensions necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ROLES
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- USUARIOS
CREATE TABLE IF NOT EXISTS usuarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(100) NOT NULL UNIQUE,
    extension VARCHAR(20),
    password_hash TEXT, -- almacenar con crypt()
    rol_id INTEGER REFERENCES roles(id) ON DELETE SET NULL,
    nombre_completo TEXT,
    email VARCHAR(200),
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_usuarios_extension ON usuarios(extension);

-- BOLETAS (solicitudes)
CREATE TABLE IF NOT EXISTS boletas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    numero_boleta VARCHAR(60) NOT NULL UNIQUE,
    creado_por_uuid UUID REFERENCES usuarios(id) ON DELETE SET NULL,
    extension_creador VARCHAR(20),
    nombre_creador TEXT,
    area_origen TEXT,
    fecha TIMESTAMP WITH TIME ZONE DEFAULT now(),
    fecha_solicitada DATE,
    dia VARCHAR(16), -- Lunes..Viernes
    estado VARCHAR(30) DEFAULT 'Pendiente', -- Pendiente, En proceso, Listo, Rechazado
    paginas INTEGER DEFAULT 0,
    copias_color INTEGER DEFAULT 0,
    copias_bn INTEGER DEFAULT 0,
    total_copias INTEGER DEFAULT 0,
    cantidad_documentos INTEGER DEFAULT 0,
    servicios JSONB, -- {"fotocopiado":true, "impresion_llave":false, ...}
    empaste JSONB,   -- {"grapa":0,"resorte":0,"cuadernillo":0,...}
    observaciones TEXT,
    firmas JSONB, -- rutas o metadatos de firmas {"small":"/path","operador":"/path", "vb_ej":null,...}
    datos_extra JSONB, -- flexible para futuras ampliaciones
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_boletas_extension ON boletas(extension_creador);
CREATE INDEX IF NOT EXISTS idx_boletas_estado ON boletas(estado);
CREATE INDEX IF NOT EXISTS idx_boletas_fecha ON boletas(fecha);

-- Auditoría
CREATE TABLE IF NOT EXISTS auditoria (
    id BIGSERIAL PRIMARY KEY,
    fecha TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    extension VARCHAR(50),
    usuario_uuid UUID REFERENCES usuarios(id) ON DELETE SET NULL,
    accion VARCHAR(120),
    detalle TEXT
);
CREATE INDEX IF NOT EXISTS idx_auditoria_extension ON auditoria(extension);
CREATE INDEX IF NOT EXISTS idx_auditoria_fecha ON auditoria(fecha);

-- CIERRES DIARIOS
CREATE TABLE IF NOT EXISTS cierres (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fecha DATE NOT NULL,
    operador_uuid UUID REFERENCES usuarios(id) ON DELETE SET NULL,
    operador_nombre TEXT,
    resumen TEXT,
    totales JSONB,      -- {"trabajos":10,"copias_color":100,"copias_bn":200}
    detalle_operadores JSONB, -- array con objetos para cada operador (contadores, daños, personas atendidas)
    firmas JSONB,       -- firmas internas si aplica
    metadatos JSONB,
    creado_por UUID REFERENCES usuarios(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_cierres_fecha ON cierres(fecha);

-- NOTIFICACIONES (registro + cola)
CREATE TABLE IF NOT EXISTS notificaciones (
    id BIGSERIAL PRIMARY KEY,
    usuario_uuid UUID REFERENCES usuarios(id) ON DELETE SET NULL,
    extension_destino VARCHAR(50),
    tipo VARCHAR(60),
    payload JSONB,
    estado VARCHAR(30) DEFAULT 'pendiente', -- pendiente, enviado, fallido
    intento_count INTEGER DEFAULT 0,
    last_error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    sent_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX IF NOT EXISTS idx_notif_estado ON notificaciones(estado);

-- ADJUNTOS (firmas / pdfs asociados)
CREATE TABLE IF NOT EXISTS archivos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    boleta_id UUID REFERENCES boletas(id) ON DELETE CASCADE,
    nombre_original TEXT,
    ruta TEXT, -- ruta en disco/URL si se guarda fuera de DB
    tipo_mime VARCHAR(100),
    metadatos JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Trigger: actualizar updated_at en boletas
CREATE OR REPLACE FUNCTION fn_boletas_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_boletas_updated_at ON boletas;
CREATE TRIGGER trg_boletas_updated_at
BEFORE UPDATE ON boletas
FOR EACH ROW EXECUTE FUNCTION fn_boletas_set_updated_at();

COMMIT;

-- SEMILLAS: roles y usuario de prueba (TI puede cambiar contraseña)
BEGIN;
INSERT INTO roles (name, description) VALUES ('admin', 'Administrador completo') ON CONFLICT DO NOTHING;
INSERT INTO roles (name, description) VALUES ('operador', 'Operador del servicio') ON CONFLICT DO NOTHING;
INSERT INTO roles (name, description) VALUES ('usuario', 'Usuario solicitante') ON CONFLICT DO NOTHING;
INSERT INTO roles (name, description) VALUES ('encargado', 'Encargado/Coordinador') ON CONFLICT DO NOTHING;

INSERT INTO usuarios (username, extension, password_hash, rol_id, nombre_completo, email)
SELECT 'admin', '100', crypt('admin123', gen_salt('bf')), r.id, 'Administrador Sistema', 'admin@example.local'
FROM roles r WHERE r.name='admin'
ON CONFLICT (username) DO NOTHING;

COMMIT;
