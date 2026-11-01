from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QButtonGroup,
    QInputDialog, QScrollArea, QFrame,
)
from qfluentwidgets import (
    StrongBodyLabel, TitleLabel, SubtitleLabel, BodyLabel, LineEdit, TextEdit,
    RadioButton, ToolButton, PushButton, PrimaryPushButton,
    HorizontalSeparator, FluentIcon,
)


class ObjetivosNutricionalesInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("objetivosNutricionalesInterface")
        self.macronutrientes = {"Proteínas": None, "Carbohidratos": None, "Grasa": None}
        self.etiquetas_macros = {}
        self.botones_editar_macro = {}

        pagina = QVBoxLayout(self)
        pagina.setContentsMargins(16, 12, 16, 12)
        pagina.setSpacing(8)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        contenido = QWidget()
        layout = QVBoxLayout(contenido)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)
        scroll.setWidget(contenido)
        pagina.addWidget(scroll, 1)

        self.lbl_paciente = StrongBodyLabel("Paciente: —")
        layout.addWidget(self.lbl_paciente)
        layout.addWidget(TitleLabel("Objetivos nutricionales"), alignment=Qt.AlignHCenter)

        # En una columna para permitir que el contenido se adapte a ventanas estrechas.
        col_cal = QVBoxLayout()
        col_cal.addWidget(SubtitleLabel("Calorías objetivo (kcal/día):"))
        self.input_calorias = LineEdit()
        col_cal.addWidget(self.input_calorias)
        self.lbl_sugerencia_calorias = BodyLabel(
            "La sugerencia aparecerá al continuar desde el resultado de medición.")
        self.lbl_sugerencia_calorias.setWordWrap(True)
        col_cal.addWidget(self.lbl_sugerencia_calorias)
        layout.addLayout(col_cal)

        macros = QGridLayout()
        macros.setHorizontalSpacing(12)
        macros.setVerticalSpacing(8)
        macros.addWidget(SubtitleLabel("Macronutrientes (gramos):"), 0, 0, 1, 3)
        for fila, nombre in enumerate(self.macronutrientes, start=1):
            macros.addWidget(BodyLabel(f"{nombre}:"), fila, 0)
            valor = BodyLabel("— g")
            self.etiquetas_macros[nombre] = valor
            macros.addWidget(valor, fila, 1)
            boton = ToolButton(FluentIcon.EDIT)
            boton.setToolTip(f"Editar gramos de {nombre.lower()}")
            boton.clicked.connect(
                lambda _=False, macro=nombre: self.editar_macronutriente(macro))
            self.botones_editar_macro[nombre] = boton
            macros.addWidget(boton, fila, 2, alignment=Qt.AlignRight)
        macros.setColumnStretch(1, 1)
        layout.addLayout(macros)

        layout.addWidget(HorizontalSeparator())
        layout.addWidget(TitleLabel("Preferencias alimentarias"), alignment=Qt.AlignHCenter)

        preferencias = QVBoxLayout()
        preferencias.addWidget(SubtitleLabel("Preferencia:"))
        self.grupo_pref = QButtonGroup(self)
        for texto in ["Alta en proteínas", "Vegetariana", "Baja en carbohidratos"]:
            radio = RadioButton(texto)
            self.grupo_pref.addButton(radio)
            preferencias.addWidget(radio)
        layout.addLayout(preferencias)

        layout.addWidget(SubtitleLabel("Alergias:"))
        self.input_alergias = TextEdit()
        self.input_alergias.setMinimumHeight(80)
        layout.addWidget(self.input_alergias)

        layout.addWidget(HorizontalSeparator())
        layout.addWidget(SubtitleLabel("Alimentos para evitar:"))
        self.input_evitar = TextEdit()
        self.input_evitar.setMinimumHeight(70)
        layout.addWidget(self.input_evitar)

        botones = QHBoxLayout()
        self.btn_atras = PushButton(FluentIcon.LEFT_ARROW, "Atrás")
        self.btn_continuar = PrimaryPushButton("Continuar")
        botones.addWidget(self.btn_atras)
        botones.addStretch()
        botones.addWidget(self.btn_continuar)
        pagina.addLayout(botones)

    def editar_macronutriente(self, nombre):
        actual = self.macronutrientes[nombre]
        valor, aceptado = QInputDialog.getDouble(
            self,
            f"Gramos de {nombre.lower()}",
            f"Ingresa los gramos de {nombre.lower()}:",
            float(actual or 0),
            0,
            1000,
            1,
        )
        if aceptado:
            self.macronutrientes[nombre] = valor
            self.etiquetas_macros[nombre].setText(f"{valor:g} g")

    def obtener_datos(self):
        preferencia = next((b.text() for b in self.grupo_pref.buttons() if b.isChecked()), "Sin preferencia")
        return {
            "calorias": self.input_calorias.text().strip(),
            "macronutrientes": dict(self.macronutrientes),
            "preferencia": preferencia,
            "alergias": self.input_alergias.toPlainText().strip(),
            "evitar": self.input_evitar.toPlainText().strip(),
        }

    def mostrar_sugerencia_calorias(self, objetivo, mantenimiento, tmb):
        self.input_calorias.setText(str(objetivo))
        self.lbl_sugerencia_calorias.setText(
            f"Sugerencia: {objetivo} kcal/día. Mantenimiento: {mantenimiento} kcal/día "
            f"(TMB: {tmb} kcal/día). Puedes ajustar el valor.")

    def limpiar_sugerencia_calorias(self, mensaje):
        self.lbl_sugerencia_calorias.setText(mensaje)

    def cargar_paciente(self, nombre, objetivos):
        self.lbl_paciente.setText(f"Paciente: {nombre}")
        self.input_calorias.setText(objetivos.get("calorias", ""))
        self.input_alergias.setPlainText(objetivos.get("alergias", ""))
        self.input_evitar.setPlainText(objetivos.get("evitar", ""))
        preferencia = objetivos.get("preferencia", "")
        for boton in self.grupo_pref.buttons():
            boton.setChecked(boton.text() == preferencia)
        macros_guardados = objetivos.get("macronutrientes", {})
        for macro, etiqueta in self.etiquetas_macros.items():
            valor = macros_guardados.get(macro)
            self.macronutrientes[macro] = valor
            etiqueta.setText(f"{float(valor):g} g" if valor is not None else "— g")
