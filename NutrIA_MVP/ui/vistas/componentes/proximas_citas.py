from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import TitleLabel, BodyLabel, HyperlinkButton
from datos import repositorio

class proximascitasInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("proximasCitasInterface")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(12)

        layout.addWidget(TitleLabel("Citas del día:"))

        self.filas_layout = layout
        self.actualizar()

    def actualizar(self):
        while self.filas_layout.count() > 1:
            item = self.filas_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
        for cita in repositorio.listar_citas():
            fila = QHBoxLayout()
            fila.addWidget(BodyLabel(cita["hora"]))
            fila.addWidget(BodyLabel(cita["paciente"]))
            fila.addStretch()
            fila.addWidget(HyperlinkButton("", "Ver"))
            self.filas_layout.addLayout(fila)
        self.filas_layout.addStretch()
