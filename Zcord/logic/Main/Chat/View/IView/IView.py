from abc import abstractmethod, ABCMeta
from typing import Optional, Union
from PyQt6 import QtWidgets, QtCore
from logic.Main.Chat.View.Message.Message import Message
from logic.Main.Chat.View.CallDialog.CallView import Call
from logic.Main.Chat.View.UserIcon.UserIcon import UserIcon
from logic.Main.Chat.View.dm_view.ChatClass.ChatGUI import Ui_Chat
from logic.Main.Chat.View.group_view.Group.GroupQt import Ui_Group


class QWidgetABCMeta(type(QtWidgets.QWidget), ABCMeta):
    pass


class IView(QtWidgets.QWidget, metaclass=QWidgetABCMeta):
    @abstractmethod
    def ask_for_cached_messages(self, val):
        pass

    @abstractmethod
    def enable_scroll(self):
        pass

    @abstractmethod
    def send_message(self):
        pass

    @abstractmethod
    def receive_message(self, sender, text, date, messageIndex=1, wasSeen: bool = False):  # Нужно еще 20 аргументов
        pass

    @abstractmethod
    def change_unseen_status(self, number_of_widgets):
        pass

    @abstractmethod
    def clear_unseen_messages(self):
        pass

    @abstractmethod
    def clear_chat_layout(self):
        pass

    @property
    @abstractmethod
    def chat_id(self) -> str:
        pass


class BaseChatView(IView):
    messageReceived = QtCore.pyqtSignal(str, str, str, int, bool)
    clear_layout = QtCore.pyqtSignal()
    enable_scroll_bar = QtCore.pyqtSignal()
    change_unseen_status_signal = QtCore.pyqtSignal(int)
    clear_unseen = QtCore.pyqtSignal()

    muteDevice = QtCore.pyqtSignal(str, bool, object)
    connectReceived = QtCore.pyqtSignal(list)
    disconnectReceived = QtCore.pyqtSignal(object)
    callReceived = QtCore.pyqtSignal(bool)
    speechDetector = QtCore.pyqtSignal(bool, int)

    def __init__(self, chatId, user, controller):
        super(BaseChatView, self).__init__()
        self.ui: Optional[Union[Ui_Chat, Ui_Group]]
        """Окно приходящего звонка"""
        self.call_dialog: Call
        # Сигналы
        self.messageReceived.connect(self.receive_message)
        self.enable_scroll_bar.connect(self.enable_scroll)
        self.change_unseen_status_signal.connect(self.change_unseen_status)
        self.clear_unseen.connect(self.clear_unseen_messages)
        self.muteDevice.connect(self.mute_device_friend)
        self.connectReceived.connect(self.join_icon)
        self.disconnectReceived.connect(self.left_icon)
        self.callReceived.connect(self.show_call_widget)
        self.speechDetector.connect(self.speech_detector)
        # Сигналы

        self.ui = Ui_Chat()
        self.ui.setupUi(self)

        self._controller = controller

        self._chat_id = chatId
        self._user = user

        self._old_max_scroll = None
        self._old_value_scroll = None

        self.installEventFilter(self)

        self.messageNumber = None

        self.unseenMessages = []

        self.scroll_pos = 0

        # Словарь по иконкам юзеров: {client: icon}
        self.client_icons = {}
        # Переменные мутов
        self.microphone_mute = False
        self.headphone_mute = False



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

    def send_message(self):
        message_text = self.ui.Chat_input_.text()

        if len(message_text) == 0:
            return

        self._controller.send_message(message_text)
        self.ui.Chat_input_.clear()

    @QtCore.pyqtSlot(str, str, str, int, bool)
    def receive_message(self, sender, text, date, messageIndex=1, wasSeen: bool = False):  # Нужно еще 20 аргументов
        if self.ui.ChatScroll.verticalScrollBar().signalsBlocked():
            self.ui.ChatScroll.verticalScrollBar().blockSignals(False)
        if len(text) == 0:
            return

        message = Message(text, sender)
        message.ui.date_label.setText(date)

        qss = ""
        if sender == self._user.getNickName():
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

        return True

    @QtCore.pyqtSlot(int)
    def change_unseen_status(self, number_of_widgets):
        if not self.unseenMessages or number_of_widgets <= 0:
            return
        try:

            count = min(number_of_widgets, len(self.unseenMessages))

            messages_to_process = self.unseenMessages[-count:]

            for message in messages_to_process:
                message.WasSeenlabel.setText("Seen")

            self.unseenMessages = self.unseenMessages[:-count]

        except Exception as e:
            print(f"Error updating unseen status: {e}")

    @QtCore.pyqtSlot()
    def clear_unseen_messages(self):
        self.unseenMessages.clear()

    def clear_chat_layout(self):
        self.ui.ChatScroll.verticalScrollBar().blockSignals(True)
        self.ui.ChatScroll.clear()

    @property
    def chat_id(self):
        return self._chat_id

    def stop_call(self):
        self.ui.Call.hide()
        self._controller.stop_call()

        for icon in self.client_icons.values():
            self.ui.UsersFiled_layout.removeWidget(icon.ui.widget_2)
        self.client_icons = {}

    # Функция чередования для девайса мута друга
    def mute_device_friend(self, device, flg, client):
        if device == "mic":
            self.mute_mic_friend(flg, client)
        elif device == "head":
            self.mute_head_friend(flg, client)

    # Микрофон
    def mute_mic_self(self):
        self.microphone_mute = not self.microphone_mute
        self.client_icons[self._user.id].mute_mic(self.microphone_mute)
        self._controller.mute_mic_self(self.microphone_mute)

    def mute_mic_friend(self, flg, client):  # Сюда будет передаваться id юзера у которого пришел мут с сервера
        self.client_icons[int(client["user_id"])].mute_mic(flg)

    # Наушники
    def mute_head_self(self):
        self.headphone_mute = not self.headphone_mute
        self.client_icons[self._user.id].mute_head(self.headphone_mute)
        self._controller.mute_head_self(self.headphone_mute)

    def mute_head_friend(self, flg, client):  # Сюда будет передаваться id юзера у которого пришел мут с сервера
        self.client_icons[int(client["user_id"])].mute_head(flg)

    # Работа с иконками юзеров
    # Условие 1 - подключение к группе пользователей
    def join_icon(self, clients):
        print(f"join_icon")
        for client in clients:
            if int(client["user_id"]) not in self.client_icons.keys():
                newcomer = UserIcon(client, self._user)
                self.client_icons[int(client["user_id"])] = newcomer
                self.ui.UsersFiled_layout.addWidget(newcomer.ui.widget_2,
                                                    alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
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
