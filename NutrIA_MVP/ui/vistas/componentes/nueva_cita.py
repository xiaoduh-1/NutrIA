from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QDateEdit
from PySide6.QtCore import QDate
from qfluentwidgets import TitleLabel, LineEdit, PushButton, PrimaryPushButton, FluentIcon
from datos import repositorio

class NuevaCitaInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("nuevaCitaInterface")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(12)

        layout.addWidget(TitleLabel("Nueva cita"))

        self.input_paciente = LineEdit()
        self.input_paciente.setPlaceholderText("Nombre del paciente")
        layout.addWidget(self.input_paciente)

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
        botones.addWidget(self.btn_cancelar)
        botones.addWidget(self.btn_guardar)
        layout.addLayout(botones)

    def limpiar(self):
        self.input_paciente.clear()
        self.input_hora.clear()
        self.fecha.setDate(QDate.currentDate())

    def obtener_datos(self):
        nombre = self.input_paciente.text().strip()
        hora = self.input_hora.text().strip()
        paciente = next((p for p in repositorio.listar_pacientes()
                         if f"{p['nombre']} {p['apellido']}".casefold() == nombre.casefold()), None)
        if not paciente:
            QMessageBox.warning(self, "Paciente no encontrado", "Escribe el nombre completo de un paciente registrado.")
            return None
        if len(hora) != 5 or hora[2] != ":" or not hora[:2].isdigit() or not hora[3:].isdigit() or int(hora[:2]) > 23 or int(hora[3:]) > 59:
            QMessageBox.warning(self, "Hora no válida", "Usa el formato de 24 horas, por ejemplo 10:00.")
            return None
        fecha = self.fecha.date().toString("yyyy-MM-dd")
        conflicto = repositorio.buscar_conflicto_cita(fecha, hora)
        if conflicto:
            QMessageBox.warning(
                self,
                "Horario no disponible",
                f"Debe haber al menos 30 minutos entre citas. Ya existe una cita a las {conflicto['hora']}.",
            )
            return None
        return {"paciente": nombre, "paciente_id": paciente["id"],
                "fecha": fecha, "hora": hora}
