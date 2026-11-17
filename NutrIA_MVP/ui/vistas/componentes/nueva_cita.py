from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QDateEdit,
    QCompleter,
)
from PySide6.QtCore import QDate, Qt, QStringListModel
from qfluentwidgets import TitleLabel, LineEdit, PushButton, PrimaryPushButton, FluentIcon
from datos import repositorio

class NuevaCitaInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("nuevaCitaInterface")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(12)

        self.lbl_titulo = TitleLabel("Nueva cita")
        layout.addWidget(self.lbl_titulo)

        self.input_paciente = LineEdit()
        self.input_paciente.setPlaceholderText("Busca por nombre o apellido")
        layout.addWidget(self.input_paciente)
        self._pacientes_por_opcion = {}
        self._paciente_id_seleccionado = None
        self._modelo_pacientes = QStringListModel(self)
        self._completador_pacientes = QCompleter(self._modelo_pacientes, self)
        self._completador_pacientes.setCaseSensitivity(Qt.CaseInsensitive)
        self._completador_pacientes.setFilterMode(Qt.MatchContains)
        self._completador_pacientes.setCompletionMode(QCompleter.PopupCompletion)
        self.input_paciente.setCompleter(self._completador_pacientes)
        self.input_paciente.textEdited.connect(self._limpiar_seleccion_paciente)
        self._completador_pacientes.activated[str].connect(self._seleccionar_paciente)
        self._cargar_pacientes()

        self.input_hora = LineEdit()
        self.input_hora.setPlaceholderText("Hora (ej. 10:00)")
        layout.addWidget(self.input_hora)

        self.fecha = QDateEdit()
        self.fecha.setCalendarPopup(True)
        self.fecha.setDisplayFormat("dd/MM/yyyy")
        self.fecha.setDate(QDate.currentDate())
        layout.addWidget(self.fecha)

        layout.addStretch()

        #Botones
        botones = QHBoxLayout()
        botones.addStretch()
        self.btn_cancelar = PushButton("Cancelar")
        self.btn_guardar = PrimaryPushButton(FluentIcon.SAVE, "Guardar")
        self.btn_eliminar = PushButton("Eliminar cita")
        self.btn_eliminar.hide()
        botones.addWidget(self.btn_eliminar)
        botones.addWidget(self.btn_cancelar)
        botones.addWidget(self.btn_guardar)
        layout.addLayout(botones)
        self.cita_id = None

    def cargar_cita(self, cita):
        self.lbl_titulo.setText("Editar cita")
        self.cita_id = cita["id"]
        self.input_paciente.setText(cita["paciente"])
        self.input_paciente.setReadOnly(True)
        self._paciente_id_seleccionado = cita["paciente_id"]
        self.input_hora.setText(cita["hora"])
        self.fecha.setDate(QDate.fromString(cita["fecha"], "yyyy-MM-dd"))
        self.btn_guardar.setText("Guardar cambios")
        self.btn_eliminar.show()

    def limpiar(self):
        self.lbl_titulo.setText("Nueva cita")
        self.cita_id = None
        self.input_paciente.clear()
        self.input_paciente.setReadOnly(False)
        self._paciente_id_seleccionado = None
        self._cargar_pacientes()
        self.input_hora.clear()
        self.fecha.setDate(QDate.currentDate())
        self.btn_guardar.setText("Guardar")
        self.btn_eliminar.hide()

    def _cargar_pacientes(self):
        pacientes = repositorio.listar_pacientes()
        self._pacientes_por_opcion = {}
        opciones = []
        for paciente in pacientes:
            nombre = f"{paciente['nombre']} {paciente['apellido']}"
            telefono = paciente.get("telefono", "")
            etiqueta_contacto = telefono or paciente["id"][-6:]
            opcion = f"{nombre} · {etiqueta_contacto}" if telefono else nombre
            if opcion in self._pacientes_por_opcion:
                opcion = f"{nombre} · {etiqueta_contacto} · {paciente['id'][-6:]}"
            self._pacientes_por_opcion[opcion] = paciente
            opciones.append(opcion)
        self._modelo_pacientes.setStringList(opciones)

    def _limpiar_seleccion_paciente(self, _texto):
        self._paciente_id_seleccionado = None

    def _seleccionar_paciente(self, opcion):
        paciente = self._pacientes_por_opcion.get(opcion)
        if not paciente:
            return
        self._paciente_id_seleccionado = paciente["id"]
        self.input_paciente.setText(f"{paciente['nombre']} {paciente['apellido']}")

    def obtener_datos(self):
        nombre = self.input_paciente.text().strip()
        hora = self.input_hora.text().strip()
        if self.cita_id:
            cita_actual = repositorio.obtener_cita(self.cita_id)
            paciente = repositorio.obtener_paciente(cita_actual["paciente_id"]) if cita_actual else None
        else:
            paciente = repositorio.obtener_paciente(self._paciente_id_seleccionado)
            if paciente and nombre.casefold() != f"{paciente['nombre']} {paciente['apellido']}".casefold():
                paciente = None
        if not paciente:
            QMessageBox.warning(
                self,
                "Selecciona un paciente",
                "Escribe una parte del nombre o apellido y selecciona al paciente en las sugerencias.",
            )
            return None
        if len(hora) != 5 or hora[2] != ":" or not hora[:2].isdigit() or not hora[3:].isdigit() or int(hora[:2]) > 23 or int(hora[3:]) > 59:
            QMessageBox.warning(self, "Hora no válida", "Usa el formato de 24 horas, por ejemplo 10:00.")
            return None
        fecha = self.fecha.date().toString("yyyy-MM-dd")
        conflicto = repositorio.buscar_conflicto_cita(fecha, hora, excluir_id=self.cita_id)
        if conflicto:
            QMessageBox.warning(
                self,
                "Horario no disponible",
                f"Debe haber al menos 30 minutos entre citas. Ya existe una cita a las {conflicto['hora']}.",
            )
            return None
        return {"paciente": nombre, "paciente_id": paciente["id"],
                "fecha": fecha, "hora": hora}
