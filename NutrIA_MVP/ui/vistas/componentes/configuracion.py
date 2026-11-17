from pathlib import Path

from PySide6.QtCore import Qt, QByteArray, QBuffer, QIODevice
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFileDialog, QDialog,
    QDialogButtonBox, QMessageBox,
)
from qfluentwidgets import (
    TitleLabel, StrongBodyLabel, CardWidget, AvatarWidget, PushButton,
    PrimaryPushButton, FluentIcon, TransparentPushButton, PasswordLineEdit,
    LineEdit,
)
from datos.sesion_nutriologo import sesion_nutriologo


class ConfiguracionInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("configuracionInterface")
        self.foto_path = ""
        self.foto_bytes = b""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(12)
        layout.addWidget(TitleLabel("Configuración"))

        tarjeta = CardWidget()
        tarjeta_layout = QVBoxLayout(tarjeta)
        tarjeta_layout.setContentsMargins(30, 24, 30, 24)
        tarjeta_layout.setSpacing(16)
        contenido = QHBoxLayout()
        contenido.setSpacing(32)

        datos = QGridLayout()
        datos.setHorizontalSpacing(12)
        datos.setVerticalSpacing(12)
        campos = [
            ("Nombre completo", "input_nombre"),
            ("Usuario", "input_usuario"),
            ("Correo electrónico", "input_correo"),
            ("Nombre del consultorio", "input_consultorio"),
            ("Teléfono de contacto", "input_telefono"),
            ("Correo de contacto", "input_correo_consultorio"),
        ]
        for fila, (etiqueta, atributo) in enumerate(campos):
            label = StrongBodyLabel(etiqueta)
            label.setStyleSheet("font-size: 15px; font-weight: 600;")
            campo = LineEdit()
            campo.setMinimumHeight(38)
            setattr(self, atributo, campo)
            datos.addWidget(label, fila, 0)
            datos.addWidget(campo, fila, 1)

        self.btn_editar_password = TransparentPushButton(FluentIcon.EDIT, "Cambiar contraseña")
        self.btn_editar_password.clicked.connect(self.abrir_cambio_password)
        datos.addWidget(self.btn_editar_password, len(campos), 0, 1, 2, alignment=Qt.AlignLeft)
        datos.setColumnStretch(1, 1)

        self.avatar = AvatarWidget()
        self.avatar.setText("?")
        self.avatar.setRadius(60)
        self.avatar.setCursor(Qt.PointingHandCursor)
        self.avatar.mousePressEvent = lambda _event: self.elegir_imagen()
        contenido.addLayout(datos, 1)

        col_avatar = QVBoxLayout()
        col_avatar.setSpacing(8)
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
        self.cargar_datos()

    def cargar_datos(self, datos=None):
        datos = datos if datos is not None else sesion_nutriologo.obtener_perfil()
        self.input_nombre.setText(datos.get("nombre", ""))
        self.input_usuario.setText(datos.get("usuario", ""))
        self.input_correo.setText(datos.get("correo", ""))
        self.input_consultorio.setText(datos.get("nombre_consultorio", ""))
        self.input_telefono.setText(datos.get("telefono_consultorio", ""))
        self.input_correo_consultorio.setText(datos.get("correo_consultorio", ""))
        self.foto_path = datos.get("foto_path", "") or ""
        self.foto_bytes = datos.get("foto_bytes", b"") or b""
        pixmap = QPixmap()
        if self.foto_bytes and pixmap.loadFromData(self.foto_bytes):
            self.avatar.setImage(pixmap)
        elif self.foto_path and Path(self.foto_path).is_file():
            self.avatar.setImage(self.foto_path)
        else:
            self.avatar.setImage(None)
            iniciales = "".join(palabra[0] for palabra in datos.get("nombre", "").split()[:2])
            self.avatar.setText(iniciales.upper() or "?")

    def elegir_imagen(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar foto", "", "Imágenes (*.png *.jpg *.jpeg *.bmp)")
        if ruta:
            pixmap = QPixmap(ruta)
            if pixmap.isNull():
                QMessageBox.warning(self, "Imagen no válida", "No se pudo abrir el archivo seleccionado.")
                return
            self.foto_path = str(Path(ruta))
            self.foto_bytes = self._pixmap_a_bytes(pixmap)
            pixmap.loadFromData(self.foto_bytes)
            self.avatar.setImage(pixmap)

    @staticmethod
    def _pixmap_a_bytes(pixmap):
        imagen = pixmap.scaled(512, 512, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        buffer_bytes = QByteArray()
        buffer = QBuffer(buffer_bytes)
        buffer.open(QIODevice.WriteOnly)
        imagen.save(buffer, "JPEG", 85)
        buffer.close()
        return bytes(buffer_bytes)

    def obtener_datos(self):
        return {
            "nombre": self.input_nombre.text().strip(),
            "usuario": self.input_usuario.text().strip(),
            "correo": self.input_correo.text().strip(),
            "nombre_consultorio": self.input_consultorio.text().strip(),
            "telefono_consultorio": self.input_telefono.text().strip(),
            "correo_consultorio": self.input_correo_consultorio.text().strip(),
            "foto_path": self.foto_path,
            "foto_bytes": self.foto_bytes,
        }

    def abrir_cambio_password(self):
        dialogo = QDialog(self)
        dialogo.setWindowTitle("Cambiar contraseña")
        dialogo.setMinimumWidth(380)
        layout = QVBoxLayout(dialogo)
        layout.addWidget(StrongBodyLabel("Confirma la contraseña actual"))
        actual = PasswordLineEdit()
        actual.setPlaceholderText("Contraseña actual")
        layout.addWidget(actual)
        layout.addWidget(StrongBodyLabel("Nueva contraseña (mínimo 8 caracteres)"))
        nueva = PasswordLineEdit()
        nueva.setPlaceholderText("Nueva contraseña")
        layout.addWidget(nueva)
        layout.addWidget(StrongBodyLabel("Repite la nueva contraseña"))
        repetir = PasswordLineEdit()
        repetir.setPlaceholderText("Repetir nueva contraseña")
        layout.addWidget(repetir)
        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botones.button(QDialogButtonBox.Ok).setText("Actualizar")
        botones.button(QDialogButtonBox.Cancel).setText("Cancelar")
        botones.accepted.connect(dialogo.accept)
        botones.rejected.connect(dialogo.reject)
        layout.addWidget(botones)

        if dialogo.exec() != QDialog.Accepted:
            return
        password_nueva = nueva.text()
        if len(password_nueva) < 8:
            QMessageBox.warning(self, "Contraseña no válida", "La nueva contraseña debe tener al menos 8 caracteres.")
            return
        if password_nueva != repetir.text():
            QMessageBox.warning(self, "Contraseñas diferentes", "Las contraseñas nuevas no coinciden.")
            return
        try:
            cambio_correcto = sesion_nutriologo.cambiar_password(actual.text(), password_nueva)
        except Exception as error:
            QMessageBox.critical(self, "Error al guardar", f"No se pudo actualizar la contraseña en PostgreSQL:\n{error}")
            return
        if not cambio_correcto:
            QMessageBox.warning(self, "Contraseña incorrecta", "La contraseña actual no coincide.")
            return
        QMessageBox.information(self, "Contraseña actualizada", "La contraseña se actualizó en PostgreSQL.")
