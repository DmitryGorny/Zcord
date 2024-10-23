from PyQt6 import QtWidgets, QtCore, QtGui
from logic.Main.Friends.SendRequestDialog.FriendWindowGUI import Ui_AddFriend
from logic.Main.Friends.FriendAdding import FriendAdding


class AddFriendWindow(QtWidgets.QDialog):
    isOpen = False
    def __init__(self, user):
            QtWidgets.QDialog.__init__(self)

            self.ui = Ui_AddFriend()
            self.ui.setupUi(self)

            self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint)
            self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

            self.ui.minimizeWindow_2.clicked.connect(self.on_click_hide)
            self.ui.closeWindowButton_2.clicked.connect(self.closeWindow)

            self.ui.AddFriend_button.clicked.connect(self.SendFriendshipRequest)

            self.__user = user

            AddFriendWindow.isOpen = True

    def closeWindow(self):
        AddFriendWindow.isOpen = False

        self.close()
    def SendFriendshipRequest(self):
        FriendsADD = FriendAdding(self.__user)

        if len(self.ui.FriendsNick_input.text()) == 0:
            self.ui.FriendsNick_input.setStyleSheet("""QLineEdit {
                                                         width:250px;
                                                        height:30px;
                                                        border: 2px solid #f5737a;
                                                        border-radius: 10px;
                                                        background-color:#323338;
                                                        font-size:16px;
                                                        color:#808994;
                                                        text-align:left;
                                                        padding-left:15px;
                                                        }""")

        isRequestSent = FriendsADD.sendRequest(self.ui.FriendsNick_input.text())

        if isRequestSent:
            self.ui.Status.setIcon(QtGui.QIcon("GUI/icon/done_outline_40dp_78A75A_FILL0_wght400_GRAD0_opsz40.svg"))
            self.ui.Status.setIconSize(QtCore.QSize(20, 20))
        else:
            self.ui.Status.setIcon(QtGui.QIcon("GUI/icon/warning_40dp_BB271A_FILL0_wght400_GRAD0_opsz40.svg"))
            self.ui.Status.setIconSize(QtCore.QSize(20, 20))

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
