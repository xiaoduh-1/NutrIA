from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (StrongBodyLabel, SubtitleLabel, BodyLabel, PushButton, PrimaryPushButton,HorizontalSeparator, ScrollArea)


class MenuPersonalizableInterface(QWidget):
    COMIDAS = ["Desayuno", "Colación I", "Comida", "Colación II", "Cena"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("menuPersonalizableInterface")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(10)

        self.lbl_titulo = StrongBodyLabel("Menu personalizable: Juan Pérez")
        layout.addWidget(self.lbl_titulo)

        scroll = ScrollArea()
        scroll.setWidgetResizable(True)
        scroll.enableTransparentBackground()
        contenido = QWidget()
        contenido.setStyleSheet("background: transparent;")
        lista = QVBoxLayout(contenido)
        lista.setSpacing(8)

        self.botones_editar = {}
        for i, comida in enumerate(self.COMIDAS):
            bloque = QHBoxLayout()
            textos = QVBoxLayout()
            textos.setSpacing(4)
            textos.addWidget(SubtitleLabel(comida), alignment=Qt.AlignHCenter)
            for n in range(1, 4):
                textos.addWidget(BodyLabel(f"(Opcion {n})"), alignment=Qt.AlignHCenter)
            bloque.addSpacing(80)
            bloque.addLayout(textos, 1)
            btn = PushButton("Editar")
            bloque.addWidget(btn, alignment=Qt.AlignTop)
            self.botones_editar[comida] = btn
            lista.addLayout(bloque)
            if i < len(self.COMIDAS) - 1:
                lista.addWidget(HorizontalSeparator())

        scroll.setWidget(contenido)
        layout.addWidget(scroll, 1)

        #botones
        botones = QHBoxLayout()
        self.btn_regenerar = PushButton("Regenerar menu")
        self.btn_vista_previa = PrimaryPushButton("Vista previa")
        botones.addWidget(self.btn_regenerar)
        botones.addStretch()
        botones.addWidget(self.btn_vista_previa)
        layout.addLayout(botones)