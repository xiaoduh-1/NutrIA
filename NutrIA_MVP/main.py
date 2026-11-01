import os
os.environ["QT_API"] = "pyside6"

import sys
from PySide6.QtWidgets import QApplication
from ui.vistas.componentes import LoginWindow, pantallaPrincipal


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventanas = {"login": None, "principal": None}

    def mostrar_login():
        ventanas["login"] = LoginWindow()
        ventanas["login"].login_exitoso.connect(abrir_principal)
        ventanas["login"].show()

    def abrir_principal():
        ventanas["principal"] = pantallaPrincipal()
        ventanas["principal"].sesion_cerrada.connect(cerrar_sesion)
        ventanas["principal"].show()
        ventanas["login"].close()

    def cerrar_sesion():
        ventanas["principal"].close()
        mostrar_login()

    mostrar_login()
    sys.exit(app.exec())
