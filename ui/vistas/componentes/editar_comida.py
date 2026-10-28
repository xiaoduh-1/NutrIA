from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QTableWidgetItem, QHeaderView
from qfluentwidgets import (TitleLabel, SubtitleLabel, BodyLabel, TableWidget, TransparentPushButton,PushButton, PrimaryPushButton, HorizontalSeparator, FluentIcon)


class EditarComidaInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("editarComidaInterface")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(10)

        layout.addWidget(TitleLabel("Editar comida"))
        self.lbl_comida = SubtitleLabel("Desayuno:")
        layout.addWidget(self.lbl_comida)

        self.tabla = TableWidget()
        self.tabla.setColumnCount(2)
        self.tabla.setHorizontalHeaderLabels(["Alimento", "Porción"])
        self.tabla.verticalHeader().hide()
        self.tabla.setBorderVisible(True)
        self.tabla.setBorderRadius(8)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        alimentos = [("Huevos", "2 piezas"), ("Tortillas", "2 piezas"), ("Verduras", "100 gr")]
        self.tabla.setRowCount(len(alimentos))
        for fila, (alimento, porcion) in enumerate(alimentos):
            self.tabla.setItem(fila, 0, QTableWidgetItem(alimento))
            self.tabla.setItem(fila, 1, QTableWidgetItem(porcion))
        layout.addWidget(self.tabla)

        self.btn_agregar_alimento = TransparentPushButton(FluentIcon.ADD, "Agregar alimento")
        layout.addWidget(self.btn_agregar_alimento)

        layout.addWidget(HorizontalSeparator())

        #Totales
        totales = QGridLayout()
        totales.setHorizontalSpacing(40)
        totales.addWidget(BodyLabel("Calorías:"), 0, 0)
        totales.addWidget(BodyLabel("550 kcal"), 0, 1)
        totales.addWidget(BodyLabel("Carbohidratos:"), 0, 2)
        totales.addWidget(BodyLabel("50 gr"), 0, 3)
        totales.addWidget(BodyLabel("Proteínas:"), 1, 2)
        totales.addWidget(BodyLabel("100 gr"), 1, 3)
        totales.addWidget(BodyLabel("Grasas:"), 2, 2)
        totales.addWidget(BodyLabel("20 gr"), 2, 3)
        totales.setColumnStretch(4, 1)
        layout.addLayout(totales)

        layout.addStretch()

        #Botones
        botones = QHBoxLayout()
        self.btn_cancelar = PushButton("Cancelar")
        self.btn_guardar = PrimaryPushButton(FluentIcon.SAVE, "Guardar")
        botones.addWidget(self.btn_cancelar)
        botones.addStretch()
        botones.addWidget(self.btn_guardar)
        layout.addLayout(botones)