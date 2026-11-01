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
        self.lbl_paciente = StrongBodyLabel("Paciente: —")
        self.lbl_fecha = BodyLabel("Fecha: —")
        encabezado.addWidget(self.lbl_paciente)
        encabezado.addStretch()
        encabezado.addWidget(self.lbl_fecha)
        layout.addLayout(encabezado)

        self.lbl_objetivo = BodyLabel("Objetivo: —")
        self.lbl_motivo = BodyLabel("Motivo: —")
        self.lbl_actividad = BodyLabel("Actividad física: —")
        layout.addWidget(self.lbl_objetivo)
        layout.addWidget(self.lbl_motivo)
        layout.addWidget(self.lbl_actividad)

        layout.addWidget(TitleLabel("Resultado de la medición"), alignment=Qt.AlignHCenter)

        #Tarjetas de resultados
        resultados = [
            ("Peso:", "—"),
            ("Grasa:", "—"),
            ("Masa Muscular:", "—"),
            ("IMC:", "—"),
            ("Agua:", "—"),
            ("Calorías:", "— kcal"),
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
            tarjeta.setMinimumHeight(60)
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

    def limpiar(self, nombre_paciente="—"):
        self.lbl_paciente.setText(f"Paciente: {nombre_paciente}")
        self.lbl_fecha.setText("Fecha: —")
        self.lbl_objetivo.setText("Objetivo: —")
        self.lbl_motivo.setText("Motivo: —")
        self.lbl_actividad.setText("Actividad física: —")
        for etiqueta, valor in self.valores.items():
            valor.setText("— kcal" if etiqueta == "Calorías:" else "—")
