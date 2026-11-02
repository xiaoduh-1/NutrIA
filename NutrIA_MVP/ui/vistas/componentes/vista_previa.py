from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (TitleLabel, SubtitleLabel, StrongBodyLabel, BodyLabel, CardWidget,PushButton, PrimaryPushButton, FluentIcon)


class VistaPreviaInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("vistaPreviaInterface")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(10)

        #Reporte
        hoja = CardWidget()
        hoja_layout = QVBoxLayout(hoja)
        hoja_layout.setContentsMargins(24, 16, 24, 16)
        hoja_layout.setSpacing(8)

        hoja_layout.addWidget(TitleLabel("NutrIA"), alignment=Qt.AlignHCenter)
        hoja_layout.addWidget(SubtitleLabel("Reporte nutricional"), alignment=Qt.AlignHCenter)

        datos = QHBoxLayout()
        izq = QVBoxLayout()
        izq.addWidget(BodyLabel("Paciente: —"))
        izq.addWidget(BodyLabel("Fecha: —"))
        izq.addStretch()

        der = QVBoxLayout()
        der.addWidget(StrongBodyLabel("Resultado de la medición:"))
        self.lbl_peso = BodyLabel("Peso: — kg")
        self.lbl_grasa = BodyLabel("Grasa: —%")
        der.addWidget(self.lbl_peso)
        der.addWidget(self.lbl_grasa)
        der.addSpacing(8)
        der.addWidget(StrongBodyLabel("Objetivos nutricionales:"))
        der.addWidget(BodyLabel("— kcal"))

        datos.addLayout(izq, 1)
        datos.addLayout(der, 1)
        hoja_layout.addLayout(datos)

        hoja_layout.addWidget(StrongBodyLabel("Menu semanal"))
        self.lbl_menu = BodyLabel("(Aquí se mostrará el menu semanal)")
        hoja_layout.addWidget(self.lbl_menu)
        hoja_layout.addStretch()

        layout.addWidget(hoja, 1)
        self.lbl_paciente = izq.itemAt(0).widget()
        self.lbl_fecha = izq.itemAt(1).widget()
        self.lbl_calorias = der.itemAt(5).widget()

        #Botones
        botones = QHBoxLayout()
        self.btn_regresar = PushButton(FluentIcon.LEFT_ARROW, "Regresar")
        self.btn_exportar = PrimaryPushButton(FluentIcon.SAVE, "Exportar PDF")
        botones.addWidget(self.btn_regresar)
        botones.addStretch()
        botones.addWidget(self.btn_exportar)
        layout.addLayout(botones)

    def cargar_reporte(self, paciente, medicion, objetivos, menu):
        self.lbl_paciente.setText(f"Paciente: {paciente['nombre']} {paciente['apellido']}")
        self.lbl_fecha.setText(f"Fecha: {medicion.get('fecha', '—')}")
        self.lbl_peso.setText(f"Peso: {medicion.get('peso', '—')} kg")
        self.lbl_grasa.setText(f"Grasa: {medicion.get('grasa', '—')}%")
        self.lbl_calorias.setText(f"{objetivos.get('calorias') or '—'} kcal")
        lineas = []
        for comida, alimentos in menu.items():
            elementos = []
            for alimento in alimentos:
                if isinstance(alimento, dict):
                    nombre = alimento.get("nombre", "")
                    porcion = alimento.get("porcion", "")
                else:
                    nombre, porcion = alimento
                elementos.append(f"{nombre} ({porcion})")
            lineas.append(f"{comida}: " + ", ".join(elementos))
        self.lbl_menu.setText("\n".join(lineas) if lineas else "(Sin menú)")
