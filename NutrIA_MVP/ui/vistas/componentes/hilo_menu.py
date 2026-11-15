from PySide6.QtCore import QThread, Signal
from servicios.generador_menu import generar_menu


class HiloGenerarMenu(QThread):
    """Ejecuta la generación en segundo plano. No toca widgets: solo emite señales."""
    terminado = Signal(str, dict)   # paciente_id, resultado
    fallo = Signal(str)

    def __init__(self, paciente_id, paciente, medicion, objetivos, parent=None):
        super().__init__(parent)
        self.paciente_id = paciente_id
        self.paciente = paciente
        self.medicion = medicion
        self.objetivos = objetivos

    def run(self):
        try:
            resultado = generar_menu(self.paciente, self.medicion, self.objetivos)
            self.terminado.emit(self.paciente_id, resultado)
        except Exception as error:
            self.fallo.emit(str(error))
