-- init_db.sql
-- Esquema inicial para asamblea_db
-- Ejecutar como superuser o un usuario con permisos de creación de tablas

BEGIN;

-- ====== Extension (si se quiere usar jsonb helpers) ======
-- no necesario en PG estándar, pero dejamos espacio

-- ====== ROLES ======
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT,
    creado_ts TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- ====== USUARIOS ======
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(80) NOT NULL UNIQUE,
    nombre_completo VARCHAR(200) NOT NULL,
    extension VARCHAR(32),
    rol_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE RESTRICT,
    password TEXT NOT NULL, -- En desarrollo: password en claro o hashed. En producción: bcrypt/argon2.
    activo BOOLEAN DEFAULT TRUE,
    creado_ts TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_usuarios_extension ON usuarios(extension);

-- ====== AUDITORÍA ======
CREATE TABLE IF NOT EXISTS auditoria (
    id SERIAL PRIMARY KEY,
    fecha TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    extension VARCHAR(32),
    accion VARCHAR(120) NOT NULL,
    detalle TEXT
);

CREATE INDEX IF NOT EXISTS idx_auditoria_extension ON auditoria(extension);
CREATE INDEX IF NOT EXISTS idx_auditoria_fecha ON auditoria(fecha);

-- ====== BOLETAS (solicitudes y su estado) ======
CREATE TABLE IF NOT EXISTS boletas (
    id SERIAL PRIMARY KEY,
    numero_boleta VARCHAR(64) NOT NULL UNIQUE, -- e.g. B-1234
    extension VARCHAR(32),                       -- quien solicitó
    nombre_usuario VARCHAR(200),                 -- nombre del solicitante
    paginas INTEGER DEFAULT 0,
    estado VARCHAR(30) DEFAULT 'Pendiente',     -- Pendiente / En proceso / Listo / Rechazado
    servicios JSONB,                             -- json con servicios marcados y opciones (empaste, escaneo, etc.)
    copias_color INTEGER DEFAULT 0,
    copias_bn INTEGER DEFAULT 0,
    total_copias INTEGER DEFAULT 0,
    cantidad_documentos INTEGER DEFAULT 0,
    empaste JSONB,                               -- json con conteos por tipo de empaste
    observaciones TEXT,
    firma_paths JSONB,                            -- rutas a imágenes/pdf de firmas si aplica
    fecha_solicitud TIMESTAMP WITH TIME ZONE DEFAULT now(),
    fecha_procesado TIMESTAMP WITH TIME ZONE,
    dia VARCHAR(20),                              -- Lunes..Viernes (opcional, para agrupación rápida)
    operador_responsable VARCHAR(80),             -- extensión o usuario que lo atendió
    cerrado BOOLEAN DEFAULT FALSE,
    meta JSONB                                    -- campo libre para metadatos
);

CREATE INDEX IF NOT EXISTS idx_boletas_extension ON boletas(extension);
CREATE INDEX IF NOT EXISTS idx_boletas_estado ON boletas(estado);
CREATE INDEX IF NOT EXISTS idx_boletas_dia ON boletas(dia);

-- ====== DETALLES (tabla opcional, si quieres filas por contador/operador) ======
CREATE TABLE IF NOT EXISTS boleta_detalle (
    id SERIAL PRIMARY KEY,
    boleta_id INTEGER NOT NULL REFERENCES boletas(id) ON DELETE CASCADE,
    contador_inicial BIGINT DEFAULT 0,
    contador_final BIGINT DEFAULT 0,
    copias_danadas INTEGER DEFAULT 0,
    copias_prueba INTEGER DEFAULT 0,
    personas_atendidas INTEGER DEFAULT 0,
    firma_path TEXT
);

-- ====== BOLETA_CIERRE (registro histórico de cierres diarios) ======
CREATE TABLE IF NOT EXISTS boleta_cierre (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    operador_nombre VARCHAR(200),
    operador_extension VARCHAR(32),
    resumen JSONB,            -- resumen: cantidad boletas, usuarios_unicos, totales, etc.
    texto_boleta TEXT,        -- texto generado para mostrar en UI cierre
    creado_ts TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_boleta_cierre_fecha ON boleta_cierre(fecha);

-- ====== CALENDAR ARCHIVE (boletas archivadas por fecha; alternativa a boleta_cierre) ======
CREATE TABLE IF NOT EXISTS calendar_archive (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    boleta_id INTEGER REFERENCES boletas(id) ON DELETE SET NULL,
    datos JSONB,
    creado_ts TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_calendar_archive_fecha ON calendar_archive(fecha);

-- ====== NOTIFICATIONS ======
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    extension VARCHAR(32),
    tipo VARCHAR(80), -- e.g. cambio_estado, rechazo, info
    mensaje TEXT,
    link TEXT,
    leido BOOLEAN DEFAULT FALSE,
    creado_ts TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_notifications_extension ON notifications(extension);

-- ====== SESSIONS (opcional) ======
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    token VARCHAR(255),
    creado_ts TIMESTAMP WITH TIME ZONE DEFAULT now(),
    expiracion TIMESTAMP WITH TIME ZONE
);

-- ====== Datos de prueba: roles y usuarios mínimos ======
INSERT INTO roles (nombre, descripcion)
    VALUES
    ('admin', 'Administrador del sistema con acceso total'),
    ('operador', 'Operador de litografía (procesa boletas)'),
    ('usuario', 'Usuario solicitante'),
    ('encargado', 'Encargado / Supervisor')
ON CONFLICT (nombre) DO NOTHING;

-- Usuarios de prueba (contraseñas en claro para desarrollo)
-- Cambia a tu conveniencia (en prod usa hash)
INSERT INTO usuarios (usuario, nombre_completo, extension, rol_id, password)
VALUES
('admin1','Administrador Uno','1001', (SELECT id FROM roles WHERE nombre='admin'), 'admin123'),
('admin2','Administrador Dos','1002', (SELECT id FROM roles WHERE nombre='admin'), 'admin123'),
('operador','Juan Perez Operador','101', (SELECT id FROM roles WHERE nombre='operador'), 'operador123'),
('usuario','Maria Garcia Usuario','201', (SELECT id FROM roles WHERE nombre='usuario'), 'usuario123'),
('encargado','Carlos Rodriguez Encargado','301', (SELECT id FROM roles WHERE nombre='encargado'), 'encargado123')
ON CONFLICT (usuario) DO NOTHING;

-- Ejemplos iniciales de auditoría
INSERT INTO auditoria (fecha, extension, accion, detalle)
VALUES
(now() - interval '1 day', '1001', 'login', 'Admin demo inicio de sesión'),
(now() - interval '2 day', '101', 'crear_boleta', 'Boleta demo creada por operador')
;

-- Ejemplo de boletas demo (opcional)
INSERT INTO boletas (numero_boleta, extension, nombre_usuario, paginas, estado, servicios, copias_color, copias_bn, total_copias, dia)
VALUES
('B-1001','201','Maria Garcia Usuario', 3, 'Pendiente', '{"fotocopiado": true}'::jsonb, 0, 3, 3, 'Lunes'),
('B-1002','202','Usuario Demo', 2, 'Pendiente', '{"impresion_email": true}'::jsonb, 2, 0, 2, 'Martes')
ON CONFLICT (numero_boleta) DO NOTHING;

COMMIT;
