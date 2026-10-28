from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (TitleLabel, BodyLabel, StrongBodyLabel, SearchLineEdit, CardWidget,PushButton, PrimaryPushButton, HyperlinkButton, FluentIcon)


class PacienteCard(CardWidget):
    def __init__(self, nombre, ultima_medicion, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)

        textos = QVBoxLayout()
        textos.setSpacing(2)
        textos.addWidget(StrongBodyLabel(nombre))
        textos.addWidget(BodyLabel(f"Última medición: {ultima_medicion}"))
        layout.addLayout(textos)

        layout.addStretch()
        self.btn_ver = HyperlinkButton("", "Ver >")
        layout.addWidget(self.btn_ver)


class buscarPacientes(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("buscarPacientesInterface")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(12)

        #titulo + boton agregar
        encabezado = QHBoxLayout()
        encabezado.addWidget(TitleLabel("Pacientes"))
        encabezado.addStretch()
        self.btn_agregar_paciente = PushButton(FluentIcon.ADD, "Agregar paciente")
        encabezado.addWidget(self.btn_agregar_paciente)
        layout.addLayout(encabezado)

        #Buscador
        self.input_buscar = SearchLineEdit()
        self.input_buscar.setPlaceholderText("Buscar paciente...")
        layout.addWidget(self.input_buscar)

        #Lista de pacientes
        pacientes = [
            ("Juan Pérez", "01/10/2026"),
            ("Omar Castillo", "04/09/2026"),
            ("Pedro Pascal", "08/08/2026"),
        ]
        self.tarjetas = []
        for nombre, fecha in pacientes:
            tarjeta = PacienteCard(nombre, fecha)
            self.tarjetas.append(tarjeta)
            layout.addWidget(tarjeta)

        layout.addStretch()

        #Boton inferior
        inferior = QHBoxLayout()
        inferior.addStretch()
        self.btn_seleccionar = PrimaryPushButton("Seleccionar")
        inferior.addWidget(self.btn_seleccionar)
        layout.addLayout(inferior)