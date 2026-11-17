# NutrIA MVP

Esta es una copia de trabajo separada del proyecto original. Arranque la aplicación desde esta carpeta con `python main.py` en el entorno que ya tenga las dependencias de la interfaz.

## Persistencia actual

La interfaz usa `datos.repositorio_transicional.py`: pacientes, citas, mediciones, objetivos nutricionales y menús se guardan en PostgreSQL. El repositorio en memoria permanece como implementación temporal de respaldo, pero ya no gestiona esos módulos.

El flujo conectado para el MVP es:

1. Buscar, registrar, editar y eliminar pacientes.
2. Crear, consultar, editar y eliminar citas; el calendario marca los días que tienen citas.
3. Capturar la estatura antes de la medición, obtener el peso desde una báscula RTC-2017 por BLE, calcular el IMC y guardar el resultado ligado al paciente.
4. Guardar objetivos, agregar alimentos del catálogo o texto libre a las comidas y mostrar una vista previa del reporte.

No se precargan pacientes, citas ni mediciones. La migración del catálogo añade ocho alimentos ilustrativos marcados como datos de demostración; hay que reemplazarlos por información nutricional verificada antes de usarlos en planes clínicos. El generador de menús y la exportación PDF todavía no están implementados. La estatura se captura en centímetros antes de iniciar la medición. La báscula RTC-2017 aporta el peso por anuncios BLE; el IMC se calcula con el método existente. La grasa corporal se estima con Deurenberg y el agua total con Watson; son estimaciones antropométricas, no lecturas directas de BIA. Watson devuelve litros, y el porcentaje mostrado se calcula respecto al peso. La báscula se filtra por la MAC conocida, el producto observado y una lectura estable. El campo BIA `1770` no se utiliza. Al seleccionar un paciente, su nombre se actualiza en los encabezados de las pantallas del flujo.

Al abrir Objetivos nutricionales se sugiere una meta calórica con Mifflin–St Jeor y el factor de actividad elegido. Se resta 500 kcal para pérdida de peso, se suman 500 kcal para ganancia muscular y se usa mantenimiento para mantenimiento u otro objetivo. El usuario puede editar la sugerencia. Se necesita fecha de nacimiento válida y sexo Masculino o Femenino; si falta alguno de esos datos, la pantalla explica por qué no se pudo sugerir y permite capturar el objetivo manualmente.

La interfaz fusionada añade Inicio, Configuración, Reporte de paciente, Registro y Recuperación de contraseña. Inicio obtiene citas y conteos del repositorio, y Reporte de paciente muestra el historial del paciente seleccionado. La cuenta, el perfil del nutriólogo y los datos del consultorio se guardan en PostgreSQL; la contraseña se guarda como hash PBKDF2-HMAC-SHA256, nunca en texto simple. La foto comprimida se guarda en BYTEA y también se conserva su ruta local. La recuperación envía un código de seis dígitos por Gmail SMTP; el código se almacena como hash, vence en 10 minutos y permite hasta cinco intentos.

## Sustituir memoria por PostgreSQL

Las pantallas deben seguir dependiendo de las operaciones del repositorio y no conectarse directamente a PostgreSQL. La capa transicional conserva las operaciones que utiliza la interfaz y traduce sus datos a las tablas relacionales de PostgreSQL.

## Preparar y verificar la conexión local

La conexión está en `datos/conexion.py` y la configuración se carga desde `.env`.

1. Instala el controlador y el lector de `.env` desde esta carpeta: `python -m pip install -r requirements-postgres.txt`.
2. Copia `.env.example` como `.env` y completa `NUTRIA_DB_PASSWORD` con la contraseña del usuario PostgreSQL que usarás. No compartas ni subas ese archivo.
3. Ejecuta `python -m scripts.verificar_conexion`.
4. Si aparece “Conexión correcta”, la configuración está lista para usar PostgreSQL.

El CRUD de pacientes, citas, mediciones, objetivos y menús utiliza PostgreSQL mediante `datos/repositorio_transicional.py`. Para esta integración, ejecuta `database/mediciones_peso_ble.sql` en Query Tool sobre `nutria_mvp` (se puede volver a ejecutar para agregar la columna de agua en litros). Permite que las métricas que no se midieron queden sin dato y guarda las estimaciones Deurenberg/Watson en las columnas correspondientes. Bleak se instala junto con las demás dependencias mediante el comando del paso 1.

Las cuentas de nutriólogo requieren ejecutar una vez `database/cuentas_nutriologo.sql` en Query Tool sobre `nutria_mvp`. El login, edición de configuración y cambio de contraseña utilizan las tablas `usuarios`, `perfiles_nutriologo` y `consultorio`.

La recuperación de contraseña también requiere ejecutar `database/recuperacion_password.sql` en Query Tool. Agrega al `.env` local `NUTRIA_SMTP_EMAIL` y `NUTRIA_SMTP_APP_PASSWORD` con el correo Gmail remitente y su contraseña de aplicación (no la contraseña normal de Gmail). No compartas ni subas `.env`; usa `.env.example` como plantilla. La aplicación conecta a `smtp.gmail.com:587` mediante STARTTLS. Si el correo ingresado no corresponde a una cuenta, la interfaz muestra la misma confirmación genérica y no envía correo.

Para probar SMTP sin pasar por la recuperación, define también `NUTRIA_SMTP_TEST_TO` en `.env` y ejecuta desde `NutrIA_MVP`: `python -m scripts.correo`. El script informa errores de configuración, conexión o autenticación sin imprimir las credenciales.

## Catálogo de alimentos

En pgAdmin, abre Query Tool para `nutria_mvp` y ejecuta `database/catalogo_alimentos.sql` después del esquema inicial. La migración crea `alimentos`, agrega la referencia y la cantidad a `menu_alimentos`, y carga registros ilustrativos. En la personalización de una comida, usa **Buscar en catálogo** para buscar un alimento y añadir su cantidad en gramos o mililitros. Las filas antiguas de texto libre se conservan.
