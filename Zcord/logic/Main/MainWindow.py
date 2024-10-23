from PyQt6 import QtWidgets, QtCore, QtGui
from logic.Main.CompiledGUI.MainWindowGUI import Ui_Zcord
from logic.Main.Friends.SendRequestDialog.AddFreindWindow import AddFriendWindow
from logic.Main.Chat.Message.Message import Message


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, user):
        super(MainWindow, self).__init__()
        self.ui = Ui_Zcord()
        self.ui.setupUi(self)

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint)

        self.ui.pushButton.setIcon(QtGui.QIcon("GUI/icon/forum_400dp_333333_FILL0_wght400_GRAD0_opsz48.svg"))

        self.__user = user

        self.ui.UsersLogo.setText(self.__user.getNickName()[0]) #Установка первой буквы в лого


        self.__friends = {"drug1": 0, "drug2": 0, "DRUG":0, "DRUG2":0,"DRU3G":0,"DRUG4":0,"DRUG5":0,"DRUG6":0,"DRUG=":0,"DRUG7":0,"DRUG8":0} #Брать из json



        self.ui.close.clicked.connect(self.closeWindow)
        self.ui.minimize.clicked.connect(self.on_click_hide)
        self.ui.WindowMode.clicked.connect(self.on_click_fullscreenWindowMode)
        self.ui.AddFriends.clicked.connect(self.addFriend)
        self.ui.ShowFreind.clicked.connect(self.showFriendList)

        self.ui.ScrollFriends.setVisible(False)



    def showFriendList(self):
        if not self.ui.ScrollFriends.isVisible():
            self.ui.ScrollFriends.setVisible(True)

            layoutFinal = QtWidgets.QVBoxLayout()
            layoutFinal.setSpacing(15)
            for friend_nickname in self.__friends.keys():
                layout = QtWidgets.QHBoxLayout()
                layout.setSpacing(10)
                user_logo = QtWidgets.QPushButton()
                user_logo.setFixedHeight(40)
                user_logo.setFixedWidth(40)
                user_logo.setStyleSheet("""background-color:pink;
                                            border-radius:15%;
                                            color:white;
                                            font-size:16px;""")

                user_name = QtWidgets.QLabel()
                user_name.setStyleSheet("""color:white;
                                            font-size:18px;""")
                #user_name.setFixedWidth(100)
                #user_name.setFixedHeight(20)
                user_logo.setText(friend_nickname[0])
                user_name.setText(friend_nickname)

                layout.addWidget(user_logo)
                layout.addWidget(user_name)
                layoutFinal.addLayout(layout)


            widget = QtWidgets.QWidget()

            widget.setLayout(layoutFinal)

            self.ui.ScrollFriends.setMaximumHeight(500)


            self.ui.ScrollFriends.setWidget(widget)
        else:
            self.ui.ScrollFriends.setVisible(False)



    def addFriend(self):
        if not AddFriendWindow.isOpen:
            addFriendsDialog = AddFriendWindow(self.__user)

            addFriendsDialog.show()

            addFriendsDialog.exec()






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

    def on_click_hide(self):
        self.showMinimized()

    def on_click_fullscreenWindowMode(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()




