import queue
from typing import List

from PyQt6 import QtWidgets, QtCore

from logic.Authorization.User.User import User
from logic.Main.CompiledGUI.MainWindowGUI import Ui_Zcord
from logic.Main.Friends.FriendsWidget import FriendsWidget
from logic.client.ClientConnections.ClientConnections import ClientConnections
from logic.Main.CompiledGUI.Helpers.ClickableFrame import ClikableFrame
from logic.Main.Parameters.Params_Window import ParamsWindow
from logic.Main.Voice_main.VoiceParamsClass import VoiceParamsClass
from PyQt6.QtGui import QIcon
from logic.Main.miniProfile.MiniProfile import MiniProfile, Overlay
from logic.Main.CompiledGUI.Helpers.ChatInList import ChatInList


class MainWindow(QtWidgets.QMainWindow):
    dynamic_update = QtCore.pyqtSignal(str, dict)

    def __init__(self, user):
        super(MainWindow, self).__init__()
        self.ui = Ui_Zcord()
        self.ui.setupUi(self)

        self.voicepr = VoiceParamsClass()

        # Объект пользователя
        self.__user: User = user

        # Сигналы
        self.dynamic_update.connect(self.dynamic_update_slot)
        # Сигналы

        # Работа с друзьями
        self._friends: FriendsWidget = FriendsWidget(self.__user)
        self.ui.stackedWidget_2.addWidget(self._friends.get_widget())

        # Параметры
        self.parameters = ParamsWindow(self.ui, self.voicepr)
        self.ui.stackedWidget.addWidget(self.parameters.ui_pr.MAIN)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

        self.ui.pushButton.setIcon(QIcon("GUI/icon/forum_400dp_333333_FILL0_wght400_GRAD0_opsz48.svg"))

        # Лого
        self.ui.UsersLogo.setText(self.__user.getNickName()[0])  # Установка первой буквы в лого
        self.ui.UsersLogo.clicked.connect(self.showProfile)

        # Чаты
        self._friendsChatOptions: List[ChatInList] = self.create_chats()

        self.WidgetForScroll = QtWidgets.QWidget()

        # Конектим сигналы к кнопкам всем селом
        self.ui.close.clicked.connect(self.closeWindow)
        self.ui.minimize.clicked.connect(self.on_click_hide)
        self.ui.WindowMode.clicked.connect(self.on_click_fullscreenWindowMode)
        self.ui.AddFriends.clicked.connect(self.add_friend)
        self.ui.ShowFreind.clicked.connect(self.showFriendList)
        self.ui.SettingsButton.clicked.connect(self.show_parameters)
        self.ui.ScrollFriends.setVisible(False)

        # Вызов клиента
        self.call_chat()

        self.ui.horizontalFrame.mouseMoveEvent = self.MoveWindow

        self.ui.stackedWidget_2.addWidget(self.ui.WrapperForHomeScreen)
        self.ui.stackedWidget_2.setCurrentWidget(self.ui.WrapperForHomeScreen)

        self.showFriendList()

        self.initializeChatsInScrollArea()

    # <----------------------------------------------Работа с чатами--------------------------------------------------->
    def create_chats(self) -> List[ChatInList]:
        """Создает GUI объекты чатов ChatInList и возвращает их список"""
        chats_list: List[ChatInList] = []
        for attrs in self.__user.get_chats():
            chats_list.append(ChatInList(attrs['nickname'], attrs['chat_id'], attrs["chat_ui"]))
            self.ui.stackedWidget_2.addWidget(
                attrs["chat_ui"])  # Передается UI объекта ChatView для отображения самого чата
        return chats_list

    def addChatToList(self, chatId, friendNick):
        # chat = Chat(chatId, friendNick, self.__user)
        # self.__chats.append(chat)
        # message_client.MessageConnection.addChatToList(chat)
        # return chat
        pass

    def call_chat(self):
        queueToSend = queue.Queue()
        for chat in self.__user.get_chats():
            chat["socket_controller"] = self.__user.get_socket_controller()
            queueToSend.put(chat)

        ClientConnections.start_client(self.__user, queueToSend, self.dynamic_update)

    def initializeChatsInScrollArea(self):
        """Добавляет объекты ChatInList в ScrollFriends"""
        layoutFinal = QtWidgets.QVBoxLayout()
        layoutFinal.setSpacing(5)
        layoutFinal.setContentsMargins(0, 0, 0, 0)

        for chat in self._friendsChatOptions:
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

    def choose_chat(self):
        sender = self.sender()

        chat = list(filter(lambda x: x.username == sender.text, self._friendsChatOptions))[0]

        self.__user.change_chat(chat.id)

        # chat.chat_ui.MAIN_ChatLayout.setContentsMargins(0, 0, 0, 0)
        self.ui.stackedWidget_2.setCurrentWidget(chat.chat_ui)

    def change_friend_activity_indeicator_color(self, friendNick, color):
        friend_ChatInList = list(filter(lambda x: x.chat.getNickName() == friendNick, self._friendsChatOptions))[0]

        friend_ChatInList.changeIndicatorColor(color)

    def createChatWidget(self, chat_option: ChatInList, layoutFinal):
        """Создает объекь ClikableFrame для дальнейшей вставки в ScrollArea"""
        self.QFr = ClikableFrame(chat_option.username)
        self.QFr.clicked.connect(self.choose_chat)

        layout = chat_option.ui.Friend
        if chat_option.messageNumber is None:
            chat_option.createUnseenMessageNumber(self.QFr)

        messagesNumber = chat_option.messageNumber

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

        return layoutFinal

    def updateChatList(self, chat):
        self.createChatWidget(chat, self.ui.ScrollFriends.widget().layout())

    def deleteChatFromUI(self, chat):
        """Удаляет чат из ScrollFriends"""
        for i in range(self.ui.ScrollFriends.widget().layout().count()):
            widgetToDelete = self.ui.ScrollFriends.widget().layout().itemAt(i).widget()
            if self.ui.ScrollFriends.widget().layout().itemAt(i).widget().text == chat.nickname:
                self.ui.ScrollFriends.widget().layout().takeAt(i)
                widgetToDelete.deleteLater()
                self.ui.ScrollFriends.widget().layout().update()
                break

        if len(self._friendsChatOptions) == 0:
            self.ui.ScrollFriends.setVisible(False)

    def unseenMessages(self, chat_id: str, newValue: int):
        chat = list(filter(lambda x: x.id == chat_id, self._friendsChatOptions))[0]
        if newValue == 0:
            chat.messageNumber.setVisible(False)
            return
        if not chat.messageNumber.isVisible():
            chat.messageNumber.setVisible(True)

        if newValue >= 99:
            newValue = "99"
        chat.messageNumber.setText(str(newValue))
        # plyer.notification.notify(message='Новое сообщение', app_name='zcord', title=chat.getNickName(), toast= True )

    def delete_DM_chat(self, chat_id: str):
        self.__user.delete_chat(chat_id, is_dm=True)
        chat_gui = list(filter(lambda x: chat_id == x.id, self._friendsChatOptions))[0]
        self._friendsChatOptions.remove(chat_gui)

        self.ui.stackedWidget_2.setCurrentWidget(self.ui.WrapperForHomeScreen)
        return chat_gui

    # <----------------------------------------------Работа с чатами--------------------------------------------------->

    def mousePressEvent(self, event):
        self.start = self.mapToGlobal(event.pos())
        self.pressing = True

    def MoveWindow(self, event):
        if self.isMaximized():
            return

        if self.pressing:
            self.end = self.mapToGlobal(event.pos())
            movement = self.end - self.start
            self.move(self.mapToGlobal(movement))
            self.start = self.end

    def mouseReleaseEvent(self, event):
        self.pressing = False

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

    def show_parameters(self):
        self.ui.stackedWidget.setCurrentWidget(self.parameters.ui_pr.MAIN)

    # <---------------------------------------------Работа с друзьями-------------------------------------------------->
    def showFriendList(self):
        if len(self._friendsChatOptions) == 0:
            if not self.ui.ScrollFriends.isVisible():
                return
            else:
                self.ui.ScrollFriends.setVisible(False)
                return

        if not self.ui.ScrollFriends.isVisible():
            self.ui.ScrollFriends.setVisible(True)
        else:
            self.ui.ScrollFriends.setVisible(False)

    def add_friend(self):
        self.ui.stackedWidget_2.setCurrentWidget(self._friends.get_widget())

    # <---------------------------------------------Работа с друзьями-------------------------------------------------->
    @QtCore.pyqtSlot(str, dict)
    def dynamic_update_slot(self, command: str, args: dict, done_event=None):
        match command:
            case "FRIENDSHIP-REQUEST-SELF":
                self._friends.add_your_friend_request(friend_id=args['receiver_id'], username=args['receiver_nick'])
            case "FRIENDSHIP-REQUEST-OTHER":
                self._friends.add_others_friend_request(friend_id=args['sender_id'], username=args['sender_nick'])
            case "SELF-RECALL-REQUEST":
                self._friends.remove_your_request(args['user_id'])
            case "OTHERS-RECALL-REQUEST":
                self._friends.remove_others_request(args['user_id'])

            case "UPDATE-CHATS":
                chat = self.addChatToList(args[0], args[1])
                self.updateChatList(chat)
                if done_event is not None:
                    done_event.set()
                return chat

            case "DELETE-CHAT":
                chat = self.delete_DM_chat(args)
                self.deleteChatFromUI(chat)
            case "UPDATE-MESSAGE-NUMBER":
                self.unseenMessages(chat_id=args['chat_id'], newValue=args['message_number'])
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
    def closeWindow(self):
        # with open("Resources/frineds/friends.json", "w") as Frineds_json:
        # Frineds_json.write(json.dumps(self.__friends))
        self.close()
        ClientConnections.close()

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
