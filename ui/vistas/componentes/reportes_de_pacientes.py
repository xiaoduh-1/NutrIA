from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidgetItem, QHeaderView
from qfluentwidgets import (TitleLabel, SearchLineEdit, TableWidget, PushButton, HyperlinkButton, FluentIcon)


class reportedePacientes(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("reportesPacientesInterface")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(12)

        layout.addWidget(TitleLabel("Reportes"))

        #Buscador
        self.input_buscar = SearchLineEdit()
        self.input_buscar.setPlaceholderText("Buscar paciente...")
        layout.addWidget(self.input_buscar)

        #Tabla
        self.tabla = TableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["Paciente", "Fecha", "Tipo", "Opcion"])
        self.tabla.verticalHeader().hide()
        self.tabla.setBorderVisible(True)
        self.tabla.setBorderRadius(8)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        #Datos de ejemplo
        reportes = [
            ("Juan Pérez", "07/10/2026", "Consulta"),
            ("Juan Pérez", "07/10/2026", "Consulta"),
            ("Juan Pérez", "07/10/2026", "Consulta"),
            ("Juan Pérez", "07/10/2026", "Consulta"),
        ]
        self.tabla.setRowCount(len(reportes))

        self.botones_ver = []
        self.botones_pdf = []
        for fila, (paciente, fecha, tipo) in enumerate(reportes):
            self.tabla.setItem(fila, 0, QTableWidgetItem(paciente))
            self.tabla.setItem(fila, 1, QTableWidgetItem(fecha))
            self.tabla.setItem(fila, 2, QTableWidgetItem(tipo))

            #Columna opcion y los 2 bbotones
            celda = QWidget()
            celda_layout = QHBoxLayout(celda)
            celda_layout.setContentsMargins(0, 0, 0, 0)
            btn_ver = HyperlinkButton("", "Ver reporte")
            btn_pdf = HyperlinkButton("", "PDF")
            celda_layout.addWidget(btn_ver)
            celda_layout.addWidget(btn_pdf)
            self.tabla.setCellWidget(fila, 3, celda)
            self.botones_ver.append(btn_ver)
            self.botones_pdf.append(btn_pdf)

        layout.addWidget(self.tabla)

        #Boton
        inferior = QHBoxLayout()
        self.btn_regresar = PushButton(FluentIcon.LEFT_ARROW, "Regresar")
        inferior.addWidget(self.btn_regresar)
        inferior.addStretch()
        layout.addLayout(inferior)