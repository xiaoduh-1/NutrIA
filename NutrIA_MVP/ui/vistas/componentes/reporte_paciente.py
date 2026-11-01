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
        self.lbl_titulo = StrongBodyLabel("Reporte de paciente: —")
        tarjeta_layout.addWidget(self.lbl_titulo)
        self.lbl_grafica = QLabel("No hay mediciones registradas.")
        self.lbl_grafica.setAlignment(Qt.AlignCenter)
        self.lbl_grafica.setWordWrap(True)
        self.lbl_grafica.setMinimumHeight(220)
        self.lbl_grafica.setStyleSheet("background-color: white; color: #444; border-radius: 4px; padding: 16px;")
        tarjeta_layout.addWidget(self.lbl_grafica, 1)
        layout.addWidget(tarjeta, 1)

        botones = QHBoxLayout()
        self.btn_regresar = PushButton(FluentIcon.LEFT_ARROW, "Regresar")
        self.btn_exportar = PrimaryPushButton(FluentIcon.DOCUMENT, "Exportar PDF")
        botones.addWidget(self.btn_regresar)
        botones.addStretch()
        botones.addWidget(self.btn_exportar)
        layout.addLayout(botones)

    def cargar_paciente(self, paciente, mediciones):
        nombre = f"{paciente['nombre']} {paciente['apellido']}"
        self.lbl_titulo.setText(f"Reporte de paciente: {nombre}")
        if not mediciones:
            self.lbl_grafica.setText("No hay mediciones registradas para este paciente.")
            return
        filas = ["Historial de mediciones", ""]
        for medicion in mediciones:
            filas.append(
                f"{medicion.get('fecha', '—')}  ·  "
                f"Peso: {medicion.get('peso', '—')} kg  ·  "
                f"IMC: {medicion.get('imc', '—')}")
        self.lbl_grafica.setText("\n".join(filas))

    def set_grafica(self, ruta_imagen):
        pixmap = QPixmap(str(ruta_imagen))
        if not pixmap.isNull():
            self.lbl_grafica.setText("")
            self.lbl_grafica.setPixmap(pixmap.scaled(
                self.lbl_grafica.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
