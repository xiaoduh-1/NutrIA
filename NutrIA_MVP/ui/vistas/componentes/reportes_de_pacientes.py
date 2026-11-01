from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Signal
from qfluentwidgets import (TitleLabel, SearchLineEdit, TableWidget, PushButton, HyperlinkButton, FluentIcon)
from datos import repositorio


class reportedePacientes(QWidget):
    reporte_seleccionado = Signal(str)

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

        self.botones_ver = []
        self.botones_pdf = []
        layout.addWidget(self.tabla)
        self.input_buscar.textChanged.connect(self.actualizar)
        self.actualizar()

        #Boton
        inferior = QHBoxLayout()
        self.btn_regresar = PushButton(FluentIcon.LEFT_ARROW, "Regresar")
        inferior.addWidget(self.btn_regresar)
        inferior.addStretch()
        layout.addLayout(inferior)

    def actualizar(self, paciente_id=None):
        termino = self.input_buscar.text().casefold().strip()
        filas = []
        for paciente in repositorio.listar_pacientes(termino):
            if paciente_id and paciente["id"] != paciente_id:
                continue
            for medicion in repositorio.listar_mediciones(paciente["id"]):
                filas.append((paciente, medicion))
        self.tabla.setRowCount(len(filas))
        self.botones_ver.clear()
        self.botones_pdf.clear()
        for fila, (paciente, medicion) in enumerate(filas):
            nombre = f"{paciente['nombre']} {paciente['apellido']}"
            self.tabla.setItem(fila, 0, QTableWidgetItem(nombre))
            self.tabla.setItem(fila, 1, QTableWidgetItem(medicion.get("fecha", "")))
            self.tabla.setItem(fila, 2, QTableWidgetItem("Medición"))
            celda = QWidget()
            celda_layout = QHBoxLayout(celda)
            celda_layout.setContentsMargins(0, 0, 0, 0)
            btn_ver = HyperlinkButton("", "Ver reporte")
            btn_pdf = HyperlinkButton("", "PDF")
            btn_ver.clicked.connect(lambda _=False, pid=paciente["id"]: self.reporte_seleccionado.emit(pid))
            celda_layout.addWidget(btn_ver)
            celda_layout.addWidget(btn_pdf)
            self.tabla.setCellWidget(fila, 3, celda)
            self.botones_ver.append(btn_ver)
            self.botones_pdf.append(btn_pdf)
