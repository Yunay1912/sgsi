-- db/schema_asamblea.sql
-- Esquema para la app Asamblea (PostgreSQL)

-- Roles
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT now()
);

-- Un rol de prueba (según tu petición)
INSERT INTO roles (name, description)
VALUES ('prueba', 'Rol de prueba creado por estructura inicial')
ON CONFLICT (name) DO NOTHING;

-- Usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255), -- usar bcrypt/argon2 en producción
    nombre_completo VARCHAR(200),
    extension VARCHAR(20),
    rol_id INTEGER REFERENCES roles(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT now(),
    activo BOOLEAN DEFAULT TRUE
);
CREATE INDEX IF NOT EXISTS idx_usuarios_extension ON usuarios(extension);

-- Auditoría
CREATE TABLE IF NOT EXISTS auditoria (
    id SERIAL PRIMARY KEY,
    fecha TIMESTAMP NOT NULL DEFAULT now(),
    extension VARCHAR(20),
    accion VARCHAR(150),
    detalle TEXT
);
CREATE INDEX IF NOT EXISTS idx_auditoria_extension ON auditoria(extension);

-- Boletas (solicitudes)
CREATE TABLE IF NOT EXISTS boletas (
    id SERIAL PRIMARY KEY,
    numero_boleta VARCHAR(80) NOT NULL UNIQUE,
    extension VARCHAR(20),
    nombre VARCHAR(200),
    paginas INTEGER DEFAULT 0,
    estado VARCHAR(32) DEFAULT 'Pendiente', -- Pendiente, En proceso, Listo, Rechazado
    dia VARCHAR(16), -- Lunes, Martes, ...
    fecha_creacion TIMESTAMP DEFAULT now(),
    fecha_actualizacion TIMESTAMP DEFAULT now(),
    observaciones TEXT,
    datos JSONB, -- para empaste, copias, etc. (estructura flexible)
    firma_operador_path TEXT,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_boletas_extension ON boletas(extension);
CREATE INDEX IF NOT EXISTS idx_boletas_dia ON boletas(dia);
CREATE INDEX IF NOT EXISTS idx_boletas_estado ON boletas(estado);

-- Boletas archivadas (Calendario / Cierre)
CREATE TABLE IF NOT EXISTS boletas_archivadas (
    id SERIAL PRIMARY KEY,
    boleta_id INTEGER REFERENCES boletas(id) ON DELETE CASCADE,
    numero_boleta VARCHAR(80),
    extension VARCHAR(20),
    nombre VARCHAR(200),
    paginas INTEGER,
    fecha_archivo DATE NOT NULL DEFAULT current_date,
    metadata JSONB,
    archivado_por VARCHAR(100),
    created_at TIMESTAMP DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_boletas_archivadas_fecha ON boletas_archivadas(fecha_archivo);

-- Firmas (opcional, referencial)
CREATE TABLE IF NOT EXISTS firmas (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    path TEXT,
    tipo VARCHAR(50), -- operador, vb, small, etc.
    uploaded_at TIMESTAMP DEFAULT now()
);

-- Tabla de notificaciones ligera (si la usás después)
CREATE TABLE IF NOT EXISTS notificaciones (
    id SERIAL PRIMARY KEY,
    extension VARCHAR(20),
    tipo VARCHAR(80),
    mensaje TEXT,
    leido BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT now()
);

-- Si necesitás datos iniciales de prueba, puedes agregarlos manualmente desde SQL o Python.
