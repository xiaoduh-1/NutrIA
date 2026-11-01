from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import TitleLabel, LineEdit, PushButton, FluentIcon


class RecuperarPasswordWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 40, 30, 30)
        layout.setSpacing(12)
        layout.addWidget(TitleLabel("Recuperar contraseña"), alignment=Qt.AlignHCenter)
        self.input_correo = LineEdit()
        self.input_correo.setPlaceholderText("Correo electrónico")
        layout.addWidget(self.input_correo)
        layout.addStretch()
        botones = QHBoxLayout()
        self.btn_regresar = PushButton(FluentIcon.LEFT_ARROW, "Regresar")
        botones.addWidget(self.btn_regresar)
        botones.addStretch()
        layout.addLayout(botones)
