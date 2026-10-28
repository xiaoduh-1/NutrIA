from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import TitleLabel, BodyLabel, HyperlinkButton

class proximascitasInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("proximasCitasInterface")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(12)

        layout.addWidget(TitleLabel("Citas del día:"))

        citas = [
            ("10:00", "Juan Pérez"),
            ("11:30", "María López"),
            ("13:00", "Roberto García"),
        ]

        for hora, paciente in citas:
            fila = QHBoxLayout()
            fila.addWidget(BodyLabel(hora))
            fila.addWidget(BodyLabel(paciente))
            fila.addStretch()
            fila.addWidget(HyperlinkButton("", "Ver"))
            layout.addLayout(fila)

        layout.addStretch()