import os
os.environ["QT_API"] = "pyside6"
import sys
from PySide6.QtWidgets import QApplication
from ui.vistas.componentes.login import LoginWindow
from ui.vistas.componentes import pantallaPrincipal

if __name__ == "__main__":
    app = QApplication(sys.argv)

    login = LoginWindow()
    ventana_principal = None

    def abrir_principal():
        global ventana_principal
        ventana_principal = pantallaPrincipal()
        ventana_principal.show()
        login.close()
    
    login.login_exitoso.connect(abrir_principal)
    login.show()

    sys.exit(app.exec())