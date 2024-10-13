from PyQt6 import QtWidgets, QtCore
from logic.Authorization.AuthorizationWindow import Ui_Authorization
class Authorization(QtWidgets.QMainWindow):
    def __init__(self):
        super(Authorization, self).__init__()
        self.ui = Ui_Authorization()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint | QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.ui.Wrapper.setStyleSheet("background-color:#101317;border-radius:40px;")

        self.ui.SignInButton.clicked.connect(self.authorize)

    def authorize(self):
        pass

    def mousePressEvent(self, event):
        self.offset = event.pos()

    def mouseMoveEvent(self, event):
        x=event.pos().x()
        y=event.pos().y()
        x_w = self.offset.x()
        y_w = self.offset.y()
        self.move(x + x_w , y + y_w)
