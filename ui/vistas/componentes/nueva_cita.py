from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import TitleLabel, LineEdit, PushButton, PrimaryPushButton, FluentIcon

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

        layout.addStretch()

        #Botones
        botones = QHBoxLayout()
        botones.addStretch()
        self.btn_cancelar = PushButton("Cancelar")
        self.btn_guardar = PrimaryPushButton(FluentIcon.SAVE, "Guardar")
        botones.addWidget(self.btn_cancelar)
        botones.addWidget(self.btn_guardar)
        layout.addLayout(botones)