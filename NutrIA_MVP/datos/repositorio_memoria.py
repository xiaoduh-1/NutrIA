"""Repositorio temporal en memoria. Se reemplazará por una implementación PostgreSQL."""

from datetime import date, datetime
from uuid import uuid4


class RepositorioMemoria:
    def __init__(self):
        self.pacientes = {}
        self.citas = {}
        self.mediciones = {}
        self.objetivos = {}
        self.menus = {}

    def crear_paciente(self, datos):
        paciente = {**datos, "id": str(uuid4()), "creado_en": datetime.now().isoformat(timespec="seconds")}
        self.pacientes[paciente["id"]] = paciente
        return paciente

    def actualizar_paciente(self, paciente_id, datos):
        if paciente_id not in self.pacientes:
            return None
        self.pacientes[paciente_id].update(datos)
        return self.pacientes[paciente_id]

    def obtener_paciente(self, paciente_id):
        return self.pacientes.get(paciente_id)

    def listar_pacientes(self, busqueda=""):
        termino = busqueda.casefold().strip()
        return sorted(
            [p for p in self.pacientes.values()
             if termino in f"{p['nombre']} {p['apellido']} {p['telefono']} {p['correo']}".casefold()],
            key=lambda p: (p["apellido"].casefold(), p["nombre"].casefold()),
        )

    def eliminar_paciente(self, paciente_id):
        paciente = self.pacientes.pop(paciente_id, None)
        if paciente:
            nombre = f"{paciente['nombre']} {paciente['apellido']}"
            self.mediciones.pop(paciente_id, None)
            self.objetivos.pop(paciente_id, None)
            self.menus.pop(paciente_id, None)
            self.citas = {cid: cita for cid, cita in self.citas.items() if cita.get("paciente_id") != paciente_id}
            return nombre
        return None

    def crear_cita(self, datos):
        conflicto = self.buscar_conflicto_cita(datos["fecha"], datos["hora"])
        if conflicto:
            raise ValueError(
                f"Debe haber al menos 30 minutos entre citas. Ya existe una cita a las {conflicto['hora']}."
            )
        cita = {**datos, "id": str(uuid4()), "creado_en": datetime.now().isoformat(timespec="seconds")}
        self.citas[cita["id"]] = cita
        return cita

    def buscar_conflicto_cita(self, fecha, hora, separacion_minutos=30):
        hora_solicitada = datetime.strptime(hora, "%H:%M")
        for cita in self.listar_citas(fecha):
            hora_existente = datetime.strptime(cita["hora"], "%H:%M")
            diferencia = abs((hora_solicitada - hora_existente).total_seconds()) / 60
            if diferencia < separacion_minutos:
                return cita
        return None

    def listar_citas(self, fecha=None):
        fecha = fecha or date.today().isoformat()
        return sorted((c for c in self.citas.values() if c["fecha"] == fecha), key=lambda c: c["hora"])

    def crear_medicion(self, paciente_id, datos):
        medicion = {**datos, "id": str(uuid4()), "paciente_id": paciente_id,
                    "creado_en": datetime.now().isoformat(timespec="seconds")}
        self.mediciones.setdefault(paciente_id, []).append(medicion)
        return medicion

    def listar_mediciones(self, paciente_id):
        return list(reversed(self.mediciones.get(paciente_id, [])))

    def guardar_objetivos(self, paciente_id, datos):
        self.objetivos[paciente_id] = dict(datos)
        return self.objetivos[paciente_id]

    def obtener_objetivos(self, paciente_id):
        return self.objetivos.get(paciente_id, {})

    def obtener_menu(self, paciente_id):
        return self.menus.get(paciente_id, {})

    def guardar_comida_menu(self, paciente_id, comida, alimentos):
        menu = self.menus.setdefault(paciente_id, {})
        menu[comida] = list(alimentos)
        return menu

repositorio = RepositorioMemoria()
