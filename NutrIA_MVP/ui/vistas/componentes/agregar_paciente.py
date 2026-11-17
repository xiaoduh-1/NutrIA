import re
from datetime import date, datetime

from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QMessageBox
from qfluentwidgets import (SubtitleLabel, BodyLabel, LineEdit, ComboBox, TextEdit,PushButton, PrimaryPushButton, FluentIcon)


class agregarPaciente(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("agregarPacienteInterface")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(12)

        layout.addWidget(SubtitleLabel("Información personal"))

        #formulario
        grid = QGridLayout()
        grid.setHorizontalSpacing(30)
        grid.setVerticalSpacing(10)

        self.input_nombre = LineEdit()
        self.input_apellido = LineEdit()
        self.input_fecha_nacimiento = LineEdit()
        self.input_fecha_nacimiento.setInputMask("00/00/0000;_")
        self.input_fecha_nacimiento.setPlaceholderText("DD/MM/AAAA")
        self.combo_sexo = ComboBox()
        self.combo_sexo.addItems(["Masculino", "Femenino", "Otro"])
        self.input_telefono = LineEdit()
        self.input_telefono.setMaxLength(10)
        self.input_telefono.setValidator(
            QRegularExpressionValidator(QRegularExpression(r"[0-9]{0,10}"), self.input_telefono)
        )
        self.input_correo = LineEdit()

        grid.addWidget(BodyLabel("Nombre:"), 0, 0)
        grid.addWidget(BodyLabel("Apellido:"), 0, 1)
        grid.addWidget(self.input_nombre, 1, 0)
        grid.addWidget(self.input_apellido, 1, 1)

        grid.addWidget(BodyLabel("Fecha de nacimiento:"), 2, 0)
        grid.addWidget(BodyLabel("Sexo:"), 2, 1)
        grid.addWidget(self.input_fecha_nacimiento, 3, 0)
        grid.addWidget(self.combo_sexo, 3, 1)

        grid.addWidget(BodyLabel("Telefono:"), 4, 0)
        grid.addWidget(BodyLabel("Correo:"), 4, 1)
        grid.addWidget(self.input_telefono, 5, 0)
        grid.addWidget(self.input_correo, 5, 1)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        layout.addLayout(grid)

        #Observaciones
        layout.addWidget(BodyLabel("Observaciones:"))
        self.input_observaciones = TextEdit()
        self.input_observaciones.setMinimumHeight(100)
        layout.addWidget(self.input_observaciones)
        self.paciente_id = None

        layout.addStretch()

        #Botones
        botones = QHBoxLayout()
        self.btn_cancelar = PushButton("Cancelar")
        self.btn_guardar = PrimaryPushButton(FluentIcon.SAVE, "Guardar paciente")
        botones.addWidget(self.btn_cancelar)
        botones.addStretch()
        botones.addWidget(self.btn_guardar)
        layout.addLayout(botones)

    def cargar_paciente(self, paciente=None):
        self.paciente_id = paciente["id"] if paciente else None
        self.input_nombre.setText(paciente["nombre"] if paciente else "")
        self.input_apellido.setText(paciente["apellido"] if paciente else "")
        self.input_fecha_nacimiento.setText(paciente.get("fecha_nacimiento", "") if paciente else "")
        self.combo_sexo.setCurrentText(paciente.get("sexo", "Masculino") or "Masculino" if paciente else "Masculino")
        self.input_telefono.setText(paciente.get("telefono", "") if paciente else "")
        self.input_correo.setText(paciente.get("correo", "") if paciente else "")
        self.input_observaciones.setPlainText(paciente.get("observaciones", "") if paciente else "")

    def obtener_datos(self):
        texto_fecha = self.input_fecha_nacimiento.text()
        digitos_fecha = "".join(caracter for caracter in texto_fecha if caracter.isdigit())
        fecha_nacimiento = (
            f"{digitos_fecha[:2]}/{digitos_fecha[2:4]}/{digitos_fecha[4:]}"
            if digitos_fecha else ""
        )
        datos = {
            "nombre": self.input_nombre.text().strip(),
            "apellido": self.input_apellido.text().strip(),
            "fecha_nacimiento": fecha_nacimiento,
            "sexo": self.combo_sexo.currentText(),
            "telefono": self.input_telefono.text().strip(),
            "correo": self.input_correo.text().strip(),
            "observaciones": self.input_observaciones.toPlainText().strip(),
        }
        if not datos["nombre"] or not datos["apellido"]:
            QMessageBox.warning(self, "Datos incompletos", "Nombre y apellido son obligatorios.")
            return None
        if datos["fecha_nacimiento"]:
            if not re.fullmatch(r"[0-9]{2}/[0-9]{2}/[0-9]{4}", datos["fecha_nacimiento"]):
                QMessageBox.warning(self, "Fecha no válida", "Usa el formato DD/MM/AAAA.")
                return None
            try:
                nacimiento = datetime.strptime(datos["fecha_nacimiento"], "%d/%m/%Y").date()
            except ValueError:
                QMessageBox.warning(self, "Fecha no válida", "Escribe una fecha de nacimiento válida en formato DD/MM/AAAA.")
                return None
            hoy = date.today()
            try:
                fecha_limite = hoy.replace(year=hoy.year - 100)
            except ValueError:  # 29 de febrero en años bisiestos
                fecha_limite = hoy.replace(year=hoy.year - 100, day=28)
            if nacimiento > hoy:
                QMessageBox.warning(self, "Fecha no válida", "La fecha de nacimiento no puede ser posterior a hoy.")
                return None
            if nacimiento < fecha_limite:
                QMessageBox.warning(
                    self, "Fecha no válida",
                    f"La fecha de nacimiento no puede ser anterior al {fecha_limite.strftime('%d/%m/%Y')}.",
                )
                return None
        if datos["telefono"] and (
            len(datos["telefono"]) != 10 or not datos["telefono"].isascii() or not datos["telefono"].isdigit()
        ):
            QMessageBox.warning(self, "Teléfono no válido", "El teléfono debe contener exactamente 10 dígitos.")
            return None
        if datos["correo"] and "@" not in datos["correo"]:
            QMessageBox.warning(self, "Correo no válido", "Revisa el formato del correo electrónico.")
            return None
        return datos
