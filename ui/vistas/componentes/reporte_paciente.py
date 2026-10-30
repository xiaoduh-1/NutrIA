from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from qfluentwidgets import CardWidget, StrongBodyLabel, PushButton, PrimaryPushButton, FluentIcon


class ReportePacienteInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("reportePacienteInterface")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(10)

        tarjeta = CardWidget()
        tarjeta_layout = QVBoxLayout(tarjeta)
        tarjeta_layout.setContentsMargins(20, 16, 20, 16)
        tarjeta_layout.setSpacing(10)

        self.lbl_titulo = StrongBodyLabel('Reporte de paciente: "Juan Pérez"')
        tarjeta_layout.addWidget(self.lbl_titulo)

        self.lbl_grafica = QLabel("(Grafica)")
        self.lbl_grafica.setAlignment(Qt.AlignCenter)
        self.lbl_grafica.setMinimumHeight(300)
        self.lbl_grafica.setStyleSheet(
            "background-color: white; color: #444; border-radius: 4px;")
        tarjeta_layout.addWidget(self.lbl_grafica, 1)

        layout.addWidget(tarjeta, 1)

        #Botones
        botones = QHBoxLayout()
        self.btn_regresar = PushButton(FluentIcon.LEFT_ARROW, "Regresar")
        self.btn_exportar = PushButton(FluentIcon.DOCUMENT,"Exportar PDF")
        botones.addWidget(self.btn_regresar)
        botones.addStretch()
        botones.addWidget(self.btn_exportar)
        layout.addLayout(botones)

    def set_grafica(self, ruta_imagen):
        pixmap = QPixmap(str(ruta_imagen))
        if not pixmap.isNull():
            self.lbl_grafica.setPixmap(pixmap.scaled(
                self.lbl_grafica.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))