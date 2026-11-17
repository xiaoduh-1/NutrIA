from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QMessageBox
from qfluentwidgets import StrongBodyLabel, TitleLabel, BodyLabel, PrimaryPushButton, FluentIcon


class MedicionInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("medicionInterface")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(16)

        self.lbl_paciente = StrongBodyLabel("Paciente: —")
        layout.addWidget(self.lbl_paciente)
        layout.addWidget(TitleLabel("Medición corporal"), alignment=Qt.AlignHCenter)

        controles = QHBoxLayout()
        controles.addStretch()
        self.btn_iniciar = PrimaryPushButton(FluentIcon.PLAY, "Iniciar medición")
        self.btn_iniciar.setMinimumHeight(44)
        controles.addWidget(self.btn_iniciar)
        controles.addStretch()
        layout.addLayout(controles)

        self.lbl_estado = BodyLabel("Estado: Listo para medir")
        self.lbl_estado.setAlignment(Qt.AlignHCenter)
        self.lbl_estado.setWordWrap(True)
        layout.addWidget(self.lbl_estado)
        layout.addStretch()

    def mostrar_estado(self, texto):
        self.lbl_estado.setText(f"Estado: {texto}")

    def obtener_datos(self, fecha, objetivo, actividad, motivo, peso, altura_cm):
        try:
            peso = float(peso)
            altura_cm = float(altura_cm)
            if not 0 < peso < 1000:
                raise ValueError
            if not 50 <= altura_cm <= 250:
                raise ValueError
        except (TypeError, ValueError):
            QMessageBox.warning(
                self,
                "Medición no válida",
                "El peso o la estatura no están dentro de un rango válido.",
            )
            return None

        altura_m = altura_cm / 100
        return {
            "fecha": fecha,
            "objetivo": objetivo,
            "actividad": actividad,
            "motivo": motivo,
            "peso": peso,
            "altura_cm": altura_cm,
            "grasa": None,
            "masa_muscular": None,
            "agua": None,
            "agua_litros": None,
            "calorias": None,
            "imc": round(peso / (altura_m ** 2), 1),
        }

    def limpiar(self):
        self.btn_iniciar.setEnabled(True)
        self.mostrar_estado("Listo para medir")
