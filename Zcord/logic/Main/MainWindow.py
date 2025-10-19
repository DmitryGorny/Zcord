import queue
import sys
from typing import List
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import Qt
from logic.Authorization.User.User import User
from logic.Main.MainWidnowChats.ChatInList import ChatInList
from logic.Main.MainWindowGUI import Ui_Zcord
from logic.Main.Friends.FriendsWidget import FriendsWidget
from logic.client.ClientConnections.ClientConnections import ClientConnections
from logic.Main.Parameters.Params_Window import ParamsWindow
from logic.Main.Chat.View.Voice_params.VoiceParamsClass import VoiceParamsClass
from logic.Main.miniProfile.MiniProfile import MiniProfile, Overlay
from qframelesswindow import FramelessWindow
from logic.Main.TitleBar.TitleBar import CustomTitleBar


class MainWindow(FramelessWindow):
    dynamic_update = QtCore.pyqtSignal(str, dict)

    def __init__(self, user):
        super(MainWindow, self).__init__()
        self.ui = Ui_Zcord()
        self.ui.setupUi(self)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setResizeEnabled(True)

        self._title_bar = CustomTitleBar(self)
        self.setTitleBar(self._title_bar)

        self.setWindowTitle("Zcord")

        self.setStyleSheet("""
                            QWidget {
                                background-color: black;
                            }
                            QScrollArea, QScrollArea QWidget, QScrollArea::viewport {
                                background-color: black;
                            }
                            QStackedWidget {
                                background-color: black;
                            }
                        """)

        # Уведомления о заявках в комнатах и друзьях
        self.ui.friends_alert.setHidden(True)
        self.ui.room_alert.setHidden(True)

        # Объект пользователя
        self.__user: User = user

        # Сигналы
        self.dynamic_update.connect(self.dynamic_update_slot)
        # Сигналы

        self.voicepr = VoiceParamsClass()
        self.parameters = ParamsWindow(self.ui, self.voicepr)
        self.ui.stackedWidget.addWidget(self.parameters.ui_pr.MAIN)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        # Работа с друзьями
        self._friends: FriendsWidget = FriendsWidget(self.__user)
        self.ui.stackedWidget_2.addWidget(self._friends.get_widget())

        if self._friends.has_requests():
            self.friend_request_alert()

        # Лого
        self.ui.UsersLogo.setText(self.__user.getNickName()[0])  # Установка первой буквы в лого
        self.ui.UsersLogo.clicked.connect(self.showProfile)

        # Чаты
        self._friendsChatOptions: List[ChatInList] = self.create_chats()

        self.WidgetForScroll = QtWidgets.QWidget()

        # Конектим сигналы к кнопкам всем селом
        self.ui.AddFriends.clicked.connect(self.add_friend)
        self.ui.ShowFreind.clicked.connect(self.showFriendList)
        self.ui.SettingsButton.clicked.connect(self.show_parameters)
        self.ui.ScrollFriends.setVisible(False)

        # Вызов клиента
        self.call_chat()

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

    def add_chat_to_view(self, chat_id: str, friend_nick: str, ui) -> ChatInList:
        chat = ChatInList(friend_nick, str(chat_id), ui)
        self._friendsChatOptions.append(chat)
        self.ui.stackedWidget_2.addWidget(
            ui)
        return chat

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

        self.ui.stackedWidget_2.setCurrentWidget(chat.chat_ui)

    def change_friend_activity_indeicator_color(self, friendNick, color):
        friend_ChatInList = list(filter(lambda x: x.username == friendNick, self._friendsChatOptions))[0]
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
            if self.ui.ScrollFriends.widget().layout().itemAt(i).widget().text == chat.username:
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
        chat_gui = list(filter(lambda x: str(chat_id) == x.id, self._friendsChatOptions))[0]
        self._friendsChatOptions.remove(chat_gui)
        if self.ui.stackedWidget_2.currentWidget() == chat_gui.chat_ui:
            self.ui.stackedWidget_2.setCurrentWidget(self.ui.WrapperForHomeScreen)

        return chat_gui

    # <----------------------------------------------Работа с чатами--------------------------------------------------->

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
        self._friends.has_requests()
        self.ui.stackedWidget_2.setCurrentWidget(self._friends.get_widget())

    # <---------------------------------------------Работа с друзьями-------------------------------------------------->
    @QtCore.pyqtSlot(str, dict)
    def dynamic_update_slot(self, command: str, args: dict):
        match command:
            case "FRIENDSHIP-REQUEST-SELF":
                self._friends.add_your_friend_request(friend_id=args['receiver_id'], username=args['receiver_nick'])
            case "FRIENDSHIP-REQUEST-OTHER":
                self._friends.add_others_friend_request(friend_id=args['sender_id'], username=args['sender_nick'])
                self.friend_request_alert()
            case "SELF-RECALL-REQUEST":
                self._friends.remove_your_request(args['user_id'])
            case "OTHERS-RECALL-REQUEST":
                self._friends.remove_others_request(args['user_id'])
                self.friend_request_alert()
            case "ACCEPT-REQUEST-OTHERS":
                self._friends.remove_others_request(args['user_id'])
                chat = self.__user.add_chat(chat_id=args['chat_id'], username=args['sender_nickname'], friend_id=args['friend_id'])
                chat_gui = self.add_chat_to_view(chat_id=args['chat_id'], friend_nick=args['sender_nickname'],
                                                 ui=chat.ui.MAIN)
                ClientConnections.add_chat({'chat_id': args['chat_id'],
                                            'nickname': args['sender_nickname'],
                                            'socket_controller': self.__user.get_socket_controller()})
                self.friend_request_alert()
                self.updateChatList(chat_gui)
            case "ACCEPT-REQUEST-SELF":
                self._friends.remove_your_request(args['user_id'])
                self._friends.remove_add_friend_widget(args['friend_nickname'])
                chat = self.__user.add_chat(chat_id=args['chat_id'], username=args['friend_nickname'], friend_id=args['user_id'])
                chat_gui = self.add_chat_to_view(chat_id=args['chat_id'], friend_nick=args['friend_nickname'],
                                                 ui=chat.ui.MAIN)
                ClientConnections.add_chat({'chat_id': args['chat_id'],
                                            'nickname': args['friend_nickname'],
                                            'socket_controller': self.__user.get_socket_controller()})
                self.updateChatList(chat_gui)
            case "DECLINE-REQUEST-OTHERS":
                self._friends.show_hide_alert()
                has_reqs = self._friends.has_requests()
                if has_reqs:
                    self.friend_request_alert()
            case "DECLINE-REQUEST-SELF":
                self._friends.remove_your_request(args['receiver_id'])
                self._friends.remove_add_friend_widget(args['friend_nickname'])
            case "DELETE-FRIEND":
                chat = self.delete_DM_chat(args['chat_id'])
                self.deleteChatFromUI(chat)
            case "UPDATE-MESSAGE-NUMBER":
                self.unseenMessages(chat_id=args['chat_id'], newValue=args['message_number'])
            case "CHANGE-ACTIVITY":
                if args['target'] == "self":
                    self.change_self_activity_indicator_color(args['color'])
                elif args['target'] == "friend":
                    self.change_friend_activity_indeicator_color(args['sender_nickname'], args['color'])
                else:
                    raise ValueError(f"Expected 'self' or 'friend' but {args[0]} was given")

    def friend_request_alert(self):
        if self.ui.friends_alert.isHidden():
            self.ui.friends_alert.setHidden(False)
        else:
            self.ui.friends_alert.setHidden(True)

    def change_self_activity_indicator_color(self, color):
        activity_indicator_qss = f"""background-color:{color};
                                    border-radius:10px;
                                    color:White;
                                    border:3px solid rgba(34,35,39,255);
                                    """
        self.ui.ActivityIndicator_Logo.setStyleSheet(activity_indicator_qss)

    def close(self):
        super().close()
        ClientConnections.close()
        sys.exit(0)

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


class ClikableFrame(QtWidgets.QFrame):
    def __init__(self, text):
        super(ClikableFrame, self).__init__()
        self.text = text

    clicked = QtCore.pyqtSignal()

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)

        self.clicked.emit()
