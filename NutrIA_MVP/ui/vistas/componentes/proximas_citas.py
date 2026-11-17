from datetime import date, datetime

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea
from qfluentwidgets import TitleLabel, BodyLabel, HyperlinkButton
from datos import repositorio


class proximascitasInterface(QWidget):
    cita_seleccionada = Signal(str)
    MESES = (
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("proximasCitasInterface")
        self._preservar_dia_al_mostrar = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(12)

        self.lbl_titulo = TitleLabel("Próximas citas")
        layout.addWidget(self.lbl_titulo)

        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        contenido = QWidget()
        self.filas_layout = QVBoxLayout(contenido)
        self.filas_layout.setContentsMargins(0, 0, 0, 0)
        self.filas_layout.setSpacing(10)
        self.scroll.setWidget(contenido)
        layout.addWidget(self.scroll)

        self.actualizar()

    def actualizar(self, fecha=None):
        """Sin fecha muestra el mes actual; con fecha, solo ese día."""
        if fecha is None:
            self._preservar_dia_al_mostrar = False
            fecha_ref = date.today()
            citas = repositorio.listar_citas_mes(fecha_ref.isoformat())
            nombre_mes = self.MESES[fecha_ref.month - 1].capitalize()
            self.lbl_titulo.setText(f"Próximas citas — {nombre_mes} de {fecha_ref.year}")
            mostrar_fecha = True
            mensaje_vacio = "No hay citas programadas para este mes."
        else:
            fecha_iso = fecha.toString("yyyy-MM-dd") if hasattr(fecha, "toString") else str(fecha)
            fecha_dia = datetime.strptime(fecha_iso, "%Y-%m-%d").date()
            self._preservar_dia_al_mostrar = not self.isVisible()
            citas = repositorio.listar_citas(fecha_iso)
            self.lbl_titulo.setText(
                f"Citas del día {fecha_dia.strftime('%d/%m/%Y')}"
            )
            mostrar_fecha = False
            mensaje_vacio = "No hay citas programadas para esta fecha."

        self._limpiar_filas()
        if not citas:
            self.filas_layout.addWidget(BodyLabel(mensaje_vacio))
        else:
            for cita in citas:
                self._agregar_fila(cita, mostrar_fecha)
        self.filas_layout.addStretch()

    def _agregar_fila(self, cita, mostrar_fecha):
        fila = QHBoxLayout()
        if mostrar_fecha:
            fecha = datetime.strptime(cita["fecha"], "%Y-%m-%d")
            fila.addWidget(BodyLabel(fecha.strftime("%d/%m/%Y")))
        fila.addWidget(BodyLabel(cita["hora"]))
        fila.addWidget(BodyLabel(cita["paciente"]))
        fila.addStretch()
        btn_ver = HyperlinkButton("", "Ver")
        btn_ver.clicked.connect(
            lambda _=False, cita_id=cita["id"]: self.cita_seleccionada.emit(cita_id)
        )
        fila.addWidget(btn_ver)
        self.filas_layout.addLayout(fila)

    def _limpiar_filas(self):
        while self.filas_layout.count():
            item = self.filas_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

    def showEvent(self, event):
        super().showEvent(event)
        if self._preservar_dia_al_mostrar:
            self._preservar_dia_al_mostrar = False
            return
        self.actualizar()
