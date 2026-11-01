# NutrIA MVP

Esta es una copia de trabajo separada del proyecto original. Arranque la aplicación desde esta carpeta con `python main.py` en el entorno que ya tenga las dependencias de la interfaz.

## Persistencia actual

La interfaz obtiene y guarda datos mediante `datos/repositorio_memoria.py` (módulo `datos.repositorio_memoria`). El repositorio inicia vacío y conserva pacientes, citas, mediciones, objetivos nutricionales y menús en memoria mientras la aplicación está abierta. Al cerrar el proceso, esos datos se pierden.

El flujo conectado para el MVP es:

1. Buscar, registrar, editar y eliminar pacientes.
2. Crear citas para pacientes registrados y consultar las citas del día.
3. Capturar mediciones (incluidas estatura y calorías provisionales), guardarlas ligadas al paciente y ver su historial y resultados.
4. Guardar objetivos, agregar o editar comidas manualmente y mostrar una vista previa del reporte.

No se precargan pacientes, citas, mediciones ni alimentos de prueba. El menú debe capturarse manualmente; todavía no hay un generador de menús ni exportación PDF implementados. La estatura para el cálculo provisional del IMC se captura manualmente en centímetros en la pantalla de medición; posteriormente debe sustituirse por el dato recibido del BIA. Al seleccionar un paciente, su nombre se actualiza en los encabezados de las pantallas del flujo.

Al abrir Objetivos nutricionales se sugiere una meta calórica con Mifflin–St Jeor y el factor de actividad elegido. Se resta 500 kcal para pérdida de peso, se suman 500 kcal para ganancia muscular y se usa mantenimiento para mantenimiento u otro objetivo. El usuario puede editar la sugerencia. Se necesita fecha de nacimiento válida y sexo Masculino o Femenino; si falta alguno de esos datos, la pantalla explica por qué no se pudo sugerir y permite capturar el objetivo manualmente.

## Sustituir memoria por PostgreSQL

Las pantallas deben seguir dependiendo de las operaciones del repositorio y no conectarse directamente a PostgreSQL. Para migrar, conserva estos métodos de `RepositorioMemoria` en una implementación PostgreSQL, cambia la creación del repositorio en `datos/__init__.py` y añade configuración de conexión y migraciones de esquema. Así se puede validar el flujo funcional antes de introducir persistencia permanente.
