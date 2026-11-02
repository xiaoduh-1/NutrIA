from datetime import date, datetime

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

        self.lbl_titulo = TitleLabel("Citas del día")
        layout.addWidget(self.lbl_titulo)

        self.filas_layout = layout
        self.actualizar()

    def actualizar(self, fecha=None):
        if fecha is None:
            fecha_iso = date.today().isoformat()
        elif hasattr(fecha, "toString"):
            fecha_iso = fecha.toString("yyyy-MM-dd")
        else:
            fecha_iso = str(fecha)
        fecha_texto = datetime.strptime(fecha_iso, "%Y-%m-%d").strftime("%d/%m/%Y")
        self.lbl_titulo.setText(f"Citas del {fecha_texto}")

        while self.filas_layout.count() > 1:
            item = self.filas_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
        citas = repositorio.listar_citas(fecha_iso)
        if not citas:
            self.filas_layout.addWidget(BodyLabel("No hay citas programadas para esta fecha."))
        for cita in citas:
            fila = QHBoxLayout()
            fila.addWidget(BodyLabel(cita["hora"]))
            fila.addWidget(BodyLabel(cita["paciente"]))
            fila.addStretch()
            fila.addWidget(HyperlinkButton("", "Ver"))
            self.filas_layout.addLayout(fila)
        self.filas_layout.addStretch()
