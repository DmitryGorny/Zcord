import threading

from logic.Main.Chat.View.Animation.AnimatedCall import AnimatedBorderButton
from logic.Main.Chat.View.ChatClass.ChatGUI import Ui_Chat
from logic.Main.Chat.View.CallDialog.CallView import Call
from PyQt6 import QtWidgets, QtCore
from logic.Main.Chat.View.Message.Message import Message
from logic.Main.Chat.View.UserIcon.UserIcon import UserIcon


class ChatView(QtWidgets.QWidget):
    muteDevice = QtCore.pyqtSignal(str, bool, object)
    connectReceived = QtCore.pyqtSignal(list)
    disconnectReceived = QtCore.pyqtSignal(object)
    callReceived = QtCore.pyqtSignal(bool)
    speechDetector = QtCore.pyqtSignal(bool, int)

    messageReceived = QtCore.pyqtSignal(str, str, str, int, bool)
    awaitedMessageReceive = QtCore.pyqtSignal(str, str, str, int, bool, object)
    clear_layout = QtCore.pyqtSignal()
    enable_scroll_bar = QtCore.pyqtSignal()
    change_unseen_status_signal = QtCore.pyqtSignal(int)
    clear_unseen = QtCore.pyqtSignal()

    def __init__(self, chatId, friend_nick, friend_id, user, controller):
        super(ChatView, self).__init__()
        # Сигналы
        self.messageReceived.connect(self.recieveMessage)
        self.muteDevice.connect(self.mute_device_friend)
        self.connectReceived.connect(self.join_icon)
        self.disconnectReceived.connect(self.left_icon)
        self.callReceived.connect(self.show_call_widget)
        self.speechDetector.connect(self.speech_detector)

        self.awaitedMessageReceive.connect(self.recieveMessage)
        self.enable_scroll_bar.connect(self.enable_scroll)
        self.change_unseen_status_signal.connect(self.change_unseen_status)
        self.clear_unseen.connect(self.clear_unseen_messages)
        # Сигналы

        # интерфейс чата
        self.ui = Ui_Chat()
        self.ui.setupUi(self)

        # контроллер
        self._controller = controller

        self.__chatId = chatId
        self.__user = user
        self.__friendNickname = friend_nick
        self.__friend_id = friend_id

        self.ui.MAIN_ChatLayout.setContentsMargins(0, 0, 0, 0)

        self._old_max_scroll = None
        self._old_value_scroll = None

        self.ui.UsersNickInChat.setText(friend_nick)
        self.ui.UsersLogoinChat.setText(friend_nick[0])

        self.installEventFilter(self)

        self.ui.Send_button.clicked.connect(self.sendMessage)

        self.ui.ChatScroll.setSpacing(10)
        self.ui.ChatScroll.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.ui.ChatScroll.setSelectionMode(QtWidgets.QListWidget.SelectionMode.NoSelection)

        self.ui.Chat_input_.returnPressed.connect(self.sendMessage)

        self.ui.ChatScroll.verticalScrollBar().valueChanged.connect(self.ask_for_cached_messages)

        self.ui.ChatScroll.setVerticalScrollMode(QtWidgets.QListWidget.ScrollMode.ScrollPerPixel)

        # if self.__user.getFriends()[self.__friendNickname][1] == 1: TODO: Вернуть после переработки
        # self.ui.ChatInputLayout.setHidden(True)

        self.messageNumber = None

        self.unseenMessages = []

        self.scroll_pos = 0

        # Войс GUI
        self.ui.Call.hide()

        # Словарь по иконкам юзеров: {client: icon}
        self.client_icons = {}
        # Переменные мутов
        self.microphone_mute = False
        self.headphone_mute = False

        # Подключение кнопок войса
        """Окно чата"""
        self.ui.CallButton.clicked.connect(self.start_call)
        self.ui.leaveCall.clicked.connect(self.stop_call)
        self.ui.muteMic.clicked.connect(self.mute_mic_self)
        self.ui.muteHeadphones.clicked.connect(self.mute_head_self)

        """Окно приходящего звонка"""
        self.call_dialog = Call(self.start_call)

    def ask_for_cached_messages(self, val):
        if val <= int(self.ui.ChatScroll.verticalScrollBar().maximum() / 4):
            self._controller.ask_for_cached_message()

            self._old_max_scroll = self.ui.ChatScroll.verticalScrollBar().maximum()
            self._old_value_scroll = self.ui.ChatScroll.verticalScrollBar().value()

    @QtCore.pyqtSlot()
    def enable_scroll(self):
        scrollbar = self.ui.ChatScroll.verticalScrollBar()

        new_max = scrollbar.maximum()
        scroll_delta = new_max - self._old_max_scroll

        if scroll_delta > 0:
            scrollbar.setValue(self._old_value_scroll + scroll_delta)

    def sendMessage(self):
        message_text = self.ui.Chat_input_.text()

        if len(message_text) == 0:
            return

        self._controller.send_message(message_text)
        self.ui.Chat_input_.clear()

    @QtCore.pyqtSlot(str, str, str, int, bool)
    def recieveMessage(self, sender, text, date, messageIndex=1, wasSeen: bool = False,
                       event: threading.Event = None):  # Нужно еще 20 аргументов
        if self.ui.ChatScroll.verticalScrollBar().signalsBlocked():
            self.ui.ChatScroll.verticalScrollBar().blockSignals(False)

        if len(text) == 0:
            return

        message = Message(text, sender)
        message.ui.date_label.setText(date)

        qss = ""
        if sender == self.__user.getNickName():
            qss = """QFrame {
                    background-color:rgba(38,40,45,255);
                    border-radius:25%;
                    border:2px solid white;
                    }
                    }"""
        if not wasSeen:
            message.ui.WasSeenlabel.setText("Unseen")
            self.unseenMessages.append(message.ui)

        if len(qss) != 0:
            message.ui.Message_.setStyleSheet(qss)

        widget = QtWidgets.QListWidgetItem()
        widget.setSizeHint(message.ui.Message_.sizeHint())

        if messageIndex == 1:
            self.ui.ChatScroll.addItem(widget)
        else:
            self.ui.ChatScroll.insertItem(0, widget)
            # self.scroll_pos = self.ui.ChatScroll.verticalScrollBar().value()

        self.ui.ChatScroll.setItemWidget(widget, message.ui.Message_)

        if messageIndex == 1:
            self.ui.ChatScroll.setCurrentItem(widget)

        if event is not None:
            event.set()

        return True

    def slotForScroll(self):
        self.ui.ChatScroll.verticalScrollBar().setValue(int(self.ui.ChatScroll.verticalScrollBar().maximum() / 4))

    def addMessageOnTop(self, sender, text, date, wasSeen: int = 0, event=None):  # Надубасил в код жестко
        self.recieveMessage(sender, text, date, wasSeen, event)

    @QtCore.pyqtSlot(int)
    def change_unseen_status(self, number_of_widgets):
        if not self.unseenMessages or number_of_widgets <= 0:
            return
        try:

            count = min(number_of_widgets, len(self.unseenMessages))

            messages_to_process = self.unseenMessages[-count:]

            for message in messages_to_process:
                print(message.Message_Text.text())
                message.WasSeenlabel.setText("Seen")

            self.unseenMessages = self.unseenMessages[:-count]

        except Exception as e:
            print(f"Error updating unseen status: {e}")

    @QtCore.pyqtSlot()
    def clear_unseen_messages(self):
        self.unseenMessages.clear()

    def startMessaging(self):
        self.ui.ChatInputLayout.setHidden(False)
        self.clearLayout()

    def clearLayout(self):
        self.ui.ChatScroll.verticalScrollBar().blockSignals(True)
        self.ui.ChatScroll.clear()

    def rejectRequest(self, deleteFriend: bool = False):
        self._controller.reject_request(self.__user, self.__friendNickname, deleteFriend)

    def blockUser(self):
        self._controller.block_user(self.__user, self.__friendNickname)

    def getNickName(self):
        return self.__friendNickname

    def getChatWidget(self):
        return self.ui

    def getChatId(self):
        return self.__chatId

    #  абстрактно здесь будет класс VOICE GUI
    def start_call(self):
        print(f"ФЛАГ НАХУЙ {self._controller.get_voice_flg()}")
        if self._controller.get_voice_flg():
            return

        self.ui.Call.show()

        """Дальше здесь показана анимация дозвона до собеседника (но перед эти необходимо сделать синхронизацию 
        иконок пользователей с сервером)"""
        client = {
            "user_id": self.__friend_id,
            "user": self.__friendNickname
        }

        newcomer = UserIcon(client, self.__user, pre_create=True)
        self.client_icons[int(client["user_id"])] = newcomer
        self.ui.UsersFiled_layout.addWidget(newcomer.ui.widget_2, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)

        self._controller.start_call(self.__user, self.__chatId)
        self.call_dialog.hide_call_event()

    def stop_call(self):
        self.ui.Call.hide()
        self._controller.stop_call()

        for icon in self.client_icons.values():
            self.ui.UsersFiled_layout.removeWidget(icon.ui.widget_2)
        self.client_icons = {}

    def show_call_dialog(self):
        self.call_dialog.show_call_event()

    # Функция чередования для девайса мута друга
    def mute_device_friend(self, device, flg, client):
        if device == "mic":
            self.mute_mic_friend(flg, client)
        elif device == "head":
            self.mute_head_friend(flg, client)

    # Микрофон
    def mute_mic_self(self):
        self.microphone_mute = not self.microphone_mute
        self.client_icons[self.__user.id].mute_mic(self.microphone_mute)
        self._controller.mute_mic_self(self.microphone_mute)

    def mute_mic_friend(self, flg, client):  # Сюда будет передаваться id юзера у которого пришел мут с сервера
        self.client_icons[int(client["user_id"])].mute_mic(flg)

    # Наушники
    def mute_head_self(self):
        self.headphone_mute = not self.headphone_mute
        self.client_icons[self.__user.id].mute_head(self.headphone_mute)
        self._controller.mute_head_self(self.headphone_mute)

    def mute_head_friend(self, flg, client):  # Сюда будет передаваться id юзера у которого пришел мут с сервера
        self.client_icons[int(client["user_id"])].mute_head(flg)

    # Работа с иконками юзеров
    # Условие 1 - подключение к группе пользователей
    def join_icon(self, clients):
        print(f"join_icon")
        for client in clients:
            if int(client["user_id"]) not in self.client_icons.keys():
                newcomer = UserIcon(client, self.__user)
                self.client_icons[int(client["user_id"])] = newcomer
                self.ui.UsersFiled_layout.addWidget(newcomer.ui.widget_2, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
            else:
                self.client_icons[int(client["user_id"])].animate_call.stop_animation()
                self.client_icons[int(client["user_id"])].default_animation()

    # Условие 2 - выход одного из пользователей peer_left
    def left_icon(self, client):
        print("left_icon")
        self.ui.UsersFiled_layout.removeWidget(self.client_icons[int(client["user_id"])].ui.widget_2)
        del self.client_icons[int(client["user_id"])]

    def show_call_widget(self, flg):
        if flg and self.ui.Call.isHidden():
            self.call_dialog.show_call_event()
        else:
            self.call_dialog.hide_call_event()

    def speech_detector(self, flg, user_id):
        try:
            self.client_icons[int(user_id)].speech_animation(flg)
        except KeyError as e:
            pass
