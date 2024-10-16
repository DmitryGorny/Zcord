import sys
from PyQt6 import QtWidgets, QtCore
from logic.Authorization.AuthorizationWindow.AuthorizationWindow import Ui_Authorization
from logic.Authorization.RegistrationWindow.RegistrationWindowDisplay import ReigstrationWindowDisplay
from logic.Authorization.UserAuthorization import UserAuthorization
from logic.Errors.AuthorizationError import AuthorizationError
from logic.Errors.ErrorDialog.UserError.UserError import UserError
from logic.Errors.ErrorDialog.LoginPassError.LoginPassError import LoginPassError
import json

class AuthoriztionWindowDisplay(QtWidgets.QMainWindow):
    def __init__(self):
        super(AuthoriztionWindowDisplay, self).__init__()
        self.ui = Ui_Authorization()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.ui.Wrapper.setStyleSheet("background-color:#101317;border-radius:40px;")
        self.ui.Wrapper.layout().setSpacing(0)
        self.ui.CloseMinimizeButtons.setStyleSheet("margin-right:10px;background-color:none;")

        self.ui.Password_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

        self.ui.closeWindowButton.clicked.connect(self.on_click_close)
        self.ui.minimizeWindow.clicked.connect(self.on_click_hide)
        self.ui.SignInButton.clicked.connect(self.authorize)
        self.ui.RegistrationStartButton.clicked.connect(self.openRegistrationWindow)



    def authorize(self):
        login = self.ui.Login_input.text()
        password = self.ui.Password_input.text()

        if len(login) == 0:
            self.ui.Login_input.setStyleSheet("""QLineEdit {
                                                        width:250px;
                                                        height:30px;
                                                        border: 2px solid #f5737a;
                                                        border-radius: 10px;
                                                        background-color:#1e1f22;
                                                        font-size:16px;
                                                        color:#808994;
                                                        text-align:left;
                                                        padding-left:27px;;
                                                        }
                                                    """)
            return

        if len(password) == 0:
             self.ui.Password_input.setStyleSheet("""QLineEdit {
                                                        width:250px;
                                                        height:30px;
                                                        border: 2px solid #f5737a;
                                                        border-radius: 10px;
                                                        background-color:#1e1f22;
                                                        font-size:16px;
                                                        color:#808994;
                                                        text-align:left;
                                                        padding-left:27px;;
                                                        }
                                                    """)
             return

        try:
            if UserAuthorization(login, password).login():
                user = {
                    "nickname": login,
                    "password": password
                }
                with open(f"{sys.path[0]}/Resources/user/User.json", "w") as user_json:
                    user_json.write(json.dumps(user))
            else:
                LoginPassErrorBox = LoginPassError()
                LoginPassErrorBox.show()
                LoginPassErrorBox.exec()

        except AuthorizationError as e:
            ErorrBox = UserError()
            ErorrBox.show()
            ErorrBox.exec()


    def on_click_hide(self):
        self.showMinimized()

    def on_click_close(self):
        sys.exit()

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


    def openRegistrationWindow(self):
        Registration = ReigstrationWindowDisplay()

        Registration.show()
        Registration.exec()
