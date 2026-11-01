import os
os.environ["QT_API"] = "pyside6"

from pathlib import Path
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QColor
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy
from qframelesswindow import FramelessWindow, StandardTitleBar
from qfluentwidgets import (IconWidget, BodyLabel, LineEdit, PasswordLineEdit, CheckBox,PrimaryPushButton, HyperlinkButton, FluentIcon, setTheme, Theme)

class LoginWindow(FramelessWindow):
    login_exitoso = Signal()

    def __init__(self):
        super().__init__()
        setTheme(Theme.DARK)
        self.setWindowTitle("NutrIA")
        self.resize(900, 600)

        #Titulo
        self.setTitleBar(StandardTitleBar(self))
        self.titleBar.setTitle("NutrIA")
        self.titleBar.titleLabel.setStyleSheet("color: black; background: transparent;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        #Imagen
        self.imagen = QLabel()
        self.imagen.setAlignment(Qt.AlignCenter)
        self.imagen.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        ruta = Path(__file__).resolve().parents[2] / "recursos" / "login.jpg"
        self._pixmap_login = QPixmap(str(ruta))
        if self._pixmap_login.isNull():
            #si no hay imagen pone un color
            self.imagen.setStyleSheet("background-color: #2b6cb0;")
        else:
            self._ajustar_imagen()
        layout.addWidget(self.imagen, 1)

        #Formulario pa entrar
        derecha = QWidget()
        form = QVBoxLayout(derecha)
        form.setContentsMargins(50, 40, 50, 40)
        form.setSpacing(8)

        form.addStretch()

        logo = IconWidget(FluentIcon.PEOPLE)
        logo.setFixedSize(90, 90)
        form.addWidget(logo, alignment=Qt.AlignHCenter)
        form.addSpacing(20)

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

        self.btn_olvide = HyperlinkButton("", "¿Olvidaste tu contraseña?")
        form.addWidget(self.btn_olvide, alignment=Qt.AlignHCenter)

        form.addStretch()
        layout.addWidget(derecha, 1)

        #Color de la derecha
        derecha.setStyleSheet("background-color: rgb(32, 32, 32);")
        self.titleBar.raise_()

        self.btn_ingresar.clicked.connect(self.login_exitoso.emit)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._ajustar_imagen()

    def _ajustar_imagen(self):
        if (not hasattr(self, "_pixmap_login") or not hasattr(self, "imagen")
                or self._pixmap_login.isNull() or self.imagen.width() <= 0 or self.imagen.height() <= 0):
            return
        self.imagen.setPixmap(self._pixmap_login.scaled(
            self.imagen.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
