from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFileDialog
from qfluentwidgets import (TitleLabel, StrongBodyLabel, BodyLabel, CardWidget, AvatarWidget,ToolButton, PushButton, PrimaryPushButton, FluentIcon, TransparentPushButton)

class ConfiguracionInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("configuracionInterface")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(12)

        layout.addWidget(TitleLabel("Configuración"))

        #Tarjeta principal
        tarjeta = CardWidget()
        tarjeta_layout = QVBoxLayout(tarjeta)
        tarjeta_layout.setContentsMargins(30, 24, 30, 24)
        tarjeta_layout.setSpacing(16)

        contenido = QHBoxLayout()
        contenido.setSpacing(40)

        #Datos del usuario
        datos = QGridLayout()
        datos.setHorizontalSpacing(12)
        datos.setVerticalSpacing(20)

        self.lbl_consultorio = BodyLabel('"Nutri"')
        self.lbl_nombre = BodyLabel("ese we")
        self.lbl_correo = BodyLabel("esewe@gmail.com")

        datos.addWidget(StrongBodyLabel("Consultorio:"), 0, 0)
        datos.addWidget(self.lbl_consultorio, 0, 1)

        datos.addWidget(StrongBodyLabel("Nombre:"), 1, 0)
        datos.addWidget(self.lbl_nombre, 1, 1)

        datos.addWidget(StrongBodyLabel("Correo:"), 2, 0)
        datos.addWidget(self.lbl_correo, 2, 1)
        self.btn_editar_correo = ToolButton(FluentIcon.EDIT)
        datos.addWidget(self.btn_editar_correo, 2, 2)

        datos.addWidget(StrongBodyLabel("Cambiar contraseña"), 3, 0, 1, 2)
        self.btn_editar_password = ToolButton(FluentIcon.EDIT)
        datos.addWidget(self.btn_editar_password, 3, 2)

        datos.setColumnStretch(3, 1)

        #Imagen de perfil
        self.avatar = AvatarWidget()
        ruta = Path(__file__).resolve().parents[2] / "recursos" / "avatar.png"
        if ruta.exists():
            self.avatar.setImage(str(ruta))
        else:
            self.avatar.setText("P")
        self.avatar.setRadius(60)
        self.avatar.setCursor(Qt.PointingHandCursor)
        self.avatar.mousePressEvent = lambda e: self.elegir_imagen()

        contenido.addLayout(datos, 1)
        col_avatar = QVBoxLayout()
        col_avatar.setSpacing(6)
        col_avatar.addWidget(self.avatar, alignment=Qt.AlignHCenter)

        self.btn_cambiar_foto = TransparentPushButton(FluentIcon.CAMERA, "Cambiar foto")
        self.btn_cambiar_foto.clicked.connect(lambda: self.elegir_imagen())
        col_avatar.addWidget(self.btn_cambiar_foto, alignment=Qt.AlignHCenter)
        col_avatar.addStretch()

        contenido.addLayout(col_avatar)
        tarjeta_layout.addLayout(contenido)

        tarjeta_layout.addStretch()

        #Botones
        botones = QHBoxLayout()
        self.btn_cancelar = PushButton("Cancelar")
        self.btn_guardar = PrimaryPushButton(FluentIcon.SAVE, "Guardar cambios")
        botones.addWidget(self.btn_cancelar)
        botones.addStretch()
        botones.addWidget(self.btn_guardar)
        tarjeta_layout.addLayout(botones)

        layout.addWidget(tarjeta, 1)

    #Imagen de perfil
    def elegir_imagen(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar imagen", "", "Imágenes (*.png *.jpg *.jpeg)")
        if ruta:
            self.avatar.setImage(ruta)