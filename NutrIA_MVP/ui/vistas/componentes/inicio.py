from datetime import date

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (
    TitleLabel, SubtitleLabel, BodyLabel, StrongBodyLabel, CardWidget,
    PushButton, HyperlinkButton, FluentIcon,
)
from datos import repositorio


class InicioInterface(QWidget):
    paciente_seleccionado = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("inicioInterface")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(14)

        self.lbl_saludo = TitleLabel("Buen día, ¿qué vamos a hacer hoy?")
        layout.addWidget(self.lbl_saludo)

        accesos = QHBoxLayout()
        accesos.setSpacing(20)
        self.btn_paciente = PushButton(FluentIcon.ADD, "Paciente")
        self.btn_medicion = PushButton(FluentIcon.HEART, "Medición")
        self.btn_cita = PushButton(FluentIcon.CALENDAR, "Cita")
        for boton in (self.btn_paciente, self.btn_medicion, self.btn_cita):
            boton.setMinimumHeight(46)
            accesos.addWidget(boton, 1)
        layout.addLayout(accesos)

        layout.addWidget(SubtitleLabel("Citas de hoy"))
        tarjeta_citas = CardWidget()
        self.citas_layout = QVBoxLayout(tarjeta_citas)
        self.citas_layout.setContentsMargins(20, 14, 20, 14)
        self.citas_layout.setSpacing(6)
        self.botones_ver_cita = []
        layout.addWidget(tarjeta_citas)

        layout.addWidget(SubtitleLabel("Resumen de hoy"))
        tarjeta_resumen = CardWidget()
        resumen_layout = QHBoxLayout(tarjeta_resumen)
        resumen_layout.setContentsMargins(20, 18, 20, 18)
        self.valores = {}
        for titulo in ("Pacientes", "Citas", "Mediciones"):
            columna = QVBoxLayout()
            columna.setSpacing(4)
            columna.addWidget(BodyLabel(titulo), alignment=Qt.AlignHCenter)
            valor = StrongBodyLabel("0")
            columna.addWidget(valor, alignment=Qt.AlignHCenter)
            resumen_layout.addLayout(columna, 1)
            self.valores[titulo] = valor
        layout.addWidget(tarjeta_resumen)
        layout.addStretch()
        self.actualizar()

    def actualizar(self):
        while self.citas_layout.count():
            item = self.citas_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

        citas = repositorio.listar_citas()
        self.botones_ver_cita.clear()
        if not citas:
            self.citas_layout.addWidget(BodyLabel("No hay citas programadas para hoy."))
        for cita in citas:
            fila = QHBoxLayout()
            fila.addWidget(BodyLabel(f"{cita['hora']} — {cita['paciente']}"))
            fila.addStretch()
            boton = HyperlinkButton("", "Ver")
            boton.clicked.connect(
                lambda _=False, pid=cita.get("paciente_id"): self.paciente_seleccionado.emit(pid)
                if pid else None)
            fila.addWidget(boton)
            self.citas_layout.addLayout(fila)
            self.botones_ver_cita.append(boton)

        hoy = date.today().strftime("%d/%m/%Y")
        mediciones_hoy = sum(
            1 for grupo in repositorio.mediciones.values()
            for medicion in grupo if medicion.get("fecha") == hoy
        )
        self.valores["Pacientes"].setText(str(len(repositorio.listar_pacientes())))
        self.valores["Citas"].setText(str(len(citas)))
        self.valores["Mediciones"].setText(str(mediciones_hoy))
