from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QMessageBox
from qfluentwidgets import (StrongBodyLabel, TitleLabel, BodyLabel, CaptionLabel, LineEdit,PushButton, PrimaryPushButton, FluentIcon)


class MedicionInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("medicionInterface")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(12)

        self.lbl_paciente = StrongBodyLabel("Paciente: —")
        layout.addWidget(self.lbl_paciente)

        layout.addWidget(TitleLabel("Medición Corporal"), alignment=Qt.AlignHCenter)

        #Boton iniciar medicion + estado de conexion
        conexion = QHBoxLayout()
        conexion.addStretch()
        self.btn_iniciar = PrimaryPushButton(FluentIcon.PLAY, "Iniciar medición")
        self.btn_iniciar.setMinimumHeight(44)
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
        self.input_altura = LineEdit()
        self.input_calorias = LineEdit()

        grid.addWidget(BodyLabel("Peso:"), 0, 0)
        grid.addWidget(BodyLabel("Grasa corporal:"), 0, 1)
        grid.addWidget(self.input_peso, 1, 0)
        grid.addWidget(self.input_grasa, 1, 1)
        grid.addWidget(BodyLabel("Masa muscular:"), 2, 0)
        grid.addWidget(BodyLabel("Agua corporal:"), 2, 1)
        grid.addWidget(self.input_masa_muscular, 3, 0)
        grid.addWidget(self.input_agua, 3, 1)
        grid.addWidget(BodyLabel("Estatura (cm):"), 4, 0)
        grid.addWidget(BodyLabel("Calorías (kcal):"), 4, 1)
        grid.addWidget(self.input_altura, 5, 0)
        grid.addWidget(self.input_calorias, 5, 1)
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

    def obtener_datos(self, fecha, objetivo, actividad, motivo=""):
        datos = {"fecha": fecha, "objetivo": objetivo, "actividad": actividad, "motivo": motivo}
        for clave, campo, etiqueta in [
            ("peso", self.input_peso, "Peso"), ("grasa", self.input_grasa, "Grasa corporal"),
            ("masa_muscular", self.input_masa_muscular, "Masa muscular"), ("agua", self.input_agua, "Agua corporal"),
        ]:
            texto = campo.text().strip().replace(",", ".")
            if not texto:
                QMessageBox.warning(self, "Dato requerido", f"Captura {etiqueta.lower()}.")
                return None
            try:
                valor = float(texto)
                if valor <= 0:
                    raise ValueError
            except ValueError:
                QMessageBox.warning(self, "Dato no válido", f"{etiqueta} debe ser un número mayor que cero.")
                return None
            datos[clave] = valor
        calorias_texto = self.input_calorias.text().strip().replace(",", ".")
        try:
            calorias = float(calorias_texto)
            if calorias <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Calorías no válidas", "Captura una cantidad de calorías mayor que cero.")
            return None
        datos["calorias"] = calorias
        altura_texto = self.input_altura.text().strip().replace(",", ".")
        try:
            altura_cm = float(altura_texto)
            if not 50 <= altura_cm <= 250:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Estatura no válida", "Captura una estatura entre 50 y 250 cm.")
            return None
        datos["altura_cm"] = altura_cm
        altura_m = altura_cm / 100
        datos["imc"] = round(datos["peso"] / (altura_m ** 2), 1)
        return datos

    def limpiar(self):
        for campo in (self.input_peso, self.input_grasa, self.input_masa_muscular, self.input_agua,
                      self.input_altura, self.input_calorias):
            campo.clear()
