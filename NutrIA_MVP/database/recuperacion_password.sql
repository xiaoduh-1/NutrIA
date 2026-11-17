-- Ejecutar una sola vez en pgAdmin sobre nutria_mvp.
-- Los códigos se guardan como hash, tienen vencimiento y se invalidan al usarse.

CREATE TABLE IF NOT EXISTS recuperaciones_password (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    correo VARCHAR(254) NOT NULL,
    codigo_hash TEXT NOT NULL,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    vence_en TIMESTAMPTZ NOT NULL,
    intentos SMALLINT NOT NULL DEFAULT 0 CHECK (intentos >= 0 AND intentos <= 5),
    usado BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS ix_recuperaciones_password_correo_fecha
    ON recuperaciones_password (lower(correo), creado_en DESC);
