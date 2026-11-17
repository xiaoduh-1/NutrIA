import os
os.environ["QT_API"] = "pyside6"

from pathlib import Path
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy, QStackedWidget,
    QMessageBox,
)
from qframelesswindow import FramelessWindow, StandardTitleBar
from qfluentwidgets import (
    IconWidget, BodyLabel, LineEdit, PasswordLineEdit, CheckBox,
    PrimaryPushButton, HyperlinkButton, FluentIcon, setTheme, Theme,
)
from .recuperar_contraseña import RecuperarPasswordWidget
from .registro_usuario import RegistroUsuarioWidget
from .registro_consultorio import RegistroConsultorioWidget
from datos.sesion_nutriologo import SesionNutriologo, sesion_nutriologo


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
        self.registro_consultorio = RegistroConsultorioWidget()
        self._cuenta_pendiente = None
        self.stack = QStackedWidget()
        self.stack.addWidget(pagina_login)
        self.stack.addWidget(self.recuperar)
        self.stack.addWidget(self.registro)
        self.stack.addWidget(self.registro_consultorio)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stack)

        self.recuperar.setStyleSheet("background-color: rgb(32, 32, 32);")
        self.registro.setStyleSheet("background-color: rgb(32, 32, 32);")
        self.titleBar.raise_()

        self.btn_ingresar.clicked.connect(self.validar_login)
        self.btn_registro.clicked.connect(self.abrir_registro)
        self.registro.btn_regresar.clicked.connect(lambda: self.stack.setCurrentWidget(pagina_login))
        self.registro.continuar.connect(self.continuar_registro)
        self.registro_consultorio.btn_regresar.clicked.connect(self.regresar_a_registro)
        self.registro_consultorio.registro_completo.connect(self.completar_registro)
        self.btn_olvide.clicked.connect(lambda: self.stack.setCurrentWidget(self.recuperar))
        self.recuperar.btn_regresar.clicked.connect(lambda: self.stack.setCurrentWidget(pagina_login))
        self._ajustar_imagen()

    def validar_login(self):
        usuario = self.input_usuario.text().strip()
        password = self.input_password.text()
        try:
            autenticado = sesion_nutriologo.autenticar(usuario, password)
        except Exception as error:
            QMessageBox.critical(
                self, "Error de conexión",
                f"No se pudo validar la cuenta en PostgreSQL. Verifica la conexión y las tablas de registro.\n\n{error}",
            )
            return
        if not autenticado:
            QMessageBox.warning(
                self,
                "No se pudo ingresar",
                "El usuario o la contraseña no son correctos, o todavía no existe una cuenta registrada.",
            )
            return
        self.login_exitoso.emit()

    def abrir_registro(self):
        if sesion_nutriologo.obtener_perfil():
            QMessageBox.information(
                self, "Cuenta ya registrada",
                "La cuenta del nutriólogo ya existe. Ingresa con esas credenciales.",
            )
            return
        try:
            if sesion_nutriologo.existe_cuenta():
                QMessageBox.information(
                    self, "Cuenta ya registrada",
                    "Ya existe una cuenta de administrador. Ingresa con esas credenciales.",
                )
                return
        except Exception as error:
            QMessageBox.critical(
                self, "Error de conexión",
                f"No se pudo comprobar el registro en PostgreSQL. Verifica la conexión y las tablas.\n\n{error}",
            )
            return
        self.stack.setCurrentWidget(self.registro)

    def continuar_registro(self, datos_cuenta):
        if sesion_nutriologo.obtener_perfil():
            QMessageBox.information(
                self,
                "Cuenta ya registrada",
                "Ya existe una cuenta de nutriólogo en esta sesión. Ingresa con esa cuenta o edita sus datos desde Configuración.",
            )
            self.stack.setCurrentIndex(0)
            return
        cuenta = dict(datos_cuenta)
        password = cuenta.pop("password")
        cuenta["password_hash"] = SesionNutriologo.hashear_password(password)
        self._cuenta_pendiente = cuenta
        self.stack.setCurrentWidget(self.registro_consultorio)

    def regresar_a_registro(self):
        self.stack.setCurrentWidget(self.registro)

    def completar_registro(self, datos_consultorio):
        if not self._cuenta_pendiente:
            QMessageBox.warning(self, "Registro incompleto", "Vuelve a ingresar los datos del nutriólogo.")
            self.stack.setCurrentWidget(self.registro)
            return
        try:
            sesion_nutriologo.registrar_hash(self._cuenta_pendiente, datos_consultorio)
        except ValueError as error:
            QMessageBox.warning(self, "No se pudo registrar", str(error))
            return
        except Exception as error:
            QMessageBox.critical(
                self, "Error al guardar",
                f"No se pudieron guardar los datos en PostgreSQL. Verifica la conexión y ejecuta la migración de cuentas.\n\n{error}",
            )
            return
        self._cuenta_pendiente = None
        self.input_usuario.setText(sesion_nutriologo.obtener_perfil().get("usuario", ""))
        self.input_password.clear()
        self.registro_consultorio.limpiar()
        QMessageBox.information(
            self,
            "Registro completo",
            "La cuenta y los datos del consultorio quedaron guardados en PostgreSQL. La contraseña se almacena como hash. Ingresa con tu usuario y contraseña.",
        )
        self.stack.setCurrentIndex(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._ajustar_imagen()

    def _ajustar_imagen(self):
        if (not hasattr(self, "_pixmap_login") or not hasattr(self, "imagen")
                or self._pixmap_login.isNull() or self.imagen.width() <= 0 or self.imagen.height() <= 0):
            return
        self.imagen.setPixmap(self._pixmap_login.scaled(
            self.imagen.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
