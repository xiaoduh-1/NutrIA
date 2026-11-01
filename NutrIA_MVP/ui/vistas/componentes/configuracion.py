from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFileDialog
from qfluentwidgets import (
    TitleLabel, StrongBodyLabel, BodyLabel, CardWidget, AvatarWidget,
    PushButton, PrimaryPushButton, FluentIcon, TransparentPushButton, ToolButton,
)


class ConfiguracionInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("configuracionInterface")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(12)
        layout.addWidget(TitleLabel("Configuración"))

        tarjeta = CardWidget()
        tarjeta_layout = QVBoxLayout(tarjeta)
        tarjeta_layout.setContentsMargins(30, 24, 30, 24)
        tarjeta_layout.setSpacing(16)
        contenido = QHBoxLayout()
        contenido.setSpacing(40)

        datos = QGridLayout()
        datos.setHorizontalSpacing(12)
        datos.setVerticalSpacing(20)
        self.lbl_consultorio = BodyLabel("Sin configurar")
        self.lbl_nombre = BodyLabel("Sin configurar")
        self.lbl_correo = BodyLabel("Sin configurar")
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

        self.avatar = AvatarWidget()
        self.avatar.setText("?")
        self.avatar.setRadius(60)
        self.avatar.setCursor(Qt.PointingHandCursor)
        self.avatar.mousePressEvent = lambda _event: self.elegir_imagen()
        contenido.addLayout(datos, 1)
        col_avatar = QVBoxLayout()
        col_avatar.setSpacing(6)
        col_avatar.addWidget(self.avatar, alignment=Qt.AlignHCenter)
        self.btn_cambiar_foto = TransparentPushButton(FluentIcon.CAMERA, "Cambiar foto")
        self.btn_cambiar_foto.clicked.connect(self.elegir_imagen)
        col_avatar.addWidget(self.btn_cambiar_foto, alignment=Qt.AlignHCenter)
        contenido.addLayout(col_avatar)
        tarjeta_layout.addLayout(contenido)
        tarjeta_layout.addStretch()

        botones = QHBoxLayout()
        self.btn_cancelar = PushButton("Cancelar")
        self.btn_guardar = PrimaryPushButton(FluentIcon.SAVE, "Guardar cambios")
        botones.addWidget(self.btn_cancelar)
        botones.addStretch()
        botones.addWidget(self.btn_guardar)
        tarjeta_layout.addLayout(botones)
        layout.addWidget(tarjeta, 1)

    def elegir_imagen(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar imagen", "", "Imágenes (*.png *.jpg *.jpeg)")
        if ruta:
            self.avatar.setImage(ruta)
