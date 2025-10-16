from abc import abstractmethod, ABCMeta
from typing import Optional, Union
from PyQt6 import QtWidgets, QtCore
from logic.Main.Chat.View.Message.Message import Message
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

    def __init__(self, chatId, user, controller):
        super(BaseChatView, self).__init__()
        self.ui: Optional[Union[Ui_Chat, Ui_Group]]
        # Сигналы
        self.messageReceived.connect(self.receive_message)
        self.enable_scroll_bar.connect(self.enable_scroll)
        self.change_unseen_status_signal.connect(self.change_unseen_status)
        self.clear_unseen.connect(self.clear_unseen_messages)
        # Сигналы

        self._controller = controller

        self._chat_id = chatId
        self._user = user

        self._old_max_scroll = None
        self._old_value_scroll = None

        self.installEventFilter(self)

        self.messageNumber = None

        self.unseenMessages = []

        self.scroll_pos = 0

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
