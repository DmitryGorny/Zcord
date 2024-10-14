from PyQt6 import QtCore, QtWidgets
from logic.Authorization.AuthorizationWindow.AuthorizationWindowDisplay import AuthoriztionWindowDisplay
import sys
if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    app = QtWidgets.QApplication(sys.argv)
    AuthorizationWindow = AuthoriztionWindowDisplay()

    AuthorizationWindow.show()
    sys.exit(app.exec())
