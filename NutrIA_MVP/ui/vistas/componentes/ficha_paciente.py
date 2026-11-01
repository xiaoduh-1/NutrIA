from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,QTableWidgetItem, QHeaderView)
from qfluentwidgets import (TitleLabel, BodyLabel, StrongBodyLabel, Pivot, TableWidget,PushButton, PrimaryPushButton, FluentIcon)
from datos import repositorio


class FichaPacienteInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("fichaPacienteInterface")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(12)

        #Titulo
        self.titulo = TitleLabel("Paciente: —")
        layout.addWidget(self.titulo)

        #Pestañas
        self.pivot = Pivot(self)
        self.stack = QStackedWidget(self)

        self.pestana_info = self._crear_pestana_info()
        self.pestana_mediciones = self._crear_pestana_mediciones()
        self.stack.addWidget(self.pestana_info)
        self.stack.addWidget(self.pestana_mediciones)

        self.pivot.addItem(routeKey="info", text="Información",
                           onClick=lambda: self.cambiar_pestana(0))
        self.pivot.addItem(routeKey="mediciones", text="Mediciones",
                           onClick=lambda: self.cambiar_pestana(1))
        self.pivot.setCurrentItem("info")

        layout.addWidget(self.pivot, alignment=Qt.AlignLeft)
        layout.addWidget(self.stack, 1)

        #Botones inferiores
        botones = QHBoxLayout()
        self.btn_editar = PushButton("Editar paciente")
        self.btn_eliminar = PushButton("Eliminar paciente")
        self.btn_ver_reporte = PushButton("Ver reporte")
        self.btn_nueva_medicion = PrimaryPushButton(FluentIcon.ADD, "Nueva medición")
        botones.addWidget(self.btn_editar)
        botones.addWidget(self.btn_eliminar)
        botones.addStretch()
        botones.addWidget(self.btn_ver_reporte)
        botones.addWidget(self.btn_nueva_medicion)
        layout.addLayout(botones)

        # "Ver reporte" solo se muestra en la pestaña Mediciones
        self.btn_ver_reporte.hide()
        self.paciente_id = None

    def cargar_paciente(self, paciente_id):
        self.paciente_id = paciente_id
        paciente = repositorio.obtener_paciente(paciente_id)
        if not paciente:
            return
        self.titulo.setText(f"Paciente: {paciente['nombre']} {paciente['apellido']}")
        info = self.pestana_info.layout()
        while info.count():
            item = info.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        info.addWidget(StrongBodyLabel("Información personal"))
        info.addWidget(BodyLabel(f"Nombre: {paciente['nombre']} {paciente['apellido']}"))
        info.addWidget(BodyLabel(f"Fecha de nacimiento: {paciente.get('fecha_nacimiento') or '—'}"))
        info.addWidget(BodyLabel(f"Sexo: {paciente.get('sexo') or '—'}"))
        info.addWidget(BodyLabel(f"Teléfono: {paciente.get('telefono') or '—'}"))
        info.addWidget(BodyLabel(f"Correo: {paciente.get('correo') or '—'}"))
        info.addWidget(BodyLabel(f"Observaciones: {paciente.get('observaciones') or '—'}"))
        info.addStretch()
        self.actualizar_mediciones()

    def actualizar_mediciones(self):
        mediciones = repositorio.listar_mediciones(self.paciente_id) if self.paciente_id else []
        self.tabla.setRowCount(len(mediciones))
        for fila, medicion in enumerate(mediciones):
            valores = [medicion.get("fecha", ""), medicion.get("peso", ""),
                       medicion.get("altura_cm", ""), medicion.get("grasa", ""), medicion.get("imc", "")]
            for col, valor in enumerate(valores):
                self.tabla.setItem(fila, col, QTableWidgetItem(str(valor)))

    #Pestaña informacion
    def _crear_pestana_info(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(10, 10, 10, 10)
        l.setSpacing(6)

        l.addWidget(StrongBodyLabel("Información personal"))
        l.addWidget(BodyLabel("Nombre: —"))
        l.addWidget(BodyLabel("Fecha de nacimiento: —"))
        l.addWidget(BodyLabel("Sexo: —"))
        l.addWidget(BodyLabel("Teléfono: —"))
        l.addWidget(BodyLabel("Correo: —"))
        l.addStretch()
        return w

    #Pestaña mediciones
    def _crear_pestana_mediciones(self):
        self.tabla = TableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["Fecha", "Peso", "Estatura", "Grasa", "IMC"])
        self.tabla.verticalHeader().hide()
        self.tabla.setBorderVisible(True)
        self.tabla.setBorderRadius(8)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.tabla.setRowCount(0)
        return self.tabla

    #Cambio de pestaña
    def cambiar_pestana(self, indice):
        self.stack.setCurrentIndex(indice)
        self.btn_ver_reporte.setVisible(indice == 1)
