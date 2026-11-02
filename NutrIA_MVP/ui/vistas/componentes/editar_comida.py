from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QTableWidgetItem,
    QHeaderView, QInputDialog, QMessageBox,
)
from qfluentwidgets import (TitleLabel, SubtitleLabel, BodyLabel, TableWidget, TransparentPushButton,PushButton, PrimaryPushButton, HorizontalSeparator, FluentIcon)
from datos import repositorio


class EditarComidaInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("editarComidaInterface")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(10)

        layout.addWidget(TitleLabel("Editar comida"))
        self.lbl_comida = SubtitleLabel("Comida:")
        layout.addWidget(self.lbl_comida)

        self.tabla = TableWidget()
        self.tabla.setColumnCount(2)
        self.tabla.setHorizontalHeaderLabels(["Alimento", "Porción"])
        self.tabla.verticalHeader().hide()
        self.tabla.setBorderVisible(True)
        self.tabla.setBorderRadius(8)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        alimentos = []
        self.tabla.setRowCount(len(alimentos))
        for fila, (alimento, porcion) in enumerate(alimentos):
            self.tabla.setItem(fila, 0, QTableWidgetItem(alimento))
            self.tabla.setItem(fila, 1, QTableWidgetItem(porcion))
        layout.addWidget(self.tabla)

        self.btn_agregar_catalogo = PrimaryPushButton(FluentIcon.SEARCH, "Buscar en catálogo")
        layout.addWidget(self.btn_agregar_catalogo)
        self.btn_agregar_catalogo.clicked.connect(self.agregar_desde_catalogo)

        self.btn_agregar_alimento = TransparentPushButton(FluentIcon.ADD, "Agregar alimento manual")
        layout.addWidget(self.btn_agregar_alimento)
        self.btn_agregar_alimento.clicked.connect(lambda: self.tabla.insertRow(self.tabla.rowCount()))

        layout.addWidget(HorizontalSeparator())

        #Totales
        totales = QGridLayout()
        totales.setHorizontalSpacing(40)
        totales.addWidget(BodyLabel("Calorías:"), 0, 0)
        totales.addWidget(BodyLabel("— kcal"), 0, 1)
        totales.addWidget(BodyLabel("Carbohidratos:"), 0, 2)
        totales.addWidget(BodyLabel("— gr"), 0, 3)
        totales.addWidget(BodyLabel("Proteínas:"), 1, 2)
        totales.addWidget(BodyLabel("— gr"), 1, 3)
        totales.addWidget(BodyLabel("Grasas:"), 2, 2)
        totales.addWidget(BodyLabel("— gr"), 2, 3)
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

    def cargar_comida(self, nombre, alimentos):
        self.lbl_comida.setText(f"{nombre}:")
        self.tabla.setRowCount(len(alimentos))
        for fila, alimento in enumerate(alimentos):
            if isinstance(alimento, dict):
                nombre_alimento = alimento.get("nombre", "")
                porcion = alimento.get("porcion", "")
                alimento_id = alimento.get("alimento_id")
                cantidad = alimento.get("cantidad_base")
                unidad = alimento.get("unidad_base")
            else:
                nombre_alimento, porcion = alimento
                alimento_id = cantidad = unidad = None
            celda_nombre = QTableWidgetItem(nombre_alimento)
            celda_porcion = QTableWidgetItem(porcion)
            if alimento_id:
                celda_nombre.setData(Qt.UserRole, alimento_id)
                celda_porcion.setData(Qt.UserRole, cantidad)
                celda_porcion.setData(Qt.UserRole + 1, unidad)
                celda_nombre.setFlags(celda_nombre.flags() & ~Qt.ItemIsEditable)
                celda_porcion.setFlags(celda_porcion.flags() & ~Qt.ItemIsEditable)
            self.tabla.setItem(fila, 0, celda_nombre)
            self.tabla.setItem(fila, 1, celda_porcion)

    def agregar_desde_catalogo(self):
        termino, aceptado = QInputDialog.getText(
            self, "Buscar alimento", "Escribe el nombre o parte del nombre:")
        if not aceptado or not termino.strip():
            return
        try:
            resultados = repositorio.buscar_alimentos(termino, limite=100)
        except Exception as error:
            QMessageBox.critical(self, "Catálogo de alimentos", f"No se pudo consultar el catálogo:\n{error}")
            return
        if not resultados:
            QMessageBox.information(self, "Sin resultados", "No se encontraron alimentos con esa búsqueda.")
            return

        opciones = []
        for alimento in resultados:
            marca = " [DEMO]" if alimento["es_dato_prueba"] else ""
            opciones.append(
                f"{alimento['nombre']} — {alimento['categoria']} — "
                f"{alimento['calorias_100']:g} kcal/100 {alimento['unidad_base']}{marca}"
            )
        opcion, aceptado = QInputDialog.getItem(
            self, "Seleccionar alimento", "Alimento del catálogo:", opciones, 0, False)
        if not aceptado:
            return
        alimento = resultados[opciones.index(opcion)]
        cantidad, aceptado = QInputDialog.getDouble(
            self,
            "Cantidad del alimento",
            f"Cantidad en {alimento['unidad_base']} para {alimento['nombre']}:",
            100.0, 0.1, 5000.0, 1,
        )
        if not aceptado:
            return

        fila = self.tabla.rowCount()
        self.tabla.insertRow(fila)
        celda_nombre = QTableWidgetItem(alimento["nombre"])
        celda_nombre.setData(Qt.UserRole, alimento["id"])
        celda_nombre.setToolTip(
            f"{alimento['categoria']} · {alimento['fuente']}" +
            (" · Dato ilustrativo de prueba" if alimento["es_dato_prueba"] else "")
        )
        celda_nombre.setFlags(celda_nombre.flags() & ~Qt.ItemIsEditable)
        celda_porcion = QTableWidgetItem(f"{cantidad:g} {alimento['unidad_base']}")
        celda_porcion.setData(Qt.UserRole, cantidad)
        celda_porcion.setData(Qt.UserRole + 1, alimento["unidad_base"])
        celda_porcion.setFlags(celda_porcion.flags() & ~Qt.ItemIsEditable)
        self.tabla.setItem(fila, 0, celda_nombre)
        self.tabla.setItem(fila, 1, celda_porcion)

    def obtener_alimentos(self):
        alimentos = []
        for fila in range(self.tabla.rowCount()):
            alimento = self.tabla.item(fila, 0)
            porcion = self.tabla.item(fila, 1)
            nombre = alimento.text().strip() if alimento else ""
            cantidad = porcion.text().strip() if porcion else ""
            if nombre and cantidad:
                alimento_id = alimento.data(Qt.UserRole) if alimento else None
                alimentos.append({
                    "alimento_id": alimento_id,
                    "nombre": nombre,
                    "porcion": cantidad,
                    "cantidad_base": porcion.data(Qt.UserRole) if porcion else None,
                    "unidad_base": porcion.data(Qt.UserRole + 1) if porcion else None,
                })
        return alimentos
