import os
from datetime import date, datetime

os.environ["QT_API"] = "pyside6"

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
from datos.sesion_nutriologo import sesion_nutriologo
from devices.amazing_vision_rtc2017 import LectorRTC2017
from services.estimaciones_composicion import (
    calcular_edad,
    estimar_composicion_corporal,
)

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

        self.buscar_pacientes_interface = buscarPacientes(self)
        self.agregar_paciente_interface = agregarPaciente(self)

        self.calendario_interface = calendarioInterface(self)
        self.proximas_citas_interface = proximascitasInterface(self)
        self.nueva_cita_interface = NuevaCitaInterface(self)
        self._fecha_citas_actual = date.today().isoformat()
        self._fecha_citas_edicion_origen = None

        self.reportes_de_pacientes = reportedePacientes(self)

        self.configuracion_interface = ConfiguracionInterface(self)

        self.ficha_paciente_interface = FichaPacienteInterface(self)
        self.reporte_paciente_interface = ReportePacienteInterface(self)
        self._origen_reporte = self.ficha_paciente_interface

        self.nueva_medicion_interface = NuevaMedicionInterface(self)
        self.medicion_interface = MedicionInterface(self)
        self.resultado_medicion_interface = ResultadoMedicionInterface(self)
        self._altura_medicion_actual = None
        self._lector_bascula = None
        self._ble_error = False
        self._ble_confirmacion_pendiente = False
        self._ble_lector_finalizado = False

        self.objetivos_interface = ObjetivosNutricionalesInterface(self)
        self.carga_menu_interface = CargaMenuInterface(self)
        self.menu_personalizable_interface = MenuPersonalizableInterface(self)
        self.editar_comida_interface = EditarComidaInterface(self)
        self.vista_previa_interface = VistaPreviaInterface(self)

        #Inicio
        self.addSubInterface(self.inicio_interface, FluentIcon.HOME, "Inicio",
                             NavigationItemPosition.TOP)
        #Paciente
        self.navigationInterface.addItem(
            routeKey="pacienteGroup", icon=FluentIcon.PEOPLE, text="Paciente",
            selectable=False, position=NavigationItemPosition.TOP,
        )
        self.addSubInterface(self.agregar_paciente_interface, FluentIcon.ADD, "Agregar Paciente",
                             NavigationItemPosition.TOP, parent="pacienteGroup")
        self.addSubInterface(self.buscar_pacientes_interface, FluentIcon.SEARCH, "Buscar Paciente",
                            NavigationItemPosition.TOP, parent="pacienteGroup")


        #Agenda
        self.navigationInterface.addItem(
            routeKey="agendaGroup", icon=FluentIcon.CALENDAR, text="Agenda",
            selectable=False, position=NavigationItemPosition.TOP,
        )
        self.addSubInterface(self.calendario_interface, FluentIcon.DATE_TIME, "Calendario",
                             NavigationItemPosition.TOP, parent="agendaGroup")
        self.addSubInterface(self.proximas_citas_interface, FluentIcon.HISTORY, "Proximas citas",
                             NavigationItemPosition.TOP, parent="agendaGroup")
        self.navigationInterface.widget("proximasCitasInterface").clicked.connect(
            lambda *_: self.proximas_citas_interface.actualizar()
        )

        self.addSubInterface(self.nueva_cita_interface, FluentIcon.ADD, "Nueva cita",
                             NavigationItemPosition.TOP, parent="agendaGroup")
        self.navigationInterface.removeWidget("nuevaCitaInterface")

        #Reportes
        self.navigationInterface.addItem(
            routeKey="reportesGroup", icon=FluentIcon.DOCUMENT, text="Reportes",
            selectable=False, position=NavigationItemPosition.TOP,
        )
        self.addSubInterface(self.reportes_de_pacientes, FluentIcon.DOCUMENT, "Reportes de pacientes",
                             NavigationItemPosition.TOP, parent="reportesGroup")

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
        self.calendario_interface.calendario.activated.connect(self.abrir_citas_fecha)
        self.proximas_citas_interface.cita_seleccionada.connect(self.abrir_editar_cita)
        self.nueva_cita_interface.btn_cancelar.clicked.connect(self.cancelar_cita)
        self.nueva_cita_interface.btn_guardar.clicked.connect(self.guardar_cita)
        self.nueva_cita_interface.btn_eliminar.clicked.connect(self.eliminar_cita)
        
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
            self.continuar_a_medicion)
        self.medicion_interface.btn_iniciar.clicked.connect(
            self.iniciar_lectura_bascula)

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
            self.cancelar_configuracion)
        self.configuracion_interface.btn_guardar.clicked.connect(self.guardar_configuracion)

    #Cerrar sesion
    def cerrar_sesion(self):
        self.sesion_cerrada.emit()

    def closeEvent(self, event):
        if self._lector_bascula and self._lector_bascula.isRunning():
            self._lector_bascula.cancelar()
            self._lector_bascula.wait(5000)
        super().closeEvent(event)

    def cancelar_configuracion(self):
        self.configuracion_interface.cargar_datos()
        self.switchTo(self.inicio_interface)

    def guardar_configuracion(self):
        datos = self.configuracion_interface.obtener_datos()
        if not all(datos[campo] for campo in (
            "nombre", "usuario", "correo", "nombre_consultorio",
            "telefono_consultorio", "correo_consultorio",
        )):
            QMessageBox.warning(self, "Datos incompletos", "Completa todos los datos del perfil y del consultorio.")
            return
        for etiqueta, correo in (("nutriólogo", datos["correo"]),
                                 ("consultorio", datos["correo_consultorio"])):
            if "@" not in correo or "." not in correo.split("@")[-1]:
                QMessageBox.warning(self, "Correo no válido", f"Revisa el correo del {etiqueta}.")
                return
        if len(datos["usuario"]) < 3:
            QMessageBox.warning(self, "Usuario no válido", "El usuario debe tener al menos 3 caracteres.")
            return
        try:
            if not sesion_nutriologo.actualizar_perfil(datos):
                QMessageBox.warning(self, "Configuración", "No se encontró la cuenta que se está editando.")
                return
        except ValueError as error:
            QMessageBox.warning(self, "Datos duplicados", str(error))
            return
        except Exception as error:
            QMessageBox.critical(self, "Error al guardar", f"No se pudo actualizar PostgreSQL:\n{error}")
            return
        QMessageBox.information(self, "Configuración", "Los datos se actualizaron en PostgreSQL.")
        self.switchTo(self.inicio_interface)

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
        try:
            if self.agregar_paciente_interface.paciente_id:
                paciente_id = self.agregar_paciente_interface.paciente_id
                repositorio.actualizar_paciente(paciente_id, datos)
                self.actualizar_contexto_paciente(paciente_id)
            else:
                repositorio.crear_paciente(datos)
        except ValueError as error:
            QMessageBox.warning(self, "Datos no válidos", str(error))
            return
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
            self.calendario_interface.actualizar_marcadores()
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
            self._altura_medicion_actual = None
            self.switchTo(self.nueva_medicion_interface)

    def continuar_a_medicion(self):
        altura = self.nueva_medicion_interface.obtener_altura()
        if altura is None:
            return
        self._altura_medicion_actual = altura
        self.switchTo(self.medicion_interface)

    def iniciar_lectura_bascula(self):
        if self._lector_bascula and self._lector_bascula.isRunning():
            return
        if self._altura_medicion_actual is None:
            self.medicion_interface.mostrar_estado(
                "Error en la medición: captura primero la estatura del paciente."
            )
            return

        self._ble_error = False
        self._ble_confirmacion_pendiente = False
        self._ble_lector_finalizado = False
        self.medicion_interface.btn_iniciar.setEnabled(False)
        self.medicion_interface.mostrar_estado("Buscando báscula...")

        lector = LectorRTC2017(self)
        self._lector_bascula = lector
        lector.estado.connect(self.medicion_interface.mostrar_estado)
        lector.lectura_estable.connect(self.confirmar_lectura_bascula)
        lector.error_lectura.connect(self.error_lectura_bascula)
        lector.cancelado.connect(self.escaneo_cancelado)
        lector.finished.connect(lambda lector=lector: self.finalizar_escaneo_bascula(lector))
        lector.start()

    def error_lectura_bascula(self, mensaje):
        self._ble_error = True
        self.medicion_interface.mostrar_estado(f"Error en la medición: {mensaje}")

    def escaneo_cancelado(self):
        self.medicion_interface.mostrar_estado("Medición cancelada. Puedes volver a iniciar.")

    def finalizar_escaneo_bascula(self, lector):
        if lector is not self._lector_bascula:
            lector.deleteLater()
            return
        self._ble_lector_finalizado = True
        self._lector_bascula = None
        lector.deleteLater()
        if not self._ble_confirmacion_pendiente:
            self.medicion_interface.btn_iniciar.setEnabled(True)
            if not self._ble_error and self.medicion_interface.lbl_estado.text().endswith("Buscando báscula..."):
                self.medicion_interface.mostrar_estado("No se recibió una lectura. Intenta de nuevo.")

    def confirmar_lectura_bascula(self, lectura):
        self._ble_confirmacion_pendiente = True
        peso = lectura.peso_kg
        respuesta = QMessageBox.question(
            self,
            "Confirmar peso",
            f"La báscula reportó {peso:.2f} kg. ¿Confirmas esta lectura para guardar la medición?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        self._ble_confirmacion_pendiente = False
        if respuesta != QMessageBox.Yes:
            self.medicion_interface.mostrar_estado("Lectura descartada. Puedes iniciar otra medición.")
            if self._ble_lector_finalizado:
                self.medicion_interface.btn_iniciar.setEnabled(True)
            return
        self.guardar_medicion(peso)

    def guardar_medicion(self, peso):
        objetivo = next((b.text() for b in self.nueva_medicion_interface.grupo_objetivo.buttons() if b.isChecked()), "")
        actividad = next((b.text() for b in self.nueva_medicion_interface.grupo_actividad.buttons() if b.isChecked()), "")
        motivo = self.nueva_medicion_interface.input_motivo.text().strip()
        fecha_medicion = self.nueva_medicion_interface.fecha.date.toString("dd/MM/yyyy")
        datos = self.medicion_interface.obtener_datos(
            fecha_medicion,
            objetivo, actividad, motivo, peso, self._altura_medicion_actual)
        if not datos:
            self.medicion_interface.btn_iniciar.setEnabled(True)
            return
        paciente = repositorio.obtener_paciente(self.ficha_paciente_interface.paciente_id)
        edad = calcular_edad(
            paciente.get("fecha_nacimiento") if paciente else None,
            fecha_medicion,
        )
        estimaciones = estimar_composicion_corporal(
            peso_kg=datos["peso"],
            altura_cm=datos["altura_cm"],
            imc=datos["imc"],
            edad=edad,
            sexo=paciente.get("sexo") if paciente else None,
        )
        # El servicio usa nombres explícitos de fórmula; el repositorio recibe
        # los alias del modelo de medición.
        datos["grasa"] = estimaciones["grasa_pct"]
        datos["agua"] = estimaciones["agua_pct"]
        datos["agua_litros"] = estimaciones["agua_litros"]
        try:
            medicion = repositorio.crear_medicion(self.ficha_paciente_interface.paciente_id, datos)
        except Exception as error:
            QMessageBox.critical(self, "No se pudo guardar", f"La lectura fue válida, pero no se guardó la medición.\n\n{error}")
            self.medicion_interface.mostrar_estado("Error al guardar. Puedes volver a iniciar la medición.")
            self.medicion_interface.btn_iniciar.setEnabled(True)
            return
        self.ficha_paciente_interface.actualizar_mediciones()
        self.buscar_pacientes_interface.actualizar_lista()
        self.inicio_interface.actualizar()
        resultado = self.resultado_medicion_interface
        resultado.lbl_paciente.setText(self.medicion_interface.lbl_paciente.text())
        resultado.lbl_fecha.setText(medicion["fecha"])
        resultado.lbl_objetivo.setText(f"Objetivo: {medicion['objetivo'] or '—'}")
        resultado.lbl_motivo.setText(f"Motivo: {medicion['motivo'] or '—'}")
        resultado.lbl_actividad.setText(f"Actividad física: {medicion['actividad'] or '—'}")
        peso_grasa = medicion.get("grasa")
        agua_litros = medicion.get("agua_litros")
        agua_pct = medicion.get("agua")
        resultado.valores["Peso:"].setText(f"{medicion['peso']:.2f} kg")
        resultado.valores["IMC:"].setText(f"{medicion['imc']:.1f}")
        resultado.valores["Grasa estimada:"].setText(
            f"{peso_grasa:.1f} %" if peso_grasa is not None else "No disponible"
        )
        if agua_litros is not None and agua_pct is not None:
            resultado.valores["Agua corporal estimada:"].setText(
                f"{agua_litros:.1f} L · {agua_pct:.1f} %"
            )
        else:
            resultado.valores["Agua corporal estimada:"].setText("No disponible")
        notas = [
            "Estimaciones antropométricas Deurenberg/Watson; no son lecturas directas de la báscula. "
            "Deurenberg: edades 7–83 e IMC 13.9–40.9; Watson: adultos."
        ]
        if peso_grasa is None:
            notas.append("Grasa: requiere edad/sexo compatibles y un IMC dentro del rango de la ecuación.")
        if agua_litros is None:
            notas.append("Agua (Watson): disponible para adultos con sexo Masculino o Femenino.")
        resultado.lbl_nota_estimaciones.setText(" ".join(notas))
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

        edad = calcular_edad(paciente.get("fecha_nacimiento"))
        if edad is None:
            self.objetivos_interface.limpiar_sugerencia_calorias(
                "Registra una fecha de nacimiento válida en la ficha para calcular la sugerencia. Puedes capturar las calorías manualmente.")
            return
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
        if self.nueva_cita_interface.cita_id:
            fecha = self._fecha_citas_edicion_origen or self._fecha_citas_actual
            self.nueva_cita_interface.limpiar()
            self.proximas_citas_interface.actualizar(fecha)
            self._fecha_citas_actual = fecha
            self.switchTo(self.proximas_citas_interface)
            return
        self.nueva_cita_interface.limpiar()
        self.switchTo(self.calendario_interface)

    def abrir_citas_fecha(self, fecha):
        fecha_iso = fecha.toString("yyyy-MM-dd")
        if not repositorio.listar_citas(fecha_iso):
            return
        self._fecha_citas_actual = fecha_iso
        self.proximas_citas_interface.actualizar(fecha_iso)
        self.switchTo(self.proximas_citas_interface)

    def abrir_editar_cita(self, cita_id):
        cita = repositorio.obtener_cita(cita_id)
        if not cita:
            QMessageBox.warning(self, "Cita no encontrada", "La cita ya no existe o fue eliminada.")
            self.calendario_interface.actualizar_marcadores()
            self.proximas_citas_interface.actualizar(self._fecha_citas_actual)
            self.switchTo(self.proximas_citas_interface)
            return
        self._fecha_citas_edicion_origen = cita["fecha"]
        self._fecha_citas_actual = cita["fecha"]
        self.nueva_cita_interface.cargar_cita(cita)
        self.switchTo(self.nueva_cita_interface)

    def guardar_cita(self):
        datos = self.nueva_cita_interface.obtener_datos()
        if not datos:
            return
        try:
            cita_id = self.nueva_cita_interface.cita_id
            if cita_id:
                repositorio.actualizar_cita(cita_id, datos)
            else:
                repositorio.crear_cita(datos)
        except ValueError as error:
            QMessageBox.warning(self, "Horario no disponible", str(error))
            return
        self.calendario_interface.actualizar_marcadores()
        self._fecha_citas_actual = datos["fecha"]
        self.proximas_citas_interface.actualizar(datos["fecha"])
        self.inicio_interface.actualizar()
        self.nueva_cita_interface.limpiar()
        self.switchTo(self.proximas_citas_interface)

    def eliminar_cita(self):
        cita_id = self.nueva_cita_interface.cita_id
        cita = repositorio.obtener_cita(cita_id) if cita_id else None
        if not cita:
            QMessageBox.warning(self, "Cita no encontrada", "La cita ya no existe o fue eliminada.")
            self.nueva_cita_interface.limpiar()
            self.calendario_interface.actualizar_marcadores()
            self.proximas_citas_interface.actualizar(self._fecha_citas_actual)
            self.switchTo(self.proximas_citas_interface)
            return
        respuesta = QMessageBox.question(
            self,
            "Eliminar cita",
            f"¿Eliminar la cita de {cita['paciente']} del {datetime.strptime(cita['fecha'], '%Y-%m-%d').strftime('%d/%m/%Y')} a las {cita['hora']}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if respuesta != QMessageBox.Yes:
            return
        fecha = cita["fecha"]
        repositorio.eliminar_cita(cita_id)
        self.nueva_cita_interface.limpiar()
        self.calendario_interface.actualizar_marcadores()
        self.proximas_citas_interface.actualizar(fecha)
        self._fecha_citas_actual = fecha
        self.inicio_interface.actualizar()
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
