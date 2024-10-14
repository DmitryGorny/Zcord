import sys
print(sys.executable)
from PyQt6 import QtWidgets, QtCore
from logic.Authorization.AuthorizationWindow.AuthorizationWindow import Ui_Authorization
from logic.Authorization.UserAuthorization import UserAuthorization
from logic.Errors.AuthorizationError import AuthorizationError

class AuthoriztionWindowDisplay(QtWidgets.QMainWindow):
    def __init__(self):
        super(AuthoriztionWindowDisplay, self).__init__()
        self.ui = Ui_Authorization()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint | QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.ui.Wrapper.setStyleSheet("background-color:#101317;border-radius:40px;")
        self.ui.closeWindowButton.clicked.connect(self.on_click_close)
        self.ui.minimizeWindow.clicked.connect(self.on_click_hide)
        self.ui.SignInButton.clicked.connect(self.authorize)

    def authorize(self):
        login = self.ui.Login_input.text()
        password = self.ui.Password_input.text()

        if len(login) == 0:
            self.ui.Login_input.styleSheet("""QLineEdit {
                                                        width:250px;
                                                        height:30px;
                                                        border: 2px solid red;
                                                        border-radius: 10px;
                                                        background-color:#1e1f22;
                                                        font-size:16px;
                                                        color:#808994;
                                                        text-align:left;
                                                        padding-left:27px;;
                                                        }
                                                    """)

        try:
            UserAuthorization(login, password).login()
        except AuthorizationError as e:
            print(e)


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
