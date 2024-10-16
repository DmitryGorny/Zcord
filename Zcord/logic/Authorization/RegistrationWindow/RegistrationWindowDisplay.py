import sys
from PyQt6 import QtWidgets, QtCore, QtGui
from logic.Authorization.RegistrationWindow.RegistrationWindow import Ui_Dialog
from logic.Authorization.UserRegistration import UserRegistration
from logic.Errors.SuccessDialog.SuccessRegister.SuccessRegister import SuccessRegister
from logic.Errors.ErrorDialog.RegistrationError.RegistrationError import RegistrationError

class ReigstrationWindowDisplay(QtWidgets.QDialog):
    def __init__(self):
        super(ReigstrationWindowDisplay, self).__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.Wrapper.setStyleSheet("background-color:none;")
        self.ui.Menu.setStyleSheet("background-color:rgba(38,40,45,255);border-radius:50px;")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.ui.SignInFromRegistrationButton.clicked.connect(self.closeWindow)
        self.ui.RegistrationButton.clicked.connect(self.register)

        self.ui.Password_input_.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

    def closeWindow(self):
        self.close()

    def mousePressEvent(self, event):
        self.start = self.mapToGlobal(event.pos())
        self.pressing = True

    def mouseMoveEvent(self, event):
        if self.pressing:
            self.end = self.mapToGlobal(event.pos())
            self.movement = self.end-self.start
            self.move(self.mapToGlobal(self.movement))
            self.start = self.end

    def mouseReleaseEvent(self, event):
        self.pressing = False

    def register(self):
        login = self.ui.login_input.text()
        name = self.ui.Name_input.text()
        password = self.ui.Password_input_.text()

        if len(name) == 0:
            self.ui.Name_input.setStyleSheet("""QLineEdit{ 
                                                width:250px;
                                                height:30px;
                                                border: 2px solid #f5737a;
                                                border-radius: 10px;
                                                background-color:#1e1f22;
                                                font-size:16px;
                                                color:#808994;
                                                text-align:left;
                                                padding-left:27px;
                                                }""")
            return

        if len(login) == 0:
            self.ui.login_input.setStyleSheet("""QLineEdit{ 
                                 width:250px;
                                 height:30px;
                                 border: 2px solid #f5737a;
                                 border-radius: 10px;
                                 background-color:#1e1f22;
                                 font-size:16px;
                                 color:#808994;
                                 text-align:left;
                                 padding-left:27px;
                                        }""")
            return

        if len(password) == 0:
            self.ui.Password_input_.setStyleSheet("""QLineEdit{ 
                                 width:250px;
                                 height:30px;
                                 border: 2px solid #f5737a;
                                 border-radius: 10px;
                                 background-color:#1e1f22;
                                 font-size:16px;
                                 color:#808994;
                                 text-align:left;
                                 padding-left:27px;
                                        }""")
            return


        if UserRegistration(name, login, password).register():
            success = SuccessRegister()
            success.show()
            success.exec()

            self.close()
        else:
            error = RegistrationError()
            error.show()
            error.exec()



