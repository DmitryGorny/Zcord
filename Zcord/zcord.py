from PyQt6 import QtCore, QtWidgets
from logic.Authorization.AuthorizationWindow.AuthorizationWindowDisplay import AuthoriztionWindowDisplay
from logic.Main.MainWindow import MainWindow
import sys


if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    app = QtWidgets.QApplication(sys.argv)
    app.keyPressEvent = None
    AuthorizationWindow = AuthoriztionWindowDisplay()

    AuthorizationWindow.show()
    AuthorizationWindow.exec()

    Main = MainWindow(AuthorizationWindow.getUser())
    Main.show()

    app.exec()





