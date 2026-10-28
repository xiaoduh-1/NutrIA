import os

os.environ["QT_API"] = "pyside6"

from PySide6.QtWidgets import QWidget
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
from PySide6.QtCore import QTimer
from .objetivos_nuticionales import ObjetivosNutricionalesInterface
from .carga_menu import CargaMenuInterface
from .menu_personalizable import MenuPersonalizableInterface
from .editar_comida import EditarComidaInterface
from .vista_previa import VistaPreviaInterface

class BaseInterface(QWidget):
    def __init__(self, nombre, parent=None):
        super().__init__(parent)
        self.btn_guardar = None
        self.btn_cancelar = None
        self.setObjectName(nombre)


class pantallaPrincipal(FluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NutrIA")
        self.resize(1100, 700)
        setTheme(Theme.DARK)

        self.inicio_interface = BaseInterface("inicioInterface", self)

        self.paciente_interface = BaseInterface("pacienteInterface", self)
        self.buscar_pacientes_interface = buscarPacientes(self)
        self.agregar_paciente_interface = agregarPaciente(self)

        self.agenda_interface = BaseInterface("agendaInterface", self)
        self.calendario_interface = calendarioInterface(self)
        self.proximas_citas_interface = proximascitasInterface(self)
        self.nueva_cita_interface = NuevaCitaInterface(self)

        self.reportes_interface = BaseInterface("reportes", self)
        self.reportes_de_pacientes = reportedePacientes(self)

        self.configuracion_interface = BaseInterface("configuracionInterface", self)

        self.ficha_paciente_interface = FichaPacienteInterface(self)

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
        self.nueva_cita_interface.btn_cancelar.clicked.connect(
            lambda: self.switchTo(self.calendario_interface)
        )
        self.nueva_cita_interface.btn_guardar.clicked.connect(
            lambda: self.switchTo(self.calendario_interface)
        )
        
        self.buscar_pacientes_interface.btn_agregar_paciente.clicked.connect(
            lambda: self.switchTo(self.agregar_paciente_interface))
        self.agregar_paciente_interface.btn_cancelar.clicked.connect(
            lambda: self.switchTo(self.buscar_pacientes_interface))
        self.agregar_paciente_interface.btn_guardar.clicked.connect(
            lambda: self.switchTo(self.buscar_pacientes_interface))

        self.reportes_de_pacientes.btn_regresar.clicked.connect(
            lambda: self.switchTo(self.inicio_interface))

        #Ficha de paciente
        for tarjeta in self.buscar_pacientes_interface.tarjetas:
            tarjeta.btn_ver.clicked.connect(
                lambda: self.switchTo(self.ficha_paciente_interface))

        self.ficha_paciente_interface.btn_editar.clicked.connect(
            lambda: self.switchTo(self.agregar_paciente_interface))

        self.ficha_paciente_interface.btn_ver_reporte.clicked.connect(
            lambda: self.switchTo(self.reportes_pacientes_interface))

        #Mediciones
        self.ficha_paciente_interface.btn_nueva_medicion.clicked.connect(
            lambda: self.switchTo(self.nueva_medicion_interface))

        self.nueva_medicion_interface.btn_siguiente.clicked.connect(
            lambda: self.switchTo(self.medicion_interface))

        self.medicion_interface.btn_atras.clicked.connect(
            lambda: self.switchTo(self.nueva_medicion_interface))
        self.medicion_interface.btn_guardar.clicked.connect(
            lambda: self.switchTo(self.resultado_medicion_interface))

        #Resultado
        self.resultado_medicion_interface.btn_continuar.clicked.connect(
            lambda: self.switchTo(self.objetivos_interface))

        #Objetivos
        self.objetivos_interface.btn_atras.clicked.connect(
            lambda: self.switchTo(self.resultado_medicion_interface))
        self.objetivos_interface.btn_continuar.clicked.connect(self.generar_menu)

        #Menu personalizado
        self.menu_personalizable_interface.btn_regenerar.clicked.connect(self.generar_menu)
        self.menu_personalizable_interface.btn_vista_previa.clicked.connect(
            lambda: self.switchTo(self.vista_previa_interface))
        for btn in self.menu_personalizable_interface.botones_editar.values():
            btn.clicked.connect(lambda: self.switchTo(self.editar_comida_interface))

        #Editar comida
        self.editar_comida_interface.btn_cancelar.clicked.connect(
            lambda: self.switchTo(self.menu_personalizable_interface))
        self.editar_comida_interface.btn_guardar.clicked.connect(
            lambda: self.switchTo(self.menu_personalizable_interface))

        # Vista previa
        self.vista_previa_interface.btn_regresar.clicked.connect(
            lambda: self.switchTo(self.menu_personalizable_interface))

    #Cerrar sesion
    def cerrar_sesion(self):
        self.close()
    def generar_menu(self):
        self.switchTo(self.carga_menu_interface)
        QTimer.singleShot(3000, lambda: self.switchTo(self.menu_personalizable_interface))
