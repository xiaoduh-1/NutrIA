from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (TitleLabel, SubtitleLabel, StrongBodyLabel, BodyLabel, CardWidget,PushButton, PrimaryPushButton, FluentIcon)


class VistaPreviaInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("vistaPreviaInterface")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(10)

        #Reporte
        hoja = CardWidget()
        hoja_layout = QVBoxLayout(hoja)
        hoja_layout.setContentsMargins(24, 16, 24, 16)
        hoja_layout.setSpacing(8)

        hoja_layout.addWidget(TitleLabel("NutrIA"), alignment=Qt.AlignHCenter)
        hoja_layout.addWidget(SubtitleLabel("Reporte nutricional"), alignment=Qt.AlignHCenter)

        datos = QHBoxLayout()
        izq = QVBoxLayout()
        izq.addWidget(BodyLabel("Paciente: Juan Pérez"))
        izq.addWidget(BodyLabel("Fecha: 10/10/2026"))
        izq.addStretch()

        der = QVBoxLayout()
        der.addWidget(StrongBodyLabel("Resultado de la medición:"))
        der.addWidget(BodyLabel("Peso: 80 kg"))
        der.addWidget(BodyLabel("Grasa: 20%"))
        der.addSpacing(8)
        der.addWidget(StrongBodyLabel("Objetivos nutricionales:"))
        der.addWidget(BodyLabel("2,300 kcal"))

        datos.addLayout(izq, 1)
        datos.addLayout(der, 1)
        hoja_layout.addLayout(datos)

        hoja_layout.addWidget(StrongBodyLabel("Menu semanal"))
        self.lbl_menu = BodyLabel("(Aquí se mostrará el menu semanal)")
        hoja_layout.addWidget(self.lbl_menu)
        hoja_layout.addStretch()

        layout.addWidget(hoja, 1)

        #Botones
        botones = QHBoxLayout()
        self.btn_regresar = PushButton(FluentIcon.LEFT_ARROW, "Regresar")
        self.btn_exportar = PrimaryPushButton(FluentIcon.SAVE, "Exportar PDF")
        botones.addWidget(self.btn_regresar)
        botones.addStretch()
        botones.addWidget(self.btn_exportar)
        layout.addLayout(botones)