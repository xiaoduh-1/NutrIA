"""Repositorio PostgreSQL para los módulos de persistencia actuales de NutrIA MVP."""

from datetime import date, datetime
from uuid import UUID

from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from .conexion import conectar
from .repositorio_memoria import RepositorioMemoria


class RepositorioTransicional:
    ORDEN_COMIDAS = {
        "Desayuno": 0,
        "Colación I": 1,
        "Comida": 2,
        "Colación II": 3,
        "Cena": 4,
    }

    CAMPOS_PACIENTE = (
        "nombre", "apellido", "fecha_nacimiento", "sexo", "telefono",
        "correo", "observaciones",
    )

    def __init__(self):
        self.memoria = RepositorioMemoria()

    @property
    def citas(self):
        return {cita["id"]: cita for cita in self._listar_citas()}

    @property
    def mediciones(self):
        agrupadas = {}
        for medicion in self._listar_mediciones():
            agrupadas.setdefault(medicion["paciente_id"], []).append(medicion)
        return agrupadas

    @staticmethod
    def _fecha_db(valor):
        if not valor:
            return None
        if isinstance(valor, date):
            return valor
        texto = str(valor).strip()
        for formato in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(texto, formato).date()
            except ValueError:
                pass
        raise ValueError("La fecha de nacimiento debe tener formato DD/MM/AAAA.")

    @classmethod
    def _formatear_paciente(cls, fila):
        if fila is None:
            return None
        paciente = dict(fila)
        paciente["id"] = str(paciente["id"])
        if paciente.get("fecha_nacimiento"):
            paciente["fecha_nacimiento"] = paciente["fecha_nacimiento"].strftime("%d/%m/%Y")
        for campo in ("creado_en", "actualizado_en"):
            if paciente.get(campo):
                paciente[campo] = paciente[campo].isoformat(timespec="seconds")
        return paciente

    @staticmethod
    def _formatear_cita(fila):
        if fila is None:
            return None
        cita = dict(fila)
        cita["id"] = str(cita["id"])
        cita["paciente_id"] = str(cita["paciente_id"])
        cita["fecha"] = cita["fecha"].isoformat()
        cita["hora"] = cita["hora"].strftime("%H:%M")
        cita["paciente"] = f"{cita.pop('paciente_nombre')} {cita.pop('paciente_apellido')}"
        if cita.get("creado_en"):
            cita["creado_en"] = cita["creado_en"].isoformat(timespec="seconds")
        return cita

    @staticmethod
    def _formatear_medicion(fila):
        if fila is None:
            return None
        medicion = dict(fila)
        medicion["id"] = str(medicion["id"])
        medicion["paciente_id"] = str(medicion["paciente_id"])
        medicion["fecha"] = medicion["fecha"].strftime("%d/%m/%Y")
        equivalencias = {
            "peso_kg": "peso",
            "grasa_pct": "grasa",
            "masa_muscular_pct": "masa_muscular",
            "agua_pct": "agua",
            "calorias_kcal": "calorias",
        }
        for campo_db, campo_ui in equivalencias.items():
            medicion[campo_ui] = float(medicion.pop(campo_db))
        medicion["altura_cm"] = float(medicion["altura_cm"])
        medicion["imc"] = float(medicion["imc"])
        if medicion.get("creado_en"):
            medicion["creado_en"] = medicion["creado_en"].isoformat(timespec="seconds")
        return medicion

    @staticmethod
    def _consulta_mediciones():
        return (
            "SELECT id, paciente_id, fecha, objetivo, actividad, motivo, peso_kg, "
            "altura_cm, grasa_pct, masa_muscular_pct, agua_pct, calorias_kcal, imc, creado_en "
            "FROM mediciones"
        )

    @staticmethod
    def _consulta_citas():
        return (
            "SELECT c.id, c.paciente_id, c.fecha, c.hora, c.creado_en, "
            "p.nombre AS paciente_nombre, p.apellido AS paciente_apellido "
            "FROM citas c JOIN pacientes p ON p.id = c.paciente_id"
        )

    def crear_paciente(self, datos):
        columnas = ", ".join(self.CAMPOS_PACIENTE)
        valores = [datos.get(campo, "") for campo in self.CAMPOS_PACIENTE]
        valores[2] = self._fecha_db(valores[2])
        placeholders = ", ".join(["%s"] * len(self.CAMPOS_PACIENTE))
        with conectar() as conexion, conexion.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                f"INSERT INTO pacientes ({columnas}) VALUES ({placeholders}) RETURNING *",
                valores,
            )
            paciente = self._formatear_paciente(cursor.fetchone())
        return paciente

    def actualizar_paciente(self, paciente_id, datos):
        campos = [campo for campo in self.CAMPOS_PACIENTE if campo in datos]
        if not campos:
            return self.obtener_paciente(paciente_id)
        asignaciones = ", ".join(f"{campo} = %s" for campo in campos)
        valores = [datos[campo] for campo in campos]
        if "fecha_nacimiento" in campos:
            valores[campos.index("fecha_nacimiento")] = self._fecha_db(
                datos["fecha_nacimiento"]
            )
        valores.append(UUID(str(paciente_id)))
        with conectar() as conexion, conexion.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                f"UPDATE pacientes SET {asignaciones}, actualizado_en = CURRENT_TIMESTAMP "
                "WHERE id = %s RETURNING *",
                valores,
            )
            paciente = self._formatear_paciente(cursor.fetchone())
        return paciente

    def obtener_paciente(self, paciente_id):
        try:
            paciente_id = UUID(str(paciente_id))
        except (ValueError, TypeError, AttributeError):
            return None
        with conectar() as conexion, conexion.cursor(row_factory=dict_row) as cursor:
            cursor.execute("SELECT * FROM pacientes WHERE id = %s", (paciente_id,))
            return self._formatear_paciente(cursor.fetchone())

    def listar_pacientes(self, busqueda=""):
        termino = f"%{busqueda.strip()}%"
        with conectar() as conexion, conexion.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                "SELECT * FROM pacientes "
                "WHERE concat_ws(' ', nombre, apellido, telefono, correo) ILIKE %s "
                "ORDER BY apellido, nombre",
                (termino,),
            )
            return [self._formatear_paciente(fila) for fila in cursor.fetchall()]

    def eliminar_paciente(self, paciente_id):
        paciente = self.obtener_paciente(paciente_id)
        if not paciente:
            return None
        paciente_uuid = UUID(str(paciente_id))
        with conectar() as conexion, conexion.cursor() as cursor:
            cursor.execute("DELETE FROM pacientes WHERE id = %s", (paciente_uuid,))
        # Limpieza de los módulos que aún viven en memoria mientras migramos.
        self.memoria.citas = {
            cita_id: cita for cita_id, cita in self.memoria.citas.items()
            if str(cita.get("paciente_id")) != str(paciente_id)
        }
        self.memoria.mediciones.pop(str(paciente_id), None)
        self.memoria.objetivos.pop(str(paciente_id), None)
        self.memoria.menus.pop(str(paciente_id), None)
        return f"{paciente['nombre']} {paciente['apellido']}"

    def crear_cita(self, datos):
        conflicto = self.buscar_conflicto_cita(datos["fecha"], datos["hora"])
        if conflicto:
            raise ValueError(
                f"Debe haber al menos 30 minutos entre citas. Ya existe una cita a las {conflicto['hora']}."
            )
        fecha = self._fecha_db(datos["fecha"])
        hora = datetime.strptime(datos["hora"], "%H:%M").time()
        paciente_id = UUID(str(datos["paciente_id"]))
        with conectar() as conexion, conexion.cursor() as cursor:
            cursor.execute(
                "INSERT INTO citas (paciente_id, fecha, hora) VALUES (%s, %s, %s) RETURNING id",
                (paciente_id, fecha, hora),
            )
            cita_id = cursor.fetchone()[0]
        return next(cita for cita in self._listar_citas() if cita["id"] == str(cita_id))

    def buscar_conflicto_cita(self, fecha, hora, separacion_minutos=30):
        hora_solicitada = datetime.strptime(hora, "%H:%M")
        for cita in self.listar_citas(str(self._fecha_db(fecha))):
            hora_existente = datetime.strptime(cita["hora"], "%H:%M")
            diferencia = abs((hora_solicitada - hora_existente).total_seconds()) / 60
            if diferencia < separacion_minutos:
                return cita
        return None

    def _listar_citas(self, fecha=None):
        consulta = self._consulta_citas()
        parametros = ()
        if fecha is not None:
            consulta += " WHERE c.fecha = %s"
            parametros = (self._fecha_db(fecha),)
        consulta += " ORDER BY c.fecha, c.hora"
        with conectar() as conexion, conexion.cursor(row_factory=dict_row) as cursor:
            cursor.execute(consulta, parametros)
            return [self._formatear_cita(fila) for fila in cursor.fetchall()]

    def listar_citas(self, fecha=None):
        fecha = fecha or date.today().isoformat()
        return self._listar_citas(fecha)

    def crear_medicion(self, paciente_id, datos):
        fecha = self._fecha_db(datos["fecha"])
        valores = (
            UUID(str(paciente_id)), fecha, datos.get("objetivo", ""),
            datos.get("actividad", ""), datos.get("motivo", ""),
            datos["peso"], datos["altura_cm"], datos["grasa"],
            datos["masa_muscular"], datos["agua"], datos["calorias"], datos["imc"],
        )
        with conectar() as conexion, conexion.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                "INSERT INTO mediciones "
                "(paciente_id, fecha, objetivo, actividad, motivo, peso_kg, altura_cm, "
                "grasa_pct, masa_muscular_pct, agua_pct, calorias_kcal, imc) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *",
                valores,
            )
            return self._formatear_medicion(cursor.fetchone())

    def _listar_mediciones(self, paciente_id=None):
        consulta = self._consulta_mediciones()
        parametros = ()
        if paciente_id is not None:
            consulta += " WHERE paciente_id = %s"
            parametros = (UUID(str(paciente_id)),)
        consulta += " ORDER BY fecha DESC, creado_en DESC"
        with conectar() as conexion, conexion.cursor(row_factory=dict_row) as cursor:
            cursor.execute(consulta, parametros)
            return [self._formatear_medicion(fila) for fila in cursor.fetchall()]

    def listar_mediciones(self, paciente_id):
        return self._listar_mediciones(paciente_id)

    @staticmethod
    def _formatear_objetivos(fila):
        if fila is None:
            return {}
        return {
            "calorias": str(fila["calorias_kcal"]),
            "macronutrientes": fila["macronutrientes"] or {},
            "preferencia": fila["preferencia"],
            "alergias": fila["alergias"],
            "evitar": fila["alimentos_evitar"],
        }

    def guardar_objetivos(self, paciente_id, datos):
        try:
            calorias = round(float(str(datos["calorias"]).replace(",", ".")))
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("Las calorías objetivo deben ser un número válido.") from error
        if calorias <= 0:
            raise ValueError("Las calorías objetivo deben ser mayores que cero.")
        macros = datos.get("macronutrientes") or {}
        with conectar() as conexion, conexion.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                "INSERT INTO objetivos_nutricionales "
                "(paciente_id, calorias_kcal, macronutrientes, preferencia, alergias, alimentos_evitar) "
                "VALUES (%s, %s, %s, %s, %s, %s) RETURNING calorias_kcal, macronutrientes, "
                "preferencia, alergias, alimentos_evitar",
                (
                    UUID(str(paciente_id)), calorias, Jsonb(macros),
                    datos.get("preferencia", ""), datos.get("alergias", ""),
                    datos.get("evitar", ""),
                ),
            )
            return self._formatear_objetivos(cursor.fetchone())

    def obtener_objetivos(self, paciente_id):
        with conectar() as conexion, conexion.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                "SELECT calorias_kcal, macronutrientes, preferencia, alergias, alimentos_evitar "
                "FROM objetivos_nutricionales WHERE paciente_id = %s "
                "ORDER BY creado_en DESC, id DESC LIMIT 1",
                (UUID(str(paciente_id)),),
            )
            return self._formatear_objetivos(cursor.fetchone())

    def obtener_menu(self, paciente_id):
        paciente_uuid = UUID(str(paciente_id))
        menu = {}
        with conectar() as conexion, conexion.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                "SELECT id FROM menus WHERE paciente_id = %s "
                "ORDER BY actualizado_en DESC, creado_en DESC LIMIT 1",
                (paciente_uuid,),
            )
            menu_row = cursor.fetchone()
            if not menu_row:
                return menu
            cursor.execute(
                "SELECT mc.nombre AS comida, ma.id AS item_id, ma.alimento_id, "
                "ma.nombre AS alimento, ma.porcion, ma.cantidad_base, ma.unidad_base, "
                "ma.calorias_kcal, ma.proteinas_g, ma.carbohidratos_g, ma.grasas_g "
                "FROM menu_comidas mc LEFT JOIN menu_alimentos ma ON ma.comida_id = mc.id "
                "WHERE mc.menu_id = %s ORDER BY mc.orden, ma.orden, ma.id",
                (menu_row["id"],),
            )
            for fila in cursor.fetchall():
                alimentos = menu.setdefault(fila["comida"], [])
                if fila["alimento"] is not None:
                    alimentos.append({
                        "id": str(fila["item_id"]),
                        "alimento_id": str(fila["alimento_id"]) if fila["alimento_id"] else None,
                        "nombre": fila["alimento"],
                        "porcion": fila["porcion"],
                        "cantidad_base": float(fila["cantidad_base"]) if fila["cantidad_base"] is not None else None,
                        "unidad_base": fila["unidad_base"],
                        "calorias_kcal": float(fila["calorias_kcal"]) if fila["calorias_kcal"] is not None else None,
                        "proteinas_g": float(fila["proteinas_g"]) if fila["proteinas_g"] is not None else None,
                        "carbohidratos_g": float(fila["carbohidratos_g"]) if fila["carbohidratos_g"] is not None else None,
                        "grasas_g": float(fila["grasas_g"]) if fila["grasas_g"] is not None else None,
                    })
        return menu

    def buscar_alimentos(self, busqueda="", categoria=None, limite=50):
        termino = f"%{busqueda.strip()}%"
        limite = max(1, min(int(limite), 200))
        consulta = (
            "SELECT id, nombre, categoria, unidad_base, calorias_100, proteinas_100, "
            "carbohidratos_100, grasas_100, fibra_100, fuente, es_dato_prueba "
            "FROM alimentos WHERE activo AND nombre ILIKE %s"
        )
        parametros = [termino]
        if categoria:
            consulta += " AND categoria = %s"
            parametros.append(categoria)
        consulta += " ORDER BY categoria, nombre LIMIT %s"
        parametros.append(limite)
        with conectar() as conexion, conexion.cursor(row_factory=dict_row) as cursor:
            cursor.execute(consulta, parametros)
            resultados = []
            for fila in cursor.fetchall():
                alimento = dict(fila)
                alimento["id"] = str(alimento["id"])
                for campo in ("calorias_100", "proteinas_100", "carbohidratos_100", "grasas_100", "fibra_100"):
                    if alimento[campo] is not None:
                        alimento[campo] = float(alimento[campo])
                resultados.append(alimento)
            return resultados

    def guardar_comida_menu(self, paciente_id, comida, alimentos):
        paciente_uuid = UUID(str(paciente_id))
        orden = self.ORDEN_COMIDAS.get(comida, len(self.ORDEN_COMIDAS))
        with conectar() as conexion, conexion.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM menus WHERE paciente_id = %s "
                "ORDER BY actualizado_en DESC, creado_en DESC LIMIT 1 FOR UPDATE",
                (paciente_uuid,),
            )
            fila_menu = cursor.fetchone()
            if fila_menu:
                menu_id = fila_menu[0]
            else:
                cursor.execute(
                    "INSERT INTO menus (paciente_id) VALUES (%s) RETURNING id",
                    (paciente_uuid,),
                )
                menu_id = cursor.fetchone()[0]

            cursor.execute(
                "UPDATE menus SET actualizado_en = CURRENT_TIMESTAMP WHERE id = %s",
                (menu_id,),
            )
            cursor.execute(
                "INSERT INTO menu_comidas (menu_id, nombre, orden) VALUES (%s, %s, %s) "
                "ON CONFLICT (menu_id, nombre) DO UPDATE SET orden = EXCLUDED.orden "
                "RETURNING id",
                (menu_id, comida, orden),
            )
            comida_id = cursor.fetchone()[0]
            cursor.execute("DELETE FROM menu_alimentos WHERE comida_id = %s", (comida_id,))
            for indice, alimento in enumerate(alimentos):
                if isinstance(alimento, dict):
                    nombre = str(alimento.get("nombre", "")).strip()
                    porcion = str(alimento.get("porcion", "")).strip()
                    alimento_id = alimento.get("alimento_id")
                else:
                    nombre, porcion = (str(valor).strip() for valor in alimento)
                    alimento_id = None
                if not nombre or not porcion:
                    continue

                datos_nutricionales = (None, None, None, None, None, None)
                if alimento_id:
                    cursor.execute(
                        "SELECT nombre, unidad_base, calorias_100, proteinas_100, "
                        "carbohidratos_100, grasas_100 FROM alimentos "
                        "WHERE id = %s AND activo",
                        (UUID(str(alimento_id)),),
                    )
                    catalogo = cursor.fetchone()
                    if not catalogo:
                        raise ValueError("El alimento seleccionado ya no está disponible en el catálogo.")
                    cantidad = float(alimento.get("cantidad_base") or 0)
                    unidad = catalogo[1]
                    if cantidad <= 0:
                        raise ValueError("La cantidad del alimento debe ser mayor que cero.")
                    nombre = catalogo[0]
                    porcion = f"{cantidad:g} {unidad}"
                    alimento_uuid = UUID(str(alimento_id))
                    calorias, proteinas, carbohidratos, grasas = (
                        float(catalogo[pos]) * cantidad / 100 for pos in range(2, 6)
                    )
                    datos_nutricionales = (
                        alimento_uuid, cantidad, unidad, calorias, proteinas,
                        carbohidratos, grasas,
                    )
                else:
                    datos_nutricionales = (None, None, None, None, None, None, None)
                cursor.execute(
                    "INSERT INTO menu_alimentos "
                    "(comida_id, alimento_id, nombre, porcion, cantidad_base, unidad_base, "
                    "calorias_kcal, proteinas_g, carbohidratos_g, grasas_g, orden) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (comida_id, *datos_nutricionales[:1], nombre, porcion,
                     *datos_nutricionales[1:], indice),
                )
        return self.obtener_menu(paciente_uuid)

    # Todos los módulos de persistencia actuales ya usan PostgreSQL.
    def __getattr__(self, nombre):
        return getattr(self.memoria, nombre)
