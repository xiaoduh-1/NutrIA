from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (TitleLabel, SubtitleLabel, BodyLabel, StrongBodyLabel, CardWidget,PushButton, HyperlinkButton, FluentIcon)


class InicioInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("inicioInterface")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(14)

        #Saludo
        self.lbl_saludo = TitleLabel("Buen día, Nutri, ¿Qué vamos a hacer hoy?")
        layout.addWidget(self.lbl_saludo)

        #Botones de acceso rapido
        accesos = QHBoxLayout()
        accesos.setSpacing(20)
        self.btn_paciente = PushButton(FluentIcon.ADD, "Paciente")
        self.btn_medicion = PushButton(FluentIcon.HEART, "Medición")
        self.btn_cita = PushButton(FluentIcon.CALENDAR, "Cita")
        for btn in (self.btn_paciente, self.btn_medicion, self.btn_cita):
            btn.setFixedHeight(50)
            accesos.addWidget(btn, 1)
        layout.addLayout(accesos)

        #Citas
        layout.addWidget(SubtitleLabel("Citas de hoy"))
        tarjeta_citas = CardWidget()
        citas_layout = QVBoxLayout(tarjeta_citas)
        citas_layout.setContentsMargins(20, 14, 20, 14)
        citas_layout.setSpacing(6)

        citas = ["Juan Pérez", "Juan Pérez", "Juan Pérez"]
        self.botones_ver_cita = []
        for paciente in citas:
            fila = QHBoxLayout()
            fila.addWidget(BodyLabel(paciente))
            fila.addStretch()
            btn_ver = HyperlinkButton("", "Ver")
            fila.addWidget(btn_ver)
            citas_layout.addLayout(fila)
            self.botones_ver_cita.append(btn_ver)
        layout.addWidget(tarjeta_citas)

        #Resumen
        layout.addWidget(SubtitleLabel("Resumen de hoy"))
        tarjeta_resumen = CardWidget()
        resumen_layout = QHBoxLayout(tarjeta_resumen)
        resumen_layout.setContentsMargins(20, 18, 20, 18)

        self.valores = {}
        for titulo, valor in [("Pacientes", "100"), ("Citas", "100"), ("Mediciones", "100")]:
            columna = QVBoxLayout()
            columna.setSpacing(4)
            columna.addWidget(BodyLabel(titulo), alignment=Qt.AlignHCenter)
            lbl_valor = StrongBodyLabel(valor)
            columna.addWidget(lbl_valor, alignment=Qt.AlignHCenter)
            resumen_layout.addLayout(columna, 1)
            self.valores[titulo] = lbl_valor
        layout.addWidget(tarjeta_resumen)

        layout.addStretch()