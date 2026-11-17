from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QMessageBox
from qfluentwidgets import (
    TitleLabel, BodyLabel, LineEdit, PasswordLineEdit, PushButton,
    PrimaryPushButton, FluentIcon,
)

from datos.servicio_recuperacion import servicio_recuperacion


class RecuperarPasswordWidget(QWidget):
    MENSAJE_GENERICO = (
        "Si el correo corresponde a una cuenta, recibirás un código de recuperación. "
        "Revisa también la carpeta de spam."
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 40, 30, 30)
        layout.setSpacing(12)
        layout.addWidget(TitleLabel("Recuperar contraseña"), alignment=Qt.AlignHCenter)
        layout.addWidget(BodyLabel("Ingresa el correo registrado para recibir un código temporal."))

        self.input_correo = LineEdit()
        self.input_correo.setPlaceholderText("Correo electrónico")
        self.input_correo.setClearButtonEnabled(True)
        layout.addWidget(self.input_correo)
        self.btn_enviar = PrimaryPushButton("Enviar código")
        layout.addWidget(self.btn_enviar)

        self.input_codigo = LineEdit()
        self.input_codigo.setPlaceholderText("Código de 6 dígitos")
        self.input_codigo.setMaxLength(6)
        self.input_codigo.setVisible(False)
        layout.addWidget(self.input_codigo)
        self.input_password = PasswordLineEdit()
        self.input_password.setPlaceholderText("Nueva contraseña (mínimo 8 caracteres)")
        self.input_password.setVisible(False)
        layout.addWidget(self.input_password)
        self.input_password_repetida = PasswordLineEdit()
        self.input_password_repetida.setPlaceholderText("Repite la nueva contraseña")
        self.input_password_repetida.setVisible(False)
        layout.addWidget(self.input_password_repetida)
        self.btn_cambiar = PrimaryPushButton("Cambiar contraseña")
        self.btn_cambiar.setVisible(False)
        layout.addWidget(self.btn_cambiar)

        layout.addStretch()
        botones = QHBoxLayout()
        self.btn_regresar = PushButton(FluentIcon.LEFT_ARROW, "Regresar")
        botones.addWidget(self.btn_regresar)
        botones.addStretch()
        layout.addLayout(botones)

        self.btn_enviar.clicked.connect(self.enviar_codigo)
        self.btn_cambiar.clicked.connect(self.cambiar_password)

    def enviar_codigo(self):
        correo = self.input_correo.text().strip()
        if not correo or "@" not in correo:
            QMessageBox.warning(self, "Correo requerido", "Escribe un correo electrónico válido.")
            return
        self.btn_enviar.setEnabled(False)
        try:
            servicio_recuperacion.solicitar_codigo(correo)
        except Exception as error:
            QMessageBox.critical(
                self, "No se pudo enviar el código",
                f"Verifica la conexión a PostgreSQL y la configuración SMTP en .env.\n\n{error}",
            )
            self.btn_enviar.setEnabled(True)
            return
        QMessageBox.information(self, "Recuperación", self.MENSAJE_GENERICO)
        self.input_codigo.setVisible(True)
        self.input_password.setVisible(True)
        self.input_password_repetida.setVisible(True)
        self.btn_cambiar.setVisible(True)

    def cambiar_password(self):
        correo = self.input_correo.text().strip()
        codigo = self.input_codigo.text().strip()
        password = self.input_password.text()
        repetida = self.input_password_repetida.text()
        if len(codigo) != 6 or not codigo.isdigit():
            QMessageBox.warning(self, "Código inválido", "Escribe el código de 6 dígitos recibido por correo.")
            return
        if len(password) < 8:
            QMessageBox.warning(self, "Contraseña inválida", "La nueva contraseña debe tener al menos 8 caracteres.")
            return
        if password != repetida:
            QMessageBox.warning(self, "Las contraseñas no coinciden", "Vuelve a escribir la misma contraseña en ambos campos.")
            return
        try:
            resultado = servicio_recuperacion.restablecer_password(correo, codigo, password)
        except Exception as error:
            QMessageBox.critical(
                self, "No se pudo cambiar la contraseña",
                f"Verifica la conexión a PostgreSQL y que la migración de recuperación esté aplicada.\n\n{error}",
            )
            return
        if resultado != "correcto":
            QMessageBox.warning(
                self, "Código inválido o vencido",
                "El código no es válido, ya se utilizó o venció. Solicita uno nuevo e inténtalo otra vez.",
            )
            return
        QMessageBox.information(self, "Contraseña actualizada", "Ya puedes ingresar con tu nueva contraseña.")
        self._limpiar()

    def _limpiar(self):
        self.input_correo.clear()
        self.input_codigo.clear()
        self.input_password.clear()
        self.input_password_repetida.clear()
        self.input_codigo.setVisible(False)
        self.input_password.setVisible(False)
        self.input_password_repetida.setVisible(False)
        self.btn_cambiar.setVisible(False)
        self.btn_enviar.setEnabled(True)
