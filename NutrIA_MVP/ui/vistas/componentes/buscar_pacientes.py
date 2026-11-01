from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Signal
from qfluentwidgets import (TitleLabel, BodyLabel, StrongBodyLabel, SearchLineEdit, CardWidget,PushButton, PrimaryPushButton, HyperlinkButton, FluentIcon)
from datos import repositorio


class PacienteCard(CardWidget):
    def __init__(self, paciente, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)

        textos = QVBoxLayout()
        textos.setSpacing(2)
        self.paciente_id = paciente["id"]
        textos.addWidget(StrongBodyLabel(f"{paciente['nombre']} {paciente['apellido']}"))
        mediciones = repositorio.listar_mediciones(self.paciente_id)
        fecha = mediciones[0]["fecha"] if mediciones else "Sin mediciones"
        textos.addWidget(BodyLabel(f"Última medición: {fecha}"))
        layout.addLayout(textos)

        layout.addStretch()
        self.btn_ver = HyperlinkButton("", "Ver >")
        layout.addWidget(self.btn_ver)


class buscarPacientes(QWidget):
    paciente_seleccionado = Signal(str)

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
        self.tarjetas = []
        self.paciente_id_seleccionado = None
        self.lista_layout = layout
        self.input_buscar.textChanged.connect(self.actualizar_lista)
        self.actualizar_lista()

        layout.addStretch()

        #Boton inferior
        inferior = QHBoxLayout()
        inferior.addStretch()
        self.btn_seleccionar = PrimaryPushButton("Seleccionar")
        inferior.addWidget(self.btn_seleccionar)
        layout.addLayout(inferior)

    def actualizar_lista(self, _texto=None):
        for tarjeta in self.tarjetas:
            self.layout().removeWidget(tarjeta)
            tarjeta.deleteLater()
        self.tarjetas.clear()
        for paciente in repositorio.listar_pacientes(self.input_buscar.text()):
            tarjeta = PacienteCard(paciente, self)
            tarjeta.btn_ver.clicked.connect(lambda _=False, pid=paciente["id"]: self.seleccionar_paciente(pid))
            self.tarjetas.append(tarjeta)
            self.lista_layout.insertWidget(2, tarjeta)

    def seleccionar_paciente(self, paciente_id):
        self.paciente_id_seleccionado = paciente_id
        self.paciente_seleccionado.emit(paciente_id)
