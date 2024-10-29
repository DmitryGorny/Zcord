import queue

from PyQt6 import QtWidgets, QtCore, QtGui
from logic.Main.CompiledGUI.MainWindowGUI import Ui_Zcord
from logic.Main.Friends.SendRequestDialog.AddFreindWindow import AddFriendWindow
from logic.Main.Chat.ChatClass.Chat import Chat
from logic.db_handler.db_handler import db_handler
from logic.Message import message_client
from logic.Main.CompiledGUI.Helpers.ClickableFrame import ClikableFrame
import threading
import json

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, user):
        super(MainWindow, self).__init__()
        self.ui = Ui_Zcord()
        self.ui.setupUi(self)

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

        self.ui.pushButton.setIcon(QtGui.QIcon("GUI/icon/forum_400dp_333333_FILL0_wght400_GRAD0_opsz48.svg"))

        self.__user = user

        self.ui.UsersLogo.setText(self.__user.getNickName()[0]) #Установка первой буквы в лого

        self.__friends = {}

        self.__chats = []

        self.getFriends()
        self.createChats()

        self.ui.close.clicked.connect(self.closeWindow)
        self.ui.minimize.clicked.connect(self.on_click_hide)
        self.ui.WindowMode.clicked.connect(self.on_click_fullscreenWindowMode)
        self.ui.AddFriends.clicked.connect(self.addFriend)
        self.ui.ShowFreind.clicked.connect(self.showFriendList)

        self.ui.ScrollFriends.setVisible(False)
        self.call_chat()

        self.ui.horizontalFrame.mouseMoveEvent = self.MoveWindow

        self.pressing = False

    def mousePressEvent(self, event):
            self.start = self.mapToGlobal(event.pos())
            self.pressing = True


    def MoveWindow(self, event):
        if self.isMaximized():
            return

        if self.pressing:
            self.end = self.mapToGlobal(event.pos())
            movement = self.end-self.start
            self.move(self.mapToGlobal(movement))
            self.start = self.end



    def getFriends(self):
        with open("Resources/frineds/friends.json", "r") as Frineds_json:

            friendsDict = json.load(Frineds_json)

            self.__friends = friendsDict.copy()

            db = db_handler("26.181.96.20", "Dmitry", "gfggfggfg3D-", "zcord", "friendship")

            friends = db.getDataFromTableColumn("*", f"WHERE friend_one_id = '{self.__user.getNickName()}' AND status = 2 OR friend_two_id = '{self.__user.getNickName()}' AND status = 2")

            for friendArr in friends:
                if friendArr[1] not in self.__friends and friendArr[2] not in self.__friends:
                    if friendArr[1] != self.__user.getNickName():
                        key = friendArr[1]
                    else:
                        key = friendArr[2]

                    self.__friends[key] = {
                        "chat_id": friendArr[0],
                    }

            Frineds_json.close()



    def createChats(self):
        for friend in self.__friends.keys():
            self.__chats.append(Chat(self.__friends[friend]["chat_id"], friend, self.__user))

    def call_chat(self):
        chat_ids = []
        for chat in self.__chats:
            chat_ids.append(str(chat.getChatId()))
        queueToSend = queue.Queue()
        queueToSend.put(self.__chats)
        self.__client = message_client.call(self.__user.getNickName(), chat_ids, self.__user, queueToSend)

    def showFriendList(self):
        if not self.ui.ScrollFriends.isVisible():
            self.ui.ScrollFriends.setVisible(True)

            layoutFinal = QtWidgets.QVBoxLayout()
            layoutFinal.setSpacing(5)
            layoutFinal.setContentsMargins(0,0,0,0)
            for friend_nickname in self.__friends.keys():
                QFr = ClikableFrame(friend_nickname)
                QFr.clicked.connect(self.chooseChat)
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
                                            font-size:18px;
                                            border:none;
                                            background-color:none;""")
                user_logo.setText(friend_nickname[0])
                user_name.setText(friend_nickname)

                layout.addWidget(user_logo)
                layout.addWidget(user_name)


                QFr.setLayout(layout)
                QFr.setStyleSheet("""QFrame:hover { 
                                        border-radius:15%;
                                        background-color:rgba(0, 0, 0, 0.26);}
                                        QFrame {
                                        margin:0;
                                        }""")
                QFr.setFixedWidth(250)
                QFr.setFixedHeight(70)
                QFr.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
                layoutFinal.addWidget(QFr)

            widget = QtWidgets.QWidget()

            widget.setLayout(layoutFinal)

            self.ui.ScrollFriends.setMaximumHeight(350)

            self.ui.ScrollFriends.setStyleSheet("""QScrollArea {
                                                            border:none;
                                                        }
                                                        
                                                        QScrollBar:vertical {
                                                            border:none;
                                                            width:10px;
                                                            height:20px;
                                                            
                                                        }
                                                        
                                                         QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical
                                                         {
                                                             heigth:0;
                                                         }
                                                         QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical
                                                         {
                                                             background: none;
                                                         }
                                                         QScrollBar::add-line:vertical {
                                                                height: 0px;
                                                         }
                                                                
                                                                QScrollBar::sub-line:vertical {
                                                                height: 0px;
                                                         }
                                                         QScrollBar::handle:vertical {
                                                            background: orange;
                                                            min-height:10px;
                                                            border-radius: 5px;
                                                         }""")


            self.ui.ScrollFriends.setWidget(widget)
        else:
            self.ui.ScrollFriends.setVisible(False)


    def addFriend(self):
        if not AddFriendWindow.isOpen:
            addFriendsDialog = AddFriendWindow(self.__user)

            addFriendsDialog.show()

            addFriendsDialog.exec()

    def chooseChat(self):
        sender = self.sender()

        chat = list(filter(lambda x: x.getNickName() == sender.text, self.__chats))[0]

        chat_id = chat.getChatId()

        message_client.MainInterface.change_chat(chat_id, self.__user.getNickName())

        chat.ui.MAIN_ChatLayout.setContentsMargins(0,0,0,0)
        self.ui.stackedWidget.addWidget(chat.ui.MAIN)
        self.ui.stackedWidget.setCurrentWidget(chat.ui.MAIN)


    def closeWindow(self):
        #with open("Resources/frineds/friends.json", "w") as Frineds_json:
            #Frineds_json.write(json.dumps(self.__friends))
        self.close()

        self.__client.close()







    def mouseReleaseEvent(self, event):
        self.pressing = False

    def on_click_hide(self):
        self.showMinimized()

    def on_click_fullscreenWindowMode(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def updateWindowMargins(self):
        if self.isMaximized():
            screen_geometry = QtWidgets.QApplication.primaryScreen().availableGeometry()
            self.setGeometry(screen_geometry)

    def resizeEvent(self, event):
        self.updateWindowMargins()
        super().resizeEvent(event)





