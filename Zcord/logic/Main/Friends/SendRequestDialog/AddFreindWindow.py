from PyQt6 import QtWidgets, QtCore, QtGui
from logic.Main.Friends.SendRequestDialog.FriendWindowGUI import Ui_AddFriend

class AddFriendWindow(QtWidgets.QDialog):
    def __init__(self):
        super(AddFriendWindow, self).__init__()

        self.ui = Ui_AddFriend()
        self.ui.setupUi(self)

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.ui.minimizeWindow_2.clicked.connect(self.on_click_hide)
        self.ui.closeWindowButton_2.clicked.connect(self.close)

    def on_click_hide(self):
        self.showMinimized()

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
