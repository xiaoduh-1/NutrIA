from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,QTableWidgetItem, QHeaderView)
from qfluentwidgets import (TitleLabel, BodyLabel, StrongBodyLabel, Pivot, TableWidget,PushButton, PrimaryPushButton, FluentIcon)


class FichaPacienteInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("fichaPacienteInterface")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(12)

        #Titulo
        self.titulo = TitleLabel("Paciente: Juan Pérez")
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

    #Pestaña informacion
    def _crear_pestana_info(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(10, 10, 10, 10)
        l.setSpacing(6)

        l.addWidget(StrongBodyLabel("Información personal"))
        l.addWidget(BodyLabel("Nombre: Juan Pérez"))
        l.addWidget(BodyLabel("Edad: 20"))
        l.addWidget(BodyLabel("Sexo: ese we"))
        l.addWidget(BodyLabel("Teléfono: 3311226655"))
        l.addSpacing(10)
        l.addWidget(BodyLabel("Objetivo: Pérdida de peso"))
        l.addStretch()
        return w

    #Pestaña mediciones
    def _crear_pestana_mediciones(self):
        self.tabla = TableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["Fecha", "Peso", "Grasa", "IMC"])
        self.tabla.verticalHeader().hide()
        self.tabla.setBorderVisible(True)
        self.tabla.setBorderRadius(8)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        mediciones = [
            ("00/00/0000", "50", "20", "123"),
            ("11/11/1111", "50", "20", "123"),
            ("22/22/2222", "50", "20", "123"),
            ("33/33/3333", "50", "20", "123"),
            ("44/44/4444", "50", "20", "123"),
        ]
        self.tabla.setRowCount(len(mediciones))
        for fila, datos in enumerate(mediciones):
            for col, valor in enumerate(datos):
                self.tabla.setItem(fila, col, QTableWidgetItem(valor))
        return self.tabla

    #Cambio de pestaña
    def cambiar_pestana(self, indice):
        self.stack.setCurrentIndex(indice)
        self.btn_ver_reporte.setVisible(indice == 1)