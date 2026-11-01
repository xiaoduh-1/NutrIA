from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QCalendarWidget
from qfluentwidgets import StrongBodyLabel, PushButton, FluentIcon


class calendarioInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calendario")
        self.setObjectName("calendarioInterface")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)

        encabezado = QHBoxLayout()
        encabezado.addWidget(StrongBodyLabel("Agenda"))
        encabezado.addStretch()
        self.btn_nueva_cita = PushButton(FluentIcon.ADD, "Nueva cita")
        encabezado.addWidget(self.btn_nueva_cita)
        layout.addLayout(encabezado)

        self.calendario = QCalendarWidget()
        self.calendario.setGridVisible(True)
        layout.addWidget(self.calendario)
