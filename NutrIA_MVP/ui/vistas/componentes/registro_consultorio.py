from pathlib import Path

from PySide6.QtCore import Qt, Signal, QByteArray, QBuffer, QIODevice
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFileDialog, QMessageBox, QSizePolicy, QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (
    TitleLabel, StrongBodyLabel, LineEdit, PushButton, PrimaryPushButton,
    BodyLabel,
)


class RegistroConsultorioWidget(QWidget):
    registro_completo = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        exterior = QVBoxLayout(self)
        exterior.setContentsMargins(30, 24, 30, 24)
        exterior.addStretch()

        contenido = QWidget()
        contenido.setMaximumWidth(560)
        contenido.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        layout = QVBoxLayout(contenido)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(9)
        layout.addWidget(TitleLabel("Datos del consultorio"), alignment=Qt.AlignHCenter)
        layout.addWidget(StrongBodyLabel("Completa la información de contacto"), alignment=Qt.AlignHCenter)

        self.input_nombre = LineEdit()
        self.input_nombre.setPlaceholderText("Nombre del consultorio")
        self._agregar_campo(layout, "Nombre del consultorio", self.input_nombre)

        self.input_telefono = LineEdit()
        self.input_telefono.setPlaceholderText("Teléfono de contacto")
        self._agregar_campo(layout, "Teléfono de contacto", self.input_telefono)

        self.input_correo = LineEdit()
        self.input_correo.setPlaceholderText("contacto@consultorio.com")
        self._agregar_campo(layout, "Correo de contacto", self.input_correo)

        layout.addWidget(StrongBodyLabel("Foto de perfil o del consultorio"))
        foto_layout = QHBoxLayout()
        self.lbl_foto = BodyLabel("No se ha seleccionado una foto")
        self.lbl_foto.setWordWrap(True)
        self.lbl_foto.setMinimumHeight(100)
        self.lbl_foto.setAlignment(Qt.AlignCenter)
        self.lbl_foto.setStyleSheet("border: 1px dashed #888; border-radius: 8px; padding: 8px;")
        self.lbl_foto.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.lbl_foto.setFixedSize(150, 120)
        foto_layout.addWidget(self.lbl_foto)
        self.btn_foto = PushButton("Seleccionar foto")
        self.btn_foto.clicked.connect(self.elegir_foto)
        foto_layout.addWidget(self.btn_foto)
        foto_layout.addStretch()
        layout.addLayout(foto_layout)

        botones = QHBoxLayout()
        self.btn_regresar = PushButton("Regresar")
        self.btn_finalizar = PrimaryPushButton("Crear cuenta")
        botones.addWidget(self.btn_regresar)
        botones.addStretch()
        botones.addWidget(self.btn_finalizar)
        layout.addSpacing(8)
        layout.addLayout(botones)
        self.btn_finalizar.clicked.connect(self.validar_y_finalizar)
        exterior.addWidget(contenido, alignment=Qt.AlignHCenter)
        exterior.addStretch()
        self.foto_path = ""
        self.foto_bytes = b""

    @staticmethod
    def _agregar_campo(layout, etiqueta, campo):
        label = StrongBodyLabel(etiqueta)
        label.setStyleSheet("font-size: 16px; font-weight: 600;")
        label.setFixedWidth(400)
        layout.addWidget(label)
        campo.setMinimumHeight(40)
        layout.addWidget(campo)

    def elegir_foto(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar foto de perfil",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp)",
        )
        if not ruta:
            return
        pixmap = QPixmap(ruta)
        if pixmap.isNull():
            QMessageBox.warning(self, "Imagen no válida", "No se pudo abrir el archivo seleccionado.")
            return
        self.foto_path = str(Path(ruta))
        self.foto_bytes = self._pixmap_a_bytes(pixmap)
        self.lbl_foto.setPixmap(pixmap.scaled(
            self.lbl_foto.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))
        self.lbl_foto.setToolTip(self.foto_path)

    @staticmethod
    def _pixmap_a_bytes(pixmap):
        imagen = pixmap.scaled(512, 512, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        buffer_bytes = QByteArray()
        buffer = QBuffer(buffer_bytes)
        buffer.open(QIODevice.WriteOnly)
        imagen.save(buffer, "JPEG", 85)
        buffer.close()
        return bytes(buffer_bytes)

    def validar_y_finalizar(self):
        datos = {
            "nombre_consultorio": self.input_nombre.text().strip(),
            "telefono_consultorio": self.input_telefono.text().strip(),
            "correo_consultorio": self.input_correo.text().strip(),
            "foto_path": self.foto_path,
            "foto_bytes": self.foto_bytes,
        }
        if not all((datos["nombre_consultorio"], datos["telefono_consultorio"], datos["correo_consultorio"])):
            QMessageBox.warning(self, "Datos incompletos", "Completa nombre, teléfono y correo de contacto.")
            return
        if "@" not in datos["correo_consultorio"] or "." not in datos["correo_consultorio"].split("@")[-1]:
            QMessageBox.warning(self, "Correo no válido", "Revisa el correo de contacto del consultorio.")
            return
        self.registro_completo.emit(datos)

    def limpiar(self):
        self.input_nombre.clear()
        self.input_telefono.clear()
        self.input_correo.clear()
        self.foto_path = ""
        self.foto_bytes = b""
        self.lbl_foto.clear()
        self.lbl_foto.setText("No se ha seleccionado una foto")
        self.lbl_foto.setToolTip("")
