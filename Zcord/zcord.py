from PyQt6 import QtCore, QtWidgets
from logic.Authorization.AuthorizationWindow.AuthorizationWindowDisplay import AuthoriztionWindowDisplay
from logic.Main.MainWindow import MainWindow
from logic.Authorization.User.User import User
import sys
if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    app = QtWidgets.QApplication(sys.argv)
    AuthorizationWindow = AuthoriztionWindowDisplay()


    AuthorizationWindow.show()
    AuthorizationWindow.exec()

    Main = MainWindow(AuthorizationWindow.getUser())
    Main.show()



    app.exec()





