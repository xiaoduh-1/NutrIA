from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QButtonGroup
from PySide6.QtCore import Qt
from qfluentwidgets import (StrongBodyLabel, TitleLabel, SubtitleLabel, BodyLabel, LineEdit, TextEdit,RadioButton, ToolButton,
                            PushButton, PrimaryPushButton,HorizontalSeparator, FluentIcon)


class ObjetivosNutricionalesInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("objetivosNutricionalesInterface")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(10)

        self.lbl_paciente = StrongBodyLabel("Paciente: Juan Pérez")
        layout.addWidget(self.lbl_paciente)
        layout.addWidget(TitleLabel("Objetivos nutricionales"), alignment=Qt.AlignHCenter)

        #Calorias
        fila = QHBoxLayout()
        fila.setSpacing(60)

        col_cal = QVBoxLayout()
        col_cal.addWidget(SubtitleLabel("Calorías objetivo:"))
        self.input_calorias = LineEdit()
        self.input_calorias.setFixedWidth(180)
        col_cal.addWidget(self.input_calorias)
        col_cal.addStretch()

        col_macros = QGridLayout()
        col_macros.setVerticalSpacing(8)
        col_macros.addWidget(SubtitleLabel("Macronutrientes:"), 0, 0, 1, 3)
        self.botones_editar_macro = {}
        for i, (nombre, valor) in enumerate(
                [("Proteínas:", "100 gr"), ("Carbohidratos:", "100 gr"), ("Grasa:", "50 gr")], start=1):
            col_macros.addWidget(BodyLabel(nombre), i, 0)
            col_macros.addWidget(BodyLabel(valor), i, 1)
            btn = ToolButton(FluentIcon.EDIT)
            col_macros.addWidget(btn, i, 2)
            self.botones_editar_macro[nombre] = btn

        fila.addLayout(col_cal)
        fila.addLayout(col_macros)
        fila.addStretch()
        layout.addLayout(fila)

        layout.addWidget(HorizontalSeparator())
        layout.addWidget(TitleLabel("Preferencias alimentarias"), alignment=Qt.AlignHCenter)

        #Preferencias
        fila2 = QHBoxLayout()
        fila2.setSpacing(60)

        col_pref = QVBoxLayout()
        col_pref.addWidget(SubtitleLabel("Macronutrientes:"))
        self.grupo_pref = QButtonGroup(self)
        for texto in ["Alta en proteínas", "Vegetariana", "Baja en carbohidratos"]:
            radio = RadioButton(texto)
            self.grupo_pref.addButton(radio)
            col_pref.addWidget(radio)
        col_pref.addStretch()

        col_alergias = QVBoxLayout()
        col_alergias.addWidget(SubtitleLabel("Alergias:"))
        self.input_alergias = TextEdit()
        self.input_alergias.setFixedHeight(90)
        col_alergias.addWidget(self.input_alergias)

        fila2.addLayout(col_pref, 1)
        fila2.addLayout(col_alergias, 1)
        layout.addLayout(fila2)

        layout.addWidget(HorizontalSeparator())

        layout.addWidget(SubtitleLabel("Alimentos para evitar:"))
        self.input_evitar = TextEdit()
        self.input_evitar.setFixedHeight(70)
        layout.addWidget(self.input_evitar)

        layout.addStretch()

        #Botones
        botones = QHBoxLayout()
        self.btn_atras = PushButton(FluentIcon.LEFT_ARROW, "Atrás")
        self.btn_continuar = PrimaryPushButton("Continuar")
        botones.addWidget(self.btn_atras)
        botones.addStretch()
        botones.addWidget(self.btn_continuar)
        layout.addLayout(botones)