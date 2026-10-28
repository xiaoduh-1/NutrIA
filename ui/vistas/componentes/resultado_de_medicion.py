from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout
from qfluentwidgets import (StrongBodyLabel, TitleLabel, BodyLabel, SubtitleLabel, CardWidget,PrimaryPushButton)


class ResultadoMedicionInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("resultadoMedicionInterface")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(12)

        #Paciente y fecha
        encabezado = QHBoxLayout()
        self.lbl_paciente = StrongBodyLabel("Paciente: Juan Pérez")
        self.lbl_fecha = BodyLabel("10/10/2020")
        encabezado.addWidget(self.lbl_paciente)
        encabezado.addStretch()
        encabezado.addWidget(self.lbl_fecha)
        layout.addLayout(encabezado)

        layout.addWidget(TitleLabel("Resultado de la medición"), alignment=Qt.AlignHCenter)

        #Tarjetas de resultados
        resultados = [
            ("Peso:", "70"),
            ("Grasa:", "10%"),
            ("Masa Muscular:", "20%"),
            ("IMC:", "100"),
            ("Agua:", "10%"),
            ("Metabolismo:", "1,850 kcal"),
        ]

        grid = QGridLayout()
        grid.setHorizontalSpacing(30)
        grid.setVerticalSpacing(8)
        self.valores = {}

        for i, (titulo, valor) in enumerate(resultados):
            fila, col = divmod(i, 3)
            bloque = QVBoxLayout()
            bloque.addWidget(BodyLabel(titulo))

            tarjeta = CardWidget()
            tarjeta.setFixedHeight(60)
            tarjeta_layout = QVBoxLayout(tarjeta)
            lbl_valor = SubtitleLabel(valor)
            lbl_valor.setAlignment(Qt.AlignCenter)
            tarjeta_layout.addWidget(lbl_valor)
            bloque.addWidget(tarjeta)

            grid.addLayout(bloque, fila, col)
            self.valores[titulo] = lbl_valor

        layout.addLayout(grid)
        layout.addStretch()

        #Boton
        inferior = QHBoxLayout()
        inferior.addStretch()
        self.btn_continuar = PrimaryPushButton("Continuar")
        inferior.addWidget(self.btn_continuar)
        layout.addLayout(inferior)