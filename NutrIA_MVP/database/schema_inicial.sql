-- Esquema inicial para la persistencia del flujo actual de NutrIA MVP.
-- Ejecutar una sola vez en la base de datos nutria_mvp desde pgAdmin.

CREATE TABLE IF NOT EXISTS pacientes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE,
    sexo VARCHAR(20) NOT NULL DEFAULT 'Masculino'
        CHECK (sexo IN ('Masculino', 'Femenino', 'Otro')),
    telefono VARCHAR(30) NOT NULL DEFAULT '',
    correo VARCHAR(254) NOT NULL DEFAULT '',
    observaciones TEXT NOT NULL DEFAULT '',
    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS citas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_citas_fecha_hora ON citas (fecha, hora);
CREATE INDEX IF NOT EXISTS idx_citas_paciente_fecha ON citas (paciente_id, fecha);

CREATE TABLE IF NOT EXISTS mediciones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    fecha DATE NOT NULL,
    objetivo VARCHAR(80) NOT NULL DEFAULT '',
    actividad VARCHAR(80) NOT NULL DEFAULT '',
    motivo TEXT NOT NULL DEFAULT '',
    peso_kg NUMERIC(7, 2) NOT NULL CHECK (peso_kg > 0),
    altura_cm NUMERIC(6, 2) NOT NULL CHECK (altura_cm BETWEEN 50 AND 250),
    grasa_pct NUMERIC(5, 2) NOT NULL CHECK (grasa_pct > 0),
    masa_muscular_pct NUMERIC(5, 2) NOT NULL CHECK (masa_muscular_pct > 0),
    agua_pct NUMERIC(5, 2) NOT NULL CHECK (agua_pct > 0),
    calorias_kcal NUMERIC(8, 2) NOT NULL CHECK (calorias_kcal > 0),
    imc NUMERIC(5, 1) NOT NULL CHECK (imc > 0),
    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_mediciones_paciente_fecha
    ON mediciones (paciente_id, fecha DESC, creado_en DESC);

CREATE TABLE IF NOT EXISTS objetivos_nutricionales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    calorias_kcal INTEGER NOT NULL CHECK (calorias_kcal > 0),
    macronutrientes JSONB NOT NULL DEFAULT '{}'::jsonb,
    preferencia VARCHAR(80) NOT NULL DEFAULT '',
    alergias TEXT NOT NULL DEFAULT '',
    alimentos_evitar TEXT NOT NULL DEFAULT '',
    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_objetivos_paciente_fecha
    ON objetivos_nutricionales (paciente_id, creado_en DESC);

CREATE TABLE IF NOT EXISTS menus (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    nombre VARCHAR(120) NOT NULL DEFAULT 'Menú personalizado',
    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_menus_paciente_fecha
    ON menus (paciente_id, actualizado_en DESC);

CREATE TABLE IF NOT EXISTS menu_comidas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    menu_id UUID NOT NULL REFERENCES menus(id) ON DELETE CASCADE,
    nombre VARCHAR(80) NOT NULL,
    orden SMALLINT NOT NULL DEFAULT 0,
    UNIQUE (menu_id, nombre)
);

CREATE TABLE IF NOT EXISTS menu_alimentos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    comida_id UUID NOT NULL REFERENCES menu_comidas(id) ON DELETE CASCADE,
    nombre VARCHAR(200) NOT NULL,
    porcion VARCHAR(100) NOT NULL,
    orden SMALLINT NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_menu_comidas_menu_orden
    ON menu_comidas (menu_id, orden);
CREATE INDEX IF NOT EXISTS idx_menu_alimentos_comida_orden
    ON menu_alimentos (comida_id, orden);
