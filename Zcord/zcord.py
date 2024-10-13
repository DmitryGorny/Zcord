from PyQt6 import QtCore, QtWidgets
from logic.Authorization.Authorization import Authorization
import sys
if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    app = QtWidgets.QApplication(sys.argv)
    AuthorizationWindow = Authorization()

    AuthorizationWindow.show()
    sys.exit(app.exec())
