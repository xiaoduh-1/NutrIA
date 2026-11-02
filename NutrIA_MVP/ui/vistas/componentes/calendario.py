from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QCalendarWidget
from qfluentwidgets import StrongBodyLabel, PushButton, FluentIcon
from datos import repositorio


class CalendarioConCitas(QCalendarWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fechas_con_citas = set()

    def establecer_fechas_con_citas(self, fechas):
        self.fechas_con_citas = set(fechas)
        self.updateCells()

    def paintCell(self, painter, rect, fecha):
        super().paintCell(painter, rect, fecha)
        if fecha.toString("yyyy-MM-dd") not in self.fechas_con_citas:
            return
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#3B82F6"))
        diametro = 6
        painter.drawEllipse(
            rect.center().x() - diametro // 2,
            rect.bottom() - 8,
            diametro,
            diametro,
        )
        painter.restore()


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

        self.calendario = CalendarioConCitas(self)
        self.calendario.setGridVisible(True)
        layout.addWidget(self.calendario)
        self.actualizar_marcadores()

    def actualizar_marcadores(self):
        fechas = {cita["fecha"] for cita in repositorio.citas.values()}
        self.calendario.establecer_fechas_con_citas(fechas)
