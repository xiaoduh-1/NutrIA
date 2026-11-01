import os
os.environ["QT_API"] = "pyside6"

from pathlib import Path
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy, QStackedWidget,
)
from qframelesswindow import FramelessWindow, StandardTitleBar
from qfluentwidgets import (
    IconWidget, BodyLabel, LineEdit, PasswordLineEdit, CheckBox,
    PrimaryPushButton, HyperlinkButton, FluentIcon, setTheme, Theme,
)
from .recuperar_contraseña import RecuperarPasswordWidget
from .registro_usuario import RegistroUsuarioWidget


class LoginWindow(FramelessWindow):
    login_exitoso = Signal()

    def __init__(self):
        super().__init__()
        setTheme(Theme.DARK)
        self.setWindowTitle("NutrIA")
        self.resize(900, 600)
        self.setTitleBar(StandardTitleBar(self))
        self.titleBar.setTitle("NutrIA")
        self.titleBar.titleLabel.setStyleSheet("color: black; background: transparent;")

        pagina_login = QWidget()
        login_layout = QHBoxLayout(pagina_login)
        login_layout.setContentsMargins(0, 0, 0, 0)
        login_layout.setSpacing(0)

        self.imagen = QLabel()
        self.imagen.setAlignment(Qt.AlignCenter)
        self.imagen.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        ruta = Path(__file__).resolve().parents[2] / "recursos" / "login.jpg"
        self._pixmap_login = QPixmap(str(ruta))
        if self._pixmap_login.isNull():
            self.imagen.setStyleSheet("background-color: #2b6cb0;")
        login_layout.addWidget(self.imagen, 1)

        derecha = QWidget()
        form = QVBoxLayout(derecha)
        form.setContentsMargins(32, 28, 32, 28)
        form.setSpacing(8)
        form.addStretch()

        logo = IconWidget(FluentIcon.PEOPLE)
        logo.setFixedSize(90, 90)
        form.addWidget(logo, alignment=Qt.AlignHCenter)
        form.addSpacing(16)
        form.addWidget(BodyLabel("Usuario"))
        self.input_usuario = LineEdit()
        self.input_usuario.setPlaceholderText("Usuario")
        self.input_usuario.setClearButtonEnabled(True)
        form.addWidget(self.input_usuario)
        form.addWidget(BodyLabel("Contraseña"))
        self.input_password = PasswordLineEdit()
        self.input_password.setPlaceholderText("Contraseña")
        form.addWidget(self.input_password)
        self.check_recordar = CheckBox("Recordar contraseña")
        form.addWidget(self.check_recordar)
        self.btn_ingresar = PrimaryPushButton("Ingresar")
        form.addWidget(self.btn_ingresar)
        self.btn_registro = HyperlinkButton("", "¿No tienes cuenta? Regístrate")
        form.addWidget(self.btn_registro, alignment=Qt.AlignHCenter)
        self.btn_olvide = HyperlinkButton("", "¿Olvidaste tu contraseña?")
        form.addWidget(self.btn_olvide, alignment=Qt.AlignHCenter)
        form.addStretch()
        login_layout.addWidget(derecha, 1)
        derecha.setStyleSheet("background-color: rgb(32, 32, 32);")

        self.recuperar = RecuperarPasswordWidget()
        self.registro = RegistroUsuarioWidget()
        self.stack = QStackedWidget()
        self.stack.addWidget(pagina_login)
        self.stack.addWidget(self.recuperar)
        self.stack.addWidget(self.registro)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stack)

        self.recuperar.setStyleSheet("background-color: rgb(32, 32, 32);")
        self.registro.setStyleSheet("background-color: rgb(32, 32, 32);")
        self.titleBar.raise_()

        self.btn_ingresar.clicked.connect(self.login_exitoso.emit)
        self.btn_registro.clicked.connect(lambda: self.stack.setCurrentWidget(self.registro))
        self.registro.btn_regresar.clicked.connect(lambda: self.stack.setCurrentWidget(pagina_login))
        self.btn_olvide.clicked.connect(lambda: self.stack.setCurrentWidget(self.recuperar))
        self.recuperar.btn_regresar.clicked.connect(lambda: self.stack.setCurrentWidget(pagina_login))
        self._ajustar_imagen()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._ajustar_imagen()

    def _ajustar_imagen(self):
        if (not hasattr(self, "_pixmap_login") or not hasattr(self, "imagen")
                or self._pixmap_login.isNull() or self.imagen.width() <= 0 or self.imagen.height() <= 0):
            return
        self.imagen.setPixmap(self._pixmap_login.scaled(
            self.imagen.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
