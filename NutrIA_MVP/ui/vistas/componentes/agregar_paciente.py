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
        self.input_fecha_nacimiento.setPlaceholderText("DD/MM/AAAA")
        self.combo_sexo = ComboBox()
        self.combo_sexo.addItems(["Masculino", "Femenino", "Otro"])
        self.input_telefono = LineEdit()
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
        datos = {
            "nombre": self.input_nombre.text().strip(),
            "apellido": self.input_apellido.text().strip(),
            "fecha_nacimiento": self.input_fecha_nacimiento.text().strip(),
            "sexo": self.combo_sexo.currentText(),
            "telefono": self.input_telefono.text().strip(),
            "correo": self.input_correo.text().strip(),
            "observaciones": self.input_observaciones.toPlainText().strip(),
        }
        if not datos["nombre"] or not datos["apellido"]:
            QMessageBox.warning(self, "Datos incompletos", "Nombre y apellido son obligatorios.")
            return None
        if datos["correo"] and "@" not in datos["correo"]:
            QMessageBox.warning(self, "Correo no válido", "Revisa el formato del correo electrónico.")
            return None
        return datos
