from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout
from qfluentwidgets import (StrongBodyLabel, TitleLabel, BodyLabel, CaptionLabel, LineEdit,PushButton, PrimaryPushButton, FluentIcon)


class MedicionInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("medicionInterface")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(12)

        self.lbl_paciente = StrongBodyLabel("Paciente: Juan Pérez")
        layout.addWidget(self.lbl_paciente)

        layout.addWidget(TitleLabel("Medición Corporal"), alignment=Qt.AlignHCenter)

        #Boton iniciar medicion + estado de conexion
        conexion = QHBoxLayout()
        conexion.addStretch()
        self.btn_iniciar = PrimaryPushButton(FluentIcon.PLAY, "Iniciar medición")
        self.btn_iniciar.setFixedHeight(50)
        conexion.addWidget(self.btn_iniciar)
        self.lbl_estado = BodyLabel("Estado: Desconectado")
        conexion.addWidget(self.lbl_estado)
        conexion.addStretch()
        layout.addLayout(conexion)

        #Columnas de medicion
        grid = QGridLayout()
        grid.setHorizontalSpacing(40)
        grid.setVerticalSpacing(8)

        self.input_peso = LineEdit()
        self.input_grasa = LineEdit()
        self.input_masa_muscular = LineEdit()
        self.input_agua = LineEdit()

        grid.addWidget(BodyLabel("Peso:"), 0, 0)
        grid.addWidget(BodyLabel("Grasa corporal:"), 0, 1)
        grid.addWidget(self.input_peso, 1, 0)
        grid.addWidget(self.input_grasa, 1, 1)
        grid.addWidget(BodyLabel("Masa muscular:"), 2, 0)
        grid.addWidget(BodyLabel("Agua corporal:"), 2, 1)
        grid.addWidget(self.input_masa_muscular, 3, 0)
        grid.addWidget(self.input_agua, 3, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        layout.addLayout(grid)

        layout.addWidget(CaptionLabel(),
            alignment=Qt.AlignHCenter)

        layout.addStretch()

        #Botones
        botones = QHBoxLayout()
        self.btn_atras = PushButton(FluentIcon.LEFT_ARROW, "Atrás")
        self.btn_guardar = PrimaryPushButton(FluentIcon.SAVE, "Guardar y seguir")
        botones.addWidget(self.btn_atras)
        botones.addStretch()
        botones.addWidget(self.btn_guardar)
        layout.addLayout(botones)