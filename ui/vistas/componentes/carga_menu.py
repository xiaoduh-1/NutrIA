from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import ProgressRing, StrongBodyLabel, BodyLabel


class CargaMenuInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("cargaMenuInterface")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)

        self.anillo = ProgressRing()
        self.anillo.setFixedSize(80, 80)
        self.anillo.setTextVisible(False)
        self.anillo.setStrokeWidth(6)
        layout.addWidget(self.anillo, alignment=Qt.AlignHCenter)
        layout.addSpacing(10)

        layout.addWidget(StrongBodyLabel("NutrIA está trabajando"), alignment=Qt.AlignHCenter)
        for texto in ["Analizando la información del paciente...",
                      "Calculando distribución nutricional...",
                      "Generando propuesta de menu..."]:
            layout.addWidget(BodyLabel(texto), alignment=Qt.AlignHCenter)