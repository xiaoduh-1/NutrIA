-- Cuentas y perfil del único nutriólogo administrador del MVP.
-- Ejecutar en pgAdmin sobre nutria_mvp antes de registrar una cuenta.

CREATE TABLE IF NOT EXISTS usuarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario VARCHAR(80) NOT NULL,
    correo VARCHAR(254) NOT NULL,
    password_hash TEXT NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_usuarios_usuario_ci
    ON usuarios (lower(usuario));
CREATE UNIQUE INDEX IF NOT EXISTS uq_usuarios_correo_ci
    ON usuarios (lower(correo));

CREATE TABLE IF NOT EXISTS perfiles_nutriologo (
    usuario_id UUID PRIMARY KEY REFERENCES usuarios(id) ON DELETE CASCADE,
    nombre_completo VARCHAR(180) NOT NULL,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS consultorio (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID NOT NULL UNIQUE REFERENCES usuarios(id) ON DELETE CASCADE,
    nombre VARCHAR(180) NOT NULL,
    telefono_contacto VARCHAR(30) NOT NULL,
    correo_contacto VARCHAR(254) NOT NULL,
    foto_path TEXT NOT NULL DEFAULT '',
    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE consultorio
    ADD COLUMN IF NOT EXISTS foto_bytes BYTEA NOT NULL DEFAULT ''::bytea;

COMMENT ON COLUMN usuarios.password_hash IS
    'Hash PBKDF2-HMAC-SHA256 con sal aleatoria; nunca almacenar contraseñas en texto simple.';
