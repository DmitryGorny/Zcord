import queue
from PyQt6 import QtWidgets, QtCore, QtGui
from logic.Main.CompiledGUI.MainWindowGUI import Ui_Zcord
from logic.Main.Friends.SendRequestDialog.AddFreindWindow import AddFriendWindow
from logic.Main.Chat.ChatClass.Chat import Chat
from logic.db_handler.db_handler import db_handler
from logic.Message import message_client
from logic.Main.CompiledGUI.Helpers.ClickableFrame import ClikableFrame
from logic.Main.Parameters.Params_Window import ParamsWindow
from logic.Main.Voice_main.VoiceParamsClass import VoiceParamsClass
import threading
import json
import plyer

from PyQt6.QtGui import QIcon
from logic.Main.miniProfile.MiniProfile import MiniProfile, Overlay
from logic.Main.CompiledGUI.Helpers.ChatInList import ChatInList

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, user):
        super(MainWindow, self).__init__()
        self.ui = Ui_Zcord()
        self.ui.setupUi(self)

        self.voicepr = VoiceParamsClass()

        self.parameters = ParamsWindow(self.ui, self.voicepr)
        self.ui.stackedWidget.addWidget(self.parameters.ui_pr.MAIN)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

        self.ui.pushButton.setIcon(QIcon("GUI/icon/forum_400dp_333333_FILL0_wght400_GRAD0_opsz48.svg"))

        self.__user = user

        self.ui.UsersLogo.setText(self.__user.getNickName()[0]) #Установка первой буквы в лого
        self.ui.UsersLogo.clicked.connect(self.showProfile)

        self.__friends = {}

        self.__chats = []

        self.__chatOptionsFrames = []

        self.friendsChatOptions = []

        #ГЫГЫГЫГЫГЫГЫ Я ДОЛБАЕБ Я НАСРАЛ В КОД ГЫГЫГЫГЫГЫГЫГЫГЫ
        self.WidgetForScroll = QtWidgets.QWidget()

        self.getFriends()
        self.createChats()

        self.ui.close.clicked.connect(self.closeWindow)
        self.ui.minimize.clicked.connect(self.on_click_hide)
        self.ui.WindowMode.clicked.connect(self.on_click_fullscreenWindowMode)
        self.ui.AddFriends.clicked.connect(self.addFriend)
        self.ui.ShowFreind.clicked.connect(self.showFriendList)
        self.ui.SettingsButton.clicked.connect(self.show_parameters)
        self.ui.ScrollFriends.setVisible(False)
        self.call_chat()

        self.ui.horizontalFrame.mouseMoveEvent = self.MoveWindow

        self.ui.stackedWidget_2.addWidget(self.ui.WrapperForHomeScreen)
        self.ui.stackedWidget_2.setCurrentWidget(self.ui.WrapperForHomeScreen)

        self.initializeChatsInScrollArea()

    def initializeChatsInScrollArea(self):
        layoutFinal = QtWidgets.QVBoxLayout()
        layoutFinal.setSpacing(5)
        layoutFinal.setContentsMargins(0,0,0,0)

        for chat in self.__chats:
           self.createChatWidget(chat, layoutFinal)

        self.WidgetForScroll.setLayout(layoutFinal)

        self.ui.stackedWidget_2.addWidget(self.ui.WrapperForHomeScreen)
        self.ui.stackedWidget_2.setCurrentWidget(self.ui.WrapperForHomeScreen)

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

        self.ui.ScrollFriends.setWidget(self.WidgetForScroll)
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

    def mouseReleaseEvent(self, event):
        self.pressing = False


    def getFriends(self):
        db = db_handler("26.181.96.20", "Dmitry", "gfggfggfg3D-", "zcord", "friendship")

        friends = db.getDataFromTableColumn("*", f"WHERE friend_one_id = '{self.__user.getNickName()}' OR friend_two_id = '{self.__user.getNickName()}'")

        for friendArr in friends:
            if friendArr[len(friendArr) - 1] == 3:
                continue

            if friendArr[1] not in self.__friends and friendArr[2] not in self.__friends:
                if friendArr[1] != self.__user.getNickName():
                    key = friendArr[1]
                else:
                    key = friendArr[2]

                self.__friends[key] = [friendArr[0], friendArr[3]]
        self.__user.setFrinds(self.__friends)

    def createChats(self):
        for friend in self.__friends.keys():
            self.__chats.append(Chat(self.__friends[friend][0], friend, self.__user, self.voicepr))
        self.showFriendList()


    def addChatToList(self, chatId, friendNick):
        chat = Chat(chatId, friendNick, self.__user)
        self.__chats.append(chat)
        message_client.MessageConnection.addChatToList(chat)
        return chat

    def call_chat(self):
        queueToSend = queue.Queue()
        for chat in self.__chats:
            queueToSend.put(chat)

        self.callClient = message_client.call(self.__user, queueToSend, self.dynamicUpdateSlot)

        self.__client = self.callClient[0]
        self.__messageConnection = self.callClient[1]


    def showProfile(self):
        self.miniProfile = MiniProfile(QtWidgets.QApplication.primaryScreen().geometry().center(), self.__user)
        self.miniProfile.setParent(self.ui.Main)

        self.overlay = Overlay(self.miniProfile, parent=self.ui.Main)
        new_rect = QtCore.QRect(
            self.rect().x(),
            self.rect().y(),
            self.width(),
            self.height()
        )
        self.overlay.setGeometry(new_rect)
        self.overlay.show()
        self.miniProfile.raise_()

        self.miniProfile.show()
        self.miniProfile.exec()


    def addFriendToDict(self, name, chat_id, status):
        self.__friends[name] = [chat_id, status]

    def show_parameters(self):
        self.ui.stackedWidget.setCurrentWidget(self.parameters.ui_pr.MAIN)

    def showFriendList(self):
        if len(self.__chats) == 0:
            if not self.ui.ScrollFriends.isVisible():
                return
            else:
                self.ui.ScrollFriends.setVisible(False)
                return

        if not self.ui.ScrollFriends.isVisible():
            self.ui.ScrollFriends.setVisible(True)
        else:
            self.ui.ScrollFriends.setVisible(False)

    def addFriend(self):
        if not AddFriendWindow.isOpen:
            addFriendsDialog = AddFriendWindow(self.__user)

            addFriendsDialog.show()

            addFriendsDialog.exec()

            senderAndReciver = addFriendsDialog.getSenderAndReciver()

            if len(senderAndReciver) == 0:
                return

            friendshipTable = db_handler("26.181.96.20", "Dmitry", "gfggfggfg3D-", "zcord", "friendship")

            #Подумать над необходимостью получения status, т.к. при создании запроса он всегда равен 1
            friendshipInfo = friendshipTable.getCertainRow("friend_one_id", senderAndReciver[0], "chat_id, status", f"friend_two_id = '{senderAndReciver[1]}'")[0]

            self.dynamicUpdateSlot("ADD-CANDIDATE-FRIEND", (senderAndReciver[1], friendshipInfo[0], friendshipInfo[1]))

            chat = self.dynamicUpdateSlot("UPDATE-CHATS", (friendshipInfo[0], senderAndReciver[1]))
            chat.sendFriendRequest()

    def chooseChat(self):
        sender = self.sender()

        chat = list(filter(lambda x: x.getNickName() == sender.text, self.__chats))[0]

        chat_id = chat.getChatId()

        message_client.MainInterface.change_chat(chat_id, self.__user.getNickName(), message_client.SygnalChanger())

        chat.ui.MAIN_ChatLayout.setContentsMargins(0,0,0,0)
        self.ui.stackedWidget_2.addWidget(chat.ui.MAIN)
        self.ui.stackedWidget_2.setCurrentWidget(chat.ui.MAIN)


    def dynamicUpdateSlot(self, command:str, args:tuple, done_event=None):
        """
        В *args передаются парометры необходимые для дальнейшего выполнения функций в кейсах
                      индекс\/
        ADD-FRIEND: args = 0:"никнейм друга" - обнавляет статус друга в словаре, передает словарь в user
        UPDATE-CHATS: args = 0:"айди чата", 1:"никнейм друга"
        DELETE-FRIEND: args = 0:"никнейм друга"
        DELETE-CHAT: args = 0:"никнейм друга"
        UPDATE-MESSAGE-NUMBER: args = 0: "чат", 1: "новое значение"
        CHANGE-ACTIVITY: args = 0: "self/friend", 1: "цвет", 2: "никнейм друга (если есть)"
        """
        match command:
            case "ADD-FRIEND":
                self.updateFriendshipStatus(args)
                self.__user.setFrinds(self.__friends)
            case "UPDATE-CHATS":
                chat = self.addChatToList(args[0], args[1])
                self.updateChatList(chat)
                if done_event is not None:
                    done_event.set()
                return chat
            case "ADD-CANDIDATE-FRIEND":
                self.addFriendToDict(args[0], args[1], args[2])
                self.__user.setFrinds(self.__friends)
                if done_event is not None:
                    done_event.set()
            case "DELETE-FRIEND":
                self.deleteFriend(args)
                self.__user.setFrinds(self.__friends)
            case "DELETE-CHAT":
                chat = self.deleteChat(args)
                self.deleteChatFromUI(chat)
            case "UPDATE-MESSAGE-NUMBER":
                self.unseenMessages(args[0], args[1])
                if done_event is not None:
                    done_event.set()
            case "CHANGE-ACTIVITY":
                if args[0] == "self":
                    self.change_self_activity_indicator_color(args[1])
                elif args[0] == "friend":
                    self.change_friend_activity_indeicator_color(args[2], args[1])
                else:
                    raise ValueError(f"Expected 'self' or 'friend' but {args[0]} was given")

    def change_self_activity_indicator_color(self, color):
        activity_indicator_qss = f"""background-color:{color};
                                    border-radius:10px;
                                    color:White;
                                    border:3px solid rgba(34,35,39,255);
                                    """
        self.ui.ActivityIndicator_Logo.setStyleSheet(activity_indicator_qss)

    def change_friend_activity_indeicator_color(self, friendNick, color):
        print(self.friendsChatOptions[0].ui.user_name)
        friend_ChatInList = list(filter(lambda x: x.chat.getNickName() == friendNick, self.friendsChatOptions))[0]

        friend_ChatInList.changeIndicatorColor(color)

    def updateFriendshipStatus(self, friendName):
        """Метод просто меняет статус с 1 на 2, т.к. в противном случае будет вызван deleteFriend"""
        self.__friends[friendName][1] = 2

    def deleteFriend(self, friendName):
        del self.__friends[friendName]

    def deleteChat(self, friendName):
        chat = list(filter(lambda chat: chat.getNickName() == friendName, self.__chats))[0]
        self.__chats.remove(chat)
        self.ui.stackedWidget_2.setCurrentWidget(self.ui.WrapperForHomeScreen)
        return chat
    def closeWindow(self):
        #with open("Resources/frineds/friends.json", "w") as Frineds_json:
            #Frineds_json.write(json.dumps(self.__friends))
        self.close()
        message_client.MessageConnection.flg = False
        db_handler._engine.dispose()

        self.__client.close()


    def on_click_hide(self):
        self.showMinimized()

    def on_click_fullscreenWindowMode(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
        self.updateOverlayGeometry()
    def updateOverlayGeometry(self):
        if hasattr(self, 'overlay'):
            new_rect = QtCore.QRect(
                0,
                0,
                self.contentsRect().width(),
                self.contentsRect().height()
            )
            self.overlay.setGeometry(new_rect)

    def updateMiniProfilePosition(self):
        if hasattr(self, "miniProfile"):
            self.miniProfile.center_child_window()
    def updateWindowMargins(self):
        if self.isMaximized():
            screen_geometry = QtWidgets.QApplication.primaryScreen().availableGeometry()
            self.setGeometry(screen_geometry)
            self.updateOverlayGeometry()
            self.updateMiniProfilePosition()
        else:
            self.updateMiniProfilePosition()

    def resizeEvent(self, event):
        self.updateWindowMargins()
        super().resizeEvent(event)

    def createChatWidget(self, chat, layoutFinal):
        self.QFr = ClikableFrame(chat.getNickName())
        self.QFr.clicked.connect(self.chooseChat)
        chat_option = ChatInList(chat.getNickName()[0], chat.getNickName(), chat)
        layout = chat_option.ui.Friend
        if chat.messageNumber is None:
            chat.createUnseenMessageNumber(self.QFr)
        messagesNumber = chat.messageNumber
        messagesNumber.setFixedHeight(25)
        messagesNumber.setFixedWidth(25)
        messagesNumber.setStyleSheet("""color:black;
                                    font-size:18px;
                                    border:1px solid white;
                                    border-radius:10%;
                                    padding:0;
                                    padding-bottom:2px;
                                    text-align:center;
                                    background-color:white;""")

        layout.addWidget(messagesNumber)
        messagesNumber.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)

        self.QFr.setLayout(layout)
        self.QFr.setStyleSheet("""QFrame:hover { 
                                border-radius:15%;
                                background-color:rgba(0, 0, 0, 0.26);}
                                QFrame {
                                margin:0;
                                }""")
        self.QFr.setFixedWidth(250)
        self.QFr.setFixedHeight(70)
        self.QFr.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        layoutFinal.addWidget(self.QFr)
        layoutFinal.update()
        self.friendsChatOptions.append(chat_option)
        return layoutFinal

    def updateChatList(self, chat):
        if self.ui.ScrollFriends.isVisible():
            self.createChatWidget(chat, self.ui.ScrollFriends.widget().layout())

    def deleteChatFromUI(self, chat):
        if self.ui.ScrollFriends.isVisible():
            for i in range(self.ui.ScrollFriends.widget().layout().count()):
                widgetToDelete = self.ui.ScrollFriends.widget().layout().itemAt(i).widget()
                if self.ui.ScrollFriends.widget().layout().itemAt(i).widget().text == chat.getNickName():
                    self.ui.ScrollFriends.widget().layout().takeAt(i)
                    widgetToDelete.deleteLater()
                    self.ui.ScrollFriends.widget().layout().update()
                    break

    def unseenMessages(self, chat:Chat, newValue:int):
        if newValue == 0:
            chat.messageNumber.setVisible(False)
            return
        if not chat.messageNumber.isVisible():
            chat.messageNumber.setVisible(True)

        print(chat.messageNumber.isVisible())
        if newValue >= 99:
            newValue = "99"
        chat.messageNumber.setText(str(newValue))
        #plyer.notification.notify(message='Новое сообщение', app_name='zcord', title=chat.getNickName(), toast= True )
