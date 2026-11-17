-- Ejecutar una vez en pgAdmin sobre nutria_mvp.
-- La RTC-2017 entrega peso; no inventamos composición corporal ni calorías.
-- Los campos medidos no disponibles quedan opcionales; las estimaciones de
-- grasa y agua se guardan por separado en sus campos correspondientes. Los
-- datos históricos existentes se conservan sin cambios.

ALTER TABLE mediciones
    ALTER COLUMN grasa_pct DROP NOT NULL,
    ALTER COLUMN masa_muscular_pct DROP NOT NULL,
    ALTER COLUMN agua_pct DROP NOT NULL,
    ALTER COLUMN calorias_kcal DROP NOT NULL;

ALTER TABLE mediciones
    ADD COLUMN IF NOT EXISTS agua_litros NUMERIC(6, 2) CHECK (agua_litros > 0);
