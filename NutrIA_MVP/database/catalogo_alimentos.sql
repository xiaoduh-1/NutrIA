-- Migración del catálogo de alimentos y su vínculo con los alimentos del menú.
-- Ejecutar en pgAdmin sobre nutria_mvp después de schema_inicial.sql.

CREATE TABLE IF NOT EXISTS alimentos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(180) NOT NULL,
    categoria VARCHAR(80) NOT NULL,
    unidad_base VARCHAR(2) NOT NULL DEFAULT 'g'
        CHECK (unidad_base IN ('g', 'ml')),
    calorias_100 NUMERIC(8, 2) NOT NULL DEFAULT 0 CHECK (calorias_100 >= 0),
    proteinas_100 NUMERIC(8, 2) NOT NULL DEFAULT 0 CHECK (proteinas_100 >= 0),
    carbohidratos_100 NUMERIC(8, 2) NOT NULL DEFAULT 0 CHECK (carbohidratos_100 >= 0),
    grasas_100 NUMERIC(8, 2) NOT NULL DEFAULT 0 CHECK (grasas_100 >= 0),
    fibra_100 NUMERIC(8, 2) CHECK (fibra_100 IS NULL OR fibra_100 >= 0),
    fuente VARCHAR(180) NOT NULL DEFAULT 'Sin especificar',
    referencia_fuente TEXT NOT NULL DEFAULT '',
    es_dato_prueba BOOLEAN NOT NULL DEFAULT FALSE,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_alimentos_nombre_categoria
    ON alimentos (lower(nombre), lower(categoria));
CREATE INDEX IF NOT EXISTS idx_alimentos_activo_categoria_nombre
    ON alimentos (activo, categoria, nombre);

-- Los campos de texto existentes se conservan como fotografía del alimento y
-- porción mostrados en el menú. alimento_id queda nullable para mantener filas
-- anteriores que se capturaron como texto libre.
ALTER TABLE menu_alimentos
    ADD COLUMN IF NOT EXISTS alimento_id UUID REFERENCES alimentos(id) ON DELETE RESTRICT,
    ADD COLUMN IF NOT EXISTS cantidad_base NUMERIC(10, 2)
        CHECK (cantidad_base IS NULL OR cantidad_base > 0),
    ADD COLUMN IF NOT EXISTS unidad_base VARCHAR(2)
        CHECK (unidad_base IS NULL OR unidad_base IN ('g', 'ml')),
    ADD COLUMN IF NOT EXISTS calorias_kcal NUMERIC(10, 2),
    ADD COLUMN IF NOT EXISTS proteinas_g NUMERIC(10, 2),
    ADD COLUMN IF NOT EXISTS carbohidratos_g NUMERIC(10, 2),
    ADD COLUMN IF NOT EXISTS grasas_g NUMERIC(10, 2);

CREATE INDEX IF NOT EXISTS idx_menu_alimentos_alimento
    ON menu_alimentos (alimento_id);

-- Registros ilustrativos únicamente para probar búsqueda, selección y porciones.
-- Reemplaza estos valores por datos verificados antes de usarlos en planes clínicos.
INSERT INTO alimentos (
    nombre, categoria, unidad_base, calorias_100, proteinas_100,
    carbohidratos_100, grasas_100, fibra_100, fuente, referencia_fuente, es_dato_prueba
) VALUES
    ('Pechuga de pollo cocida', 'Proteínas', 'g', 165, 31.00, 0.00, 3.60, 0.00,
     'NutrIA - datos de demostración', 'Valores ilustrativos para validar el flujo; verificar antes de uso clínico.', TRUE),
    ('Huevo cocido', 'Proteínas', 'g', 155, 12.60, 1.10, 10.60, 0.00,
     'NutrIA - datos de demostración', 'Valores ilustrativos para validar el flujo; verificar antes de uso clínico.', TRUE),
    ('Frijoles negros cocidos', 'Leguminosas', 'g', 132, 8.90, 23.70, 0.50, 8.70,
     'NutrIA - datos de demostración', 'Valores ilustrativos para validar el flujo; verificar antes de uso clínico.', TRUE),
    ('Arroz blanco cocido', 'Cereales', 'g', 130, 2.70, 28.20, 0.30, 0.40,
     'NutrIA - datos de demostración', 'Valores ilustrativos para validar el flujo; verificar antes de uso clínico.', TRUE),
    ('Avena seca', 'Cereales', 'g', 389, 16.90, 66.30, 6.90, 10.60,
     'NutrIA - datos de demostración', 'Valores ilustrativos para validar el flujo; verificar antes de uso clínico.', TRUE),
    ('Plátano', 'Frutas', 'g', 89, 1.10, 22.80, 0.30, 2.60,
     'NutrIA - datos de demostración', 'Valores ilustrativos para validar el flujo; verificar antes de uso clínico.', TRUE),
    ('Aguacate', 'Grasas', 'g', 160, 2.00, 8.50, 14.70, 6.70,
     'NutrIA - datos de demostración', 'Valores ilustrativos para validar el flujo; verificar antes de uso clínico.', TRUE),
    ('Brócoli cocido', 'Verduras', 'g', 35, 2.40, 7.20, 0.40, 3.30,
     'NutrIA - datos de demostración', 'Valores ilustrativos para validar el flujo; verificar antes de uso clínico.', TRUE)
ON CONFLICT DO NOTHING;
