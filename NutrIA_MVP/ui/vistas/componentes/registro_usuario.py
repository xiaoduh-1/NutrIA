from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QMessageBox
from qfluentwidgets import (
    TitleLabel, StrongBodyLabel, LineEdit, PasswordLineEdit, PushButton,
    PrimaryPushButton,
)


class RegistroUsuarioWidget(QWidget):
    continuar = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        externo = QVBoxLayout(self)
        externo.setContentsMargins(24, 30, 24, 30)

        contenedor = QWidget()
        contenedor.setMaximumWidth(460)
        contenedor.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        layout = QVBoxLayout(contenedor)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(TitleLabel("Crear cuenta"), alignment=Qt.AlignHCenter)
        layout.addWidget(StrongBodyLabel("Datos del nutriólogo"), alignment=Qt.AlignHCenter)
        layout.addSpacing(8)

        self.input_nombre = LineEdit()
        self.input_nombre.setPlaceholderText("Nombre completo")
        self._agregar_campo(layout, "Nombre completo", self.input_nombre)
        self.input_usuario = LineEdit()
        self.input_usuario.setPlaceholderText("Usuario para ingresar")
        self._agregar_campo(layout, "Usuario", self.input_usuario)
        self.input_correo = LineEdit()
        self.input_correo.setPlaceholderText("nombre@correo.com")
        self._agregar_campo(layout, "Correo electrónico", self.input_correo)
        self.input_password = PasswordLineEdit()
        self.input_password.setPlaceholderText("Mínimo 8 caracteres")
        self._agregar_campo(layout, "Contraseña", self.input_password)
        self.input_repetir = PasswordLineEdit()
        self.input_repetir.setPlaceholderText("Escribe nuevamente la contraseña")
        self._agregar_campo(layout, "Repetir contraseña", self.input_repetir)
        self.btn_crear = PrimaryPushButton("Continuar")
        layout.addSpacing(8)
        layout.addWidget(self.btn_crear)
        self.btn_regresar = PushButton("Regresar")
        layout.addWidget(self.btn_regresar, alignment=Qt.AlignHCenter)
        self.btn_crear.clicked.connect(self.validar_y_continuar)

        externo.addStretch()
        externo.addWidget(contenedor, alignment=Qt.AlignHCenter)
        externo.addStretch()

    @staticmethod
    def _agregar_campo(layout, etiqueta, campo):
        label = StrongBodyLabel(etiqueta)
        label.setStyleSheet("font-size: 16px; font-weight: 600;")
        label.setFixedWidth(400)
        layout.addWidget(label)
        campo.setMinimumHeight(40)
        layout.addWidget(campo)

    def validar_y_continuar(self):
        datos = {
            "nombre": self.input_nombre.text().strip(),
            "usuario": self.input_usuario.text().strip(),
            "correo": self.input_correo.text().strip(),
            "password": self.input_password.text(),
        }
        repetir = self.input_repetir.text()
        if not all((datos["nombre"], datos["usuario"], datos["correo"], datos["password"], repetir)):
            QMessageBox.warning(self, "Datos incompletos", "Completa todos los datos para continuar.")
            return
        if len(datos["usuario"]) < 3:
            QMessageBox.warning(self, "Usuario no válido", "El usuario debe tener al menos 3 caracteres.")
            return
        if "@" not in datos["correo"] or "." not in datos["correo"].split("@")[-1]:
            QMessageBox.warning(self, "Correo no válido", "Revisa el formato del correo electrónico.")
            return
        if len(datos["password"]) < 8:
            QMessageBox.warning(self, "Contraseña no válida", "La contraseña debe tener al menos 8 caracteres.")
            return
        if datos["password"] != repetir:
            QMessageBox.warning(self, "Contraseñas diferentes", "Las contraseñas no coinciden.")
            return

        self.input_password.clear()
        self.input_repetir.clear()
        self.continuar.emit(datos)
