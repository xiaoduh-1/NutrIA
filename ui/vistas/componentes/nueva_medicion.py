from PySide6.QtCore import QDate
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QButtonGroup
from qfluentwidgets import (StrongBodyLabel, SubtitleLabel, CalendarPicker, RadioButton,LineEdit, PrimaryPushButton)


class NuevaMedicionInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("nuevaMedicionInterface")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(12)

        self.lbl_paciente = StrongBodyLabel("Paciente: Juan Pérez")
        layout.addWidget(self.lbl_paciente)

        #Fecha de medicion
        self.fecha = CalendarPicker()
        self.fecha.setDate(QDate.currentDate())
        layout.addWidget(self.fecha)

        #Columnas objetivo y actividad física
        columnas = QHBoxLayout()
        columnas.setSpacing(60)

        #Objetivo de la consulta
        col_objetivo = QVBoxLayout()
        col_objetivo.setSpacing(8)
        col_objetivo.addWidget(SubtitleLabel("Objetivo de la consulta:"))

        self.grupo_objetivo = QButtonGroup(self)
        for texto in ["Pérdida de peso", "Ganancia muscular", "Mantenimiento", "Otro"]:
            radio = RadioButton(texto)
            self.grupo_objetivo.addButton(radio)
            col_objetivo.addWidget(radio)

        self.input_motivo = LineEdit()
        self.input_motivo.setPlaceholderText("Indicar motivo...")
        col_objetivo.addWidget(self.input_motivo)
        col_objetivo.addStretch()

        #Nivel de actividad fisica
        col_actividad = QVBoxLayout()
        col_actividad.setSpacing(8)
        col_actividad.addWidget(SubtitleLabel("Nivel de actividad física:"))

        self.grupo_actividad = QButtonGroup(self)
        for texto in ["Sedentario", "Ligeramente activo", "Moderadamente activo",
                      "Muy activo", "Extra activo"]:
            radio = RadioButton(texto)
            self.grupo_actividad.addButton(radio)
            col_actividad.addWidget(radio)
        col_actividad.addStretch()

        columnas.addLayout(col_objetivo)
        columnas.addLayout(col_actividad)
        columnas.addStretch()
        layout.addLayout(columnas)

        layout.addStretch()

        #Boton
        inferior = QHBoxLayout()
        inferior.addStretch()
        self.btn_siguiente = PrimaryPushButton("Siguiente")
        inferior.addWidget(self.btn_siguiente)
        layout.addLayout(inferior)