# NutrIA MVP

Esta es una copia de trabajo separada del proyecto original. Arranque la aplicación desde esta carpeta con `python main.py` en el entorno que ya tenga las dependencias de la interfaz.

## Persistencia actual

La interfaz usa `datos.repositorio_transicional.py`: pacientes, citas, mediciones, objetivos nutricionales y menús se guardan en PostgreSQL. El repositorio en memoria permanece como implementación temporal de respaldo, pero ya no gestiona esos módulos.

El flujo conectado para el MVP es:

1. Buscar, registrar, editar y eliminar pacientes.
2. Crear citas para pacientes registrados y consultar las citas del día.
3. Capturar mediciones (incluidas estatura y calorías provisionales), guardarlas ligadas al paciente y ver su historial y resultados.
4. Guardar objetivos, agregar alimentos del catálogo o texto libre a las comidas y mostrar una vista previa del reporte.

No se precargan pacientes, citas ni mediciones. La migración del catálogo añade ocho alimentos ilustrativos marcados como datos de demostración; hay que reemplazarlos por información nutricional verificada antes de usarlos en planes clínicos. El generador de menús y la exportación PDF todavía no están implementados. La estatura para el cálculo provisional del IMC se captura manualmente en centímetros en la pantalla de medición; posteriormente debe sustituirse por el dato recibido del BIA. Al seleccionar un paciente, su nombre se actualiza en los encabezados de las pantallas del flujo.

Al abrir Objetivos nutricionales se sugiere una meta calórica con Mifflin–St Jeor y el factor de actividad elegido. Se resta 500 kcal para pérdida de peso, se suman 500 kcal para ganancia muscular y se usa mantenimiento para mantenimiento u otro objetivo. El usuario puede editar la sugerencia. Se necesita fecha de nacimiento válida y sexo Masculino o Femenino; si falta alguno de esos datos, la pantalla explica por qué no se pudo sugerir y permite capturar el objetivo manualmente.

La interfaz fusionada añade Inicio, Configuración, Reporte de paciente, Registro y Recuperación de contraseña. Inicio obtiene citas y conteos del repositorio, y Reporte de paciente muestra el historial del paciente seleccionado. Registro y recuperación son por ahora pantallas visuales: no hay autenticación, alta de cuentas ni envío de correo conectado. La configuración de consultorio y usuario también queda pendiente de persistencia.

## Sustituir memoria por PostgreSQL

Las pantallas deben seguir dependiendo de las operaciones del repositorio y no conectarse directamente a PostgreSQL. La capa transicional conserva las operaciones que utiliza la interfaz y traduce sus datos a las tablas relacionales de PostgreSQL.

## Preparar y verificar la conexión local

La conexión está en `datos/conexion.py` y la configuración se carga desde `.env`.

1. Instala el controlador y el lector de `.env` desde esta carpeta: `python -m pip install -r requirements-postgres.txt`.
2. Copia `.env.example` como `.env` y completa `NUTRIA_DB_PASSWORD` con la contraseña del usuario PostgreSQL que usarás. No compartas ni subas ese archivo.
3. Ejecuta `python -m scripts.verificar_conexion`.
4. Si aparece “Conexión correcta”, la configuración está lista para usar PostgreSQL.

El CRUD de pacientes, citas, mediciones, objetivos y menús utiliza PostgreSQL mediante `datos/repositorio_transicional.py`.

## Catálogo de alimentos

En pgAdmin, abre Query Tool para `nutria_mvp` y ejecuta `database/catalogo_alimentos.sql` después del esquema inicial. La migración crea `alimentos`, agrega la referencia y la cantidad a `menu_alimentos`, y carga registros ilustrativos. En la personalización de una comida, usa **Buscar en catálogo** para buscar un alimento y añadir su cantidad en gramos o mililitros. Las filas antiguas de texto libre se conservan.
