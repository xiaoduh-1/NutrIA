from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (TitleLabel, LineEdit, PasswordLineEdit, CheckBox,PushButton, PrimaryPushButton, FluentIcon)


class RegistroUsuarioWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        externo = QVBoxLayout(self)
        externo.setContentsMargins(0, 40, 0, 30)

        contenedor = QWidget()
        contenedor.setFixedWidth(400)
        layout = QVBoxLayout(contenedor)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        layout.addWidget(TitleLabel("Crear cuenta"), alignment=Qt.AlignHCenter)
        layout.addSpacing(6)

        self.input_nombre = LineEdit()
        self.input_nombre.setPlaceholderText("Nombre completo")
        layout.addWidget(self.input_nombre)

        self.input_usuario = LineEdit()
        self.input_usuario.setPlaceholderText("Usuario")
        layout.addWidget(self.input_usuario)

        self.input_correo = LineEdit()
        self.input_correo.setPlaceholderText("Correo electrónico")
        layout.addWidget(self.input_correo)

        self.input_password = PasswordLineEdit()
        self.input_password.setPlaceholderText("Contraseña")
        layout.addWidget(self.input_password)

        self.input_repetir = PasswordLineEdit()
        self.input_repetir.setPlaceholderText("Repetir contraseña")
        layout.addWidget(self.input_repetir)

        self.btn_crear = PrimaryPushButton("Crear cuenta")
        layout.addWidget(self.btn_crear)

        self.btn_regresar = PushButton(FluentIcon.LEFT_ARROW, "Regresar")
        layout.addWidget(self.btn_regresar, alignment=Qt.AlignHCenter)

        externo.addStretch()
        externo.addWidget(contenedor, alignment=Qt.AlignHCenter)
        externo.addStretch()