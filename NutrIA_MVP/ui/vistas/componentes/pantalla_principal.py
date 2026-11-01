import os
from datetime import date, datetime

os.environ["QT_API"] = "pyside6"

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QGuiApplication
from qfluentwidgets import FluentWindow, NavigationItemPosition, FluentIcon, setTheme, Theme
from .calendario import calendarioInterface
from .proximas_citas import proximascitasInterface
from .nueva_cita import NuevaCitaInterface
from .reportes_de_pacientes import reportedePacientes
from .buscar_pacientes import buscarPacientes
from .agregar_paciente import agregarPaciente
from .ficha_paciente import FichaPacienteInterface
from .nueva_medicion import NuevaMedicionInterface
from .medicion import MedicionInterface
from .resultado_de_medicion import ResultadoMedicionInterface
from PySide6.QtCore import QTimer, Signal
from .objetivos_nuticionales import ObjetivosNutricionalesInterface
from .carga_menu import CargaMenuInterface
from .menu_personalizable import MenuPersonalizableInterface
from .editar_comida import EditarComidaInterface
from .vista_previa import VistaPreviaInterface
from .reporte_paciente import ReportePacienteInterface
from .configuracion import ConfiguracionInterface
from .inicio import InicioInterface
from PySide6.QtWidgets import QMessageBox
from datos import repositorio

class BaseInterface(QWidget):
    def __init__(self, nombre, parent=None):
        super().__init__(parent)
        self.btn_guardar = None
        self.btn_cancelar = None
        self.setObjectName(nombre)


class pantallaPrincipal(FluentWindow):
    sesion_cerrada = Signal()

    def centrar(self):
        pantalla = QGuiApplication.primaryScreen()
        if pantalla:
            area = pantalla.availableGeometry()
            marco = self.frameGeometry()
            marco.moveCenter(area.center())
            self.move(marco.topLeft())

    def __init__(self):
        super().__init__()
        self.setWindowTitle("NutrIA")
        self.resize(1100, 700)
        self.centrar()
        setTheme(Theme.DARK)

        self.inicio_interface = InicioInterface(self)

        self.paciente_interface = BaseInterface("pacienteInterface", self)
        self.buscar_pacientes_interface = buscarPacientes(self)
        self.agregar_paciente_interface = agregarPaciente(self)

        self.agenda_interface = BaseInterface("agendaInterface", self)
        self.calendario_interface = calendarioInterface(self)
        self.proximas_citas_interface = proximascitasInterface(self)
        self.nueva_cita_interface = NuevaCitaInterface(self)

        self.reportes_interface = BaseInterface("reportes", self)
        self.reportes_de_pacientes = reportedePacientes(self)

        self.configuracion_interface = ConfiguracionInterface(self)

        self.ficha_paciente_interface = FichaPacienteInterface(self)
        self.reporte_paciente_interface = ReportePacienteInterface(self)
        self._origen_reporte = self.ficha_paciente_interface

        self.nueva_medicion_interface = NuevaMedicionInterface(self)
        self.medicion_interface = MedicionInterface(self)
        self.resultado_medicion_interface = ResultadoMedicionInterface(self)

        self.objetivos_interface = ObjetivosNutricionalesInterface(self)
        self.carga_menu_interface = CargaMenuInterface(self)
        self.menu_personalizable_interface = MenuPersonalizableInterface(self)
        self.editar_comida_interface = EditarComidaInterface(self)
        self.vista_previa_interface = VistaPreviaInterface(self)

        #Inicio
        self.addSubInterface(self.inicio_interface, FluentIcon.HOME, "Inicio",
                             NavigationItemPosition.TOP)
        #Paciente
        self.addSubInterface(self.paciente_interface, FluentIcon.PEOPLE, "Paciente",
                             NavigationItemPosition.TOP)
        self.addSubInterface(self.agregar_paciente_interface, FluentIcon.ADD, "Agregar Paciente",
                             NavigationItemPosition.TOP, parent=self.paciente_interface)
        self.addSubInterface(self.buscar_pacientes_interface, FluentIcon.SEARCH, "Buscar Paciente",
                            NavigationItemPosition.TOP, parent=self.paciente_interface)


        #Agenda
        self.addSubInterface(self.agenda_interface, FluentIcon.CALENDAR, "Agenda",
                             NavigationItemPosition.TOP)
        self.addSubInterface(self.calendario_interface, FluentIcon.DATE_TIME, "Calendario",
                             NavigationItemPosition.TOP, parent=self.agenda_interface)
        self.addSubInterface(self.proximas_citas_interface, FluentIcon.HISTORY, "Proximas citas",
                             NavigationItemPosition.TOP, parent=self.agenda_interface)

        self.addSubInterface(self.nueva_cita_interface, FluentIcon.ADD, "Nueva cita",
                             NavigationItemPosition.TOP, parent=self.agenda_interface)
        self.navigationInterface.removeWidget("nuevaCitaInterface")

        #Reportes
        self.addSubInterface(self.reportes_interface, FluentIcon.DOCUMENT, "Reportes",
                             NavigationItemPosition.TOP)
        self.addSubInterface(self.reportes_de_pacientes, FluentIcon.DOCUMENT, "Reportes de pacientes",
                             NavigationItemPosition.TOP, parent=self.reportes_interface)

        self.addSubInterface(self.configuracion_interface, FluentIcon.SETTING, "Configuración",
                             NavigationItemPosition.BOTTOM)
        #Ficha paciente
        self.addSubInterface(self.ficha_paciente_interface, FluentIcon.PEOPLE, "Ficha paciente",
                             NavigationItemPosition.TOP)
        self.navigationInterface.removeWidget("fichaPacienteInterface")

        self.addSubInterface(self.reporte_paciente_interface, FluentIcon.DOCUMENT, "Reporte paciente",
                             NavigationItemPosition.TOP)
        self.navigationInterface.removeWidget("reportePacienteInterface")

        #Mediciones
        self.addSubInterface(self.nueva_medicion_interface, FluentIcon.ADD, "Nueva medicion",
                             NavigationItemPosition.TOP)
        self.navigationInterface.removeWidget("nuevaMedicionInterface")

        self.addSubInterface(self.medicion_interface, FluentIcon.HEART, "Medición",
                             NavigationItemPosition.TOP)
        self.navigationInterface.removeWidget("medicionInterface")

        self.addSubInterface(self.resultado_medicion_interface, FluentIcon.DOCUMENT, "Resultado",
                             NavigationItemPosition.TOP)
        self.navigationInterface.removeWidget("resultadoMedicionInterface")

        self.navigationInterface.addItem(
            routeKey="cerrar_sesion",
            icon=FluentIcon.POWER_BUTTON,
            text="Cerrar sesión",
            onClick=self.cerrar_sesion,
            position=NavigationItemPosition.BOTTOM
        )
        #Menu
        for interfaz, nombre, icono in [
            (self.objetivos_interface, "Objetivos", FluentIcon.TAG),
            (self.carga_menu_interface, "Carga", FluentIcon.SYNC),
            (self.menu_personalizable_interface, "Menu", FluentIcon.CAFE),
            (self.editar_comida_interface, "Editar comida", FluentIcon.EDIT),
            (self.vista_previa_interface, "Vista previa", FluentIcon.VIEW),
        ]:
            self.addSubInterface(interfaz, icono, nombre, NavigationItemPosition.TOP)
            self.navigationInterface.removeWidget(interfaz.objectName())

        self.calendario_interface.btn_nueva_cita.clicked.connect(
            lambda: self.switchTo(self.nueva_cita_interface)
        )
        self.nueva_cita_interface.btn_cancelar.clicked.connect(self.cancelar_cita)
        self.nueva_cita_interface.btn_guardar.clicked.connect(self.guardar_cita)
        
        self.buscar_pacientes_interface.btn_agregar_paciente.clicked.connect(
            lambda: self.switchTo(self.agregar_paciente_interface))
        self.agregar_paciente_interface.btn_cancelar.clicked.connect(self.cancelar_paciente)
        self.agregar_paciente_interface.btn_guardar.clicked.connect(self.guardar_paciente)

        self.reportes_de_pacientes.btn_regresar.clicked.connect(
            lambda: self.switchTo(self.inicio_interface))
        self.reporte_paciente_interface.btn_regresar.clicked.connect(self.regresar_reporte)
        self.reportes_de_pacientes.reporte_seleccionado.connect(self.abrir_reporte_desde_lista)

        #Ficha de paciente
        self.buscar_pacientes_interface.paciente_seleccionado.connect(self.abrir_paciente)
        self.buscar_pacientes_interface.btn_seleccionar.clicked.connect(self.abrir_paciente_seleccionado)

        self.ficha_paciente_interface.btn_editar.clicked.connect(
            self.editar_paciente)
        self.ficha_paciente_interface.btn_eliminar.clicked.connect(self.eliminar_paciente)

        self.ficha_paciente_interface.btn_ver_reporte.clicked.connect(
            lambda: self.abrir_reporte(self.ficha_paciente_interface))

        #Mediciones
        self.ficha_paciente_interface.btn_nueva_medicion.clicked.connect(
            self.iniciar_medicion)

        self.nueva_medicion_interface.btn_siguiente.clicked.connect(
            lambda: self.switchTo(self.medicion_interface))

        self.medicion_interface.btn_atras.clicked.connect(
            lambda: self.switchTo(self.nueva_medicion_interface))
        self.medicion_interface.btn_guardar.clicked.connect(
            self.guardar_medicion)

        #Resultado
        self.resultado_medicion_interface.btn_continuar.clicked.connect(
            self.mostrar_objetivos)

        #Objetivos
        self.objetivos_interface.btn_atras.clicked.connect(
            lambda: self.switchTo(self.resultado_medicion_interface))
        self.objetivos_interface.btn_continuar.clicked.connect(self.guardar_objetivos)

        #Menu personalizado
        self.menu_personalizable_interface.btn_regenerar.clicked.connect(self.generar_menu)
        self.menu_personalizable_interface.btn_vista_previa.clicked.connect(self.abrir_vista_previa)
        for comida, btn in self.menu_personalizable_interface.botones_editar.items():
            btn.clicked.connect(lambda _=False, nombre=comida: self.editar_comida(nombre))

        #Editar comida
        self.editar_comida_interface.btn_cancelar.clicked.connect(
            lambda: self.switchTo(self.menu_personalizable_interface))
        self.editar_comida_interface.btn_guardar.clicked.connect(self.guardar_comida)

        # Vista previa
        self.vista_previa_interface.btn_regresar.clicked.connect(
            lambda: self.switchTo(self.menu_personalizable_interface))

        # Inicio y configuración
        self.inicio_interface.btn_paciente.clicked.connect(
            lambda: self.switchTo(self.agregar_paciente_interface))
        self.inicio_interface.btn_medicion.clicked.connect(self.abrir_medicion_desde_inicio)
        self.inicio_interface.btn_cita.clicked.connect(
            lambda: self.switchTo(self.nueva_cita_interface))
        self.inicio_interface.paciente_seleccionado.connect(self.abrir_paciente)
        self.configuracion_interface.btn_cancelar.clicked.connect(
            lambda: self.switchTo(self.inicio_interface))
        self.configuracion_interface.btn_guardar.clicked.connect(
            lambda: self.switchTo(self.inicio_interface))

    #Cerrar sesion
    def cerrar_sesion(self):
        self.sesion_cerrada.emit()

    def abrir_medicion_desde_inicio(self):
        paciente_id = self.ficha_paciente_interface.paciente_id
        if paciente_id and repositorio.obtener_paciente(paciente_id):
            self.iniciar_medicion()
        else:
            self.switchTo(self.buscar_pacientes_interface)

    def abrir_paciente(self, paciente_id):
        if self.actualizar_contexto_paciente(paciente_id):
            self.switchTo(self.ficha_paciente_interface)

    def actualizar_contexto_paciente(self, paciente_id):
        paciente = repositorio.obtener_paciente(paciente_id)
        if not paciente:
            return False
        self.ficha_paciente_interface.cargar_paciente(paciente_id)
        nombre = f"{paciente['nombre']} {paciente['apellido']}"
        self.nueva_medicion_interface.lbl_paciente.setText(f"Paciente: {nombre}")
        self.medicion_interface.lbl_paciente.setText(f"Paciente: {nombre}")
        self.resultado_medicion_interface.limpiar(nombre)
        self.objetivos_interface.cargar_paciente(nombre, repositorio.obtener_objetivos(paciente_id))
        self.menu_personalizable_interface.cargar_menu(nombre, repositorio.obtener_menu(paciente_id))
        return True

    def abrir_paciente_seleccionado(self):
        if not self.buscar_pacientes_interface.tarjetas:
            QMessageBox.warning(self, "Sin pacientes", "favor de agregar pacientes")
            return
        paciente_id = self.buscar_pacientes_interface.paciente_id_seleccionado
        if paciente_id and repositorio.obtener_paciente(paciente_id):
            self.abrir_paciente(paciente_id)
        else:
            self.abrir_paciente(self.buscar_pacientes_interface.tarjetas[0].paciente_id)

    def guardar_paciente(self):
        datos = self.agregar_paciente_interface.obtener_datos()
        if not datos:
            return
        if self.agregar_paciente_interface.paciente_id:
            paciente_id = self.agregar_paciente_interface.paciente_id
            repositorio.actualizar_paciente(paciente_id, datos)
            self.actualizar_contexto_paciente(paciente_id)
        else:
            repositorio.crear_paciente(datos)
        self.buscar_pacientes_interface.actualizar_lista()
        self.inicio_interface.actualizar()
        self.agregar_paciente_interface.cargar_paciente()
        self.switchTo(self.buscar_pacientes_interface)

    def cancelar_paciente(self):
        self.agregar_paciente_interface.cargar_paciente()
        self.switchTo(self.buscar_pacientes_interface)

    def editar_paciente(self):
        paciente = repositorio.obtener_paciente(self.ficha_paciente_interface.paciente_id)
        self.agregar_paciente_interface.cargar_paciente(paciente)
        self.switchTo(self.agregar_paciente_interface)

    def eliminar_paciente(self):
        paciente_id = self.ficha_paciente_interface.paciente_id
        paciente = repositorio.obtener_paciente(paciente_id)
        if not paciente:
            return
        respuesta = QMessageBox.question(self, "Eliminar paciente",
            f"¿Eliminar a {paciente['nombre']} {paciente['apellido']} y sus datos asociados?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if respuesta == QMessageBox.Yes:
            repositorio.eliminar_paciente(paciente_id)
            self.limpiar_paciente_seleccionado()
            self.buscar_pacientes_interface.actualizar_lista()
            self.inicio_interface.actualizar()
            self.switchTo(self.buscar_pacientes_interface)

    def limpiar_paciente_seleccionado(self):
        self.ficha_paciente_interface.paciente_id = None
        self.ficha_paciente_interface.titulo.setText("Paciente: —")
        self.nueva_medicion_interface.lbl_paciente.setText("Paciente: —")
        self.medicion_interface.lbl_paciente.setText("Paciente: —")
        self.resultado_medicion_interface.limpiar()
        self.objetivos_interface.cargar_paciente("—", {})
        self.menu_personalizable_interface.cargar_menu("—", {})

    def iniciar_medicion(self):
        paciente = repositorio.obtener_paciente(self.ficha_paciente_interface.paciente_id)
        if paciente:
            nombre = f"{paciente['nombre']} {paciente['apellido']}"
            self.nueva_medicion_interface.lbl_paciente.setText(f"Paciente: {nombre}")
            self.medicion_interface.lbl_paciente.setText(f"Paciente: {nombre}")
            self.nueva_medicion_interface.limpiar()
            self.medicion_interface.limpiar()
            self.switchTo(self.nueva_medicion_interface)

    def guardar_medicion(self):
        objetivo = next((b.text() for b in self.nueva_medicion_interface.grupo_objetivo.buttons() if b.isChecked()), "")
        actividad = next((b.text() for b in self.nueva_medicion_interface.grupo_actividad.buttons() if b.isChecked()), "")
        motivo = self.nueva_medicion_interface.input_motivo.text().strip()
        datos = self.medicion_interface.obtener_datos(
            self.nueva_medicion_interface.fecha.date.toString("dd/MM/yyyy"), objetivo, actividad, motivo)
        if not datos:
            return
        medicion = repositorio.crear_medicion(self.ficha_paciente_interface.paciente_id, datos)
        self.ficha_paciente_interface.actualizar_mediciones()
        self.buscar_pacientes_interface.actualizar_lista()
        self.inicio_interface.actualizar()
        resultado = self.resultado_medicion_interface
        resultado.lbl_paciente.setText(self.medicion_interface.lbl_paciente.text())
        resultado.lbl_fecha.setText(medicion["fecha"])
        resultado.lbl_objetivo.setText(f"Objetivo: {medicion['objetivo'] or '—'}")
        resultado.lbl_motivo.setText(f"Motivo: {medicion['motivo'] or '—'}")
        resultado.lbl_actividad.setText(f"Actividad física: {medicion['actividad'] or '—'}")
        for titulo, valor in [("Peso:", f"{medicion['peso']} kg"), ("Grasa:", f"{medicion['grasa']}%"),
                              ("Masa Muscular:", f"{medicion['masa_muscular']}%"), ("IMC:", str(medicion["imc"])),
                              ("Agua:", f"{medicion['agua']}%"), ("Calorías:", f"{medicion['calorias']:g} kcal")]:
            resultado.valores[titulo].setText(valor)
        self.medicion_interface.limpiar()
        self.switchTo(resultado)

    def guardar_objetivos(self):
        paciente_id = self.ficha_paciente_interface.paciente_id
        if paciente_id:
            datos = self.objetivos_interface.obtener_datos()
            try:
                calorias = float(datos["calorias"].replace(",", "."))
                if calorias <= 0:
                    raise ValueError
            except ValueError:
                QMessageBox.warning(self, "Calorías objetivo", "Ingresa una cantidad de calorías objetivo mayor que cero.")
                return
            datos["calorias"] = str(round(calorias))
            repositorio.guardar_objetivos(paciente_id, datos)
        self.generar_menu()

    def mostrar_objetivos(self):
        self.sugerir_calorias_objetivo()
        self.switchTo(self.objetivos_interface)

    def sugerir_calorias_objetivo(self):
        paciente_id = self.ficha_paciente_interface.paciente_id
        paciente = repositorio.obtener_paciente(paciente_id) if paciente_id else None
        mediciones = repositorio.listar_mediciones(paciente_id) if paciente_id else []
        if not paciente or not mediciones:
            self.objetivos_interface.limpiar_sugerencia_calorias(
                "No hay datos suficientes para calcular una sugerencia. Puedes capturar las calorías manualmente.")
            return

        formatos = ("%d/%m/%Y", "%Y-%m-%d")
        fecha_nacimiento = None
        for formato in formatos:
            try:
                fecha_nacimiento = datetime.strptime(paciente.get("fecha_nacimiento", "").strip(), formato).date()
                break
            except (ValueError, AttributeError):
                continue
        if not fecha_nacimiento:
            self.objetivos_interface.limpiar_sugerencia_calorias(
                "Registra una fecha de nacimiento válida en la ficha para calcular la sugerencia. Puedes capturar las calorías manualmente.")
            return

        hoy = date.today()
        edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
        if edad <= 0:
            self.objetivos_interface.limpiar_sugerencia_calorias(
                "La fecha de nacimiento no permite calcular una edad válida. Puedes capturar las calorías manualmente.")
            return

        sexo = paciente.get("sexo", "").casefold()
        if sexo not in ("masculino", "femenino"):
            self.objetivos_interface.limpiar_sugerencia_calorias(
                "Para aplicar esta fórmula selecciona Masculino o Femenino en la ficha. Puedes capturar las calorías manualmente.")
            return

        objetivo = next((b.text() for b in self.nueva_medicion_interface.grupo_objetivo.buttons() if b.isChecked()), "")
        actividad = next((b.text() for b in self.nueva_medicion_interface.grupo_actividad.buttons() if b.isChecked()), "")
        factores = {
            "Sedentario": 1.20,
            "Ligeramente activo": 1.375,
            "Moderadamente activo": 1.55,
            "Muy activo": 1.725,
            "Extra activo": 1.90,
        }
        if not objetivo or actividad not in factores:
            self.objetivos_interface.limpiar_sugerencia_calorias(
                "Selecciona un objetivo y un nivel de actividad en la consulta para calcular la sugerencia.")
            return

        ultima_medicion = mediciones[0]
        try:
            peso = float(ultima_medicion["peso"])
            altura_cm = float(ultima_medicion["altura_cm"])
        except (KeyError, TypeError, ValueError):
            self.objetivos_interface.limpiar_sugerencia_calorias(
                "La medición no contiene peso y estatura válidos. Registra una nueva medición para calcular la sugerencia.")
            return

        ajuste_sexo = 5 if sexo == "masculino" else -161
        tmb = (10 * peso) + (6.25 * altura_cm) - (5 * edad) + ajuste_sexo
        mantenimiento = tmb * factores[actividad]
        if objetivo == "Pérdida de peso":
            calorias_objetivo = mantenimiento - 500
        elif objetivo == "Ganancia muscular":
            calorias_objetivo = mantenimiento + 500
        else:
            calorias_objetivo = mantenimiento

        self.objetivos_interface.mostrar_sugerencia_calorias(
            round(calorias_objetivo), round(mantenimiento), round(tmb))

    def editar_comida(self, comida):
        self.comida_actual = comida
        paciente_id = self.ficha_paciente_interface.paciente_id
        menu = repositorio.obtener_menu(paciente_id) if paciente_id else {}
        self.editar_comida_interface.cargar_comida(comida, menu.get(comida, []))
        self.switchTo(self.editar_comida_interface)

    def guardar_comida(self):
        paciente_id = self.ficha_paciente_interface.paciente_id
        if paciente_id and getattr(self, "comida_actual", None):
            repositorio.guardar_comida_menu(paciente_id, self.comida_actual,
                                            self.editar_comida_interface.obtener_alimentos())
            paciente = repositorio.obtener_paciente(paciente_id)
            self.menu_personalizable_interface.cargar_menu(
                f"{paciente['nombre']} {paciente['apellido']}", repositorio.obtener_menu(paciente_id))
        self.switchTo(self.menu_personalizable_interface)

    def abrir_vista_previa(self):
        paciente_id = self.ficha_paciente_interface.paciente_id
        paciente = repositorio.obtener_paciente(paciente_id) if paciente_id else None
        mediciones = repositorio.listar_mediciones(paciente_id) if paciente_id else []
        if paciente:
            self.vista_previa_interface.cargar_reporte(
                paciente, mediciones[0] if mediciones else {},
                repositorio.obtener_objetivos(paciente_id), repositorio.obtener_menu(paciente_id))
        self.switchTo(self.vista_previa_interface)

    def abrir_reporte(self, origen=None, paciente_id=None):
        paciente_id = paciente_id or self.ficha_paciente_interface.paciente_id
        paciente = repositorio.obtener_paciente(paciente_id) if paciente_id else None
        if not paciente:
            QMessageBox.warning(self, "Paciente no seleccionado", "Selecciona un paciente para ver su reporte.")
            return
        if origen is not None:
            self._origen_reporte = origen
        self.reporte_paciente_interface.cargar_paciente(
            paciente, repositorio.listar_mediciones(paciente_id))
        self.switchTo(self.reporte_paciente_interface)

    def abrir_reporte_desde_lista(self, paciente_id):
        self.actualizar_contexto_paciente(paciente_id)
        self.abrir_reporte(self.reportes_de_pacientes, paciente_id)

    def regresar_reporte(self):
        self.switchTo(self._origen_reporte)

    def abrir_reportes_paciente(self):
        self.reportes_de_pacientes.input_buscar.clear()
        self.reportes_de_pacientes.actualizar(self.ficha_paciente_interface.paciente_id)
        self.switchTo(self.reportes_de_pacientes)

    def cancelar_cita(self):
        self.nueva_cita_interface.limpiar()
        self.switchTo(self.calendario_interface)

    def guardar_cita(self):
        datos = self.nueva_cita_interface.obtener_datos()
        if not datos:
            return
        try:
            repositorio.crear_cita(datos)
        except ValueError as error:
            QMessageBox.warning(self, "Horario no disponible", str(error))
            return
        self.proximas_citas_interface.actualizar()
        self.inicio_interface.actualizar()
        self.nueva_cita_interface.limpiar()
        self.switchTo(self.proximas_citas_interface)

    def generar_menu(self):
        self.switchTo(self.carga_menu_interface)
        paciente_id = self.ficha_paciente_interface.paciente_id
        if paciente_id:
            menu = repositorio.obtener_menu(paciente_id)
            paciente = repositorio.obtener_paciente(paciente_id)
            self.menu_personalizable_interface.cargar_menu(
                f"{paciente['nombre']} {paciente['apellido']}", menu)
        self.inicio_interface.actualizar()
        QTimer.singleShot(500, lambda: self.switchTo(self.menu_personalizable_interface))
