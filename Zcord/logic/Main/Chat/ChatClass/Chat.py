from logic.Main.Chat.ChatClass.ChatGUI import Ui_Chat
from PyQt6 import QtWidgets, QtCore
from logic.Main.Chat.Message.Message import Message
from logic.Message import message_client
from logic.Voice import audio_send


class Chat(QtWidgets.QWidget):
    def __init__(self, chatId, friendNick, user):
        super(Chat, self).__init__()
        self.voice_conn = None
        self.ui = Ui_Chat()
        self.ui.setupUi(self)
        self.ui.Call.hide()
        self.__chatId = chatId
        self.__user = user
        self.__friendNickname = friendNick

        self.ui.UsersNickInChat.setText(friendNick)
        self.ui.UsersLogoinChat.setText(friendNick[0])

        self.installEventFilter(self)

        self.ui.Send_button.clicked.connect(self.sendMessage)

        self.ui.ChatScroll.setSpacing(10)
        self.ui.ChatScroll.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.ui.ChatScroll.setSelectionMode(QtWidgets.QListWidget.SelectionMode.NoSelection)

        self.ui.Chat_input_.returnPressed.connect(self.sendMessage)

        self.ui.CallButton.clicked.connect(self.call_voice)
        self.ui.leaveCall.clicked.connect(self.leave_call)

    def sendMessage(self):
        messageText = self.ui.Chat_input_.text()

        if len(messageText) == 0:
            return

        message_client.MessageConnection.send_message(messageText, self.__user.getNickName())
        message = Message(messageText, self.__user.getNickName())

        widget = QtWidgets.QListWidgetItem(self.ui.ChatScroll)
        widget.setSizeHint(message.ui.Message_.sizeHint())

        self.ui.ChatScroll.addItem(widget)
        self.ui.ChatScroll.setItemWidget(widget, message.ui.Message_)
        self.ui.ChatScroll.setCurrentItem(widget)
        self.ui.Chat_input_.clear()



    def recieveMessage(self, sender, text):
        if len(text) == 0:
            return
        message = Message(text, sender)

        widget = QtWidgets.QListWidgetItem(self.ui.ChatScroll)
        widget.setSizeHint(message.ui.Message_.sizeHint())

        self.ui.ChatScroll.addItem(widget)
        self.ui.ChatScroll.setItemWidget(widget, message.ui.Message_)
        self.ui.ChatScroll.setCurrentItem(widget)

        return True

    def leave_call(self):
        self.voice_conn.close()
        self.ui.Call.hide()
        self.voice_conn = None

    def call_voice(self):
        if not self.voice_conn:
            self.voice_conn = audio_send.start_voice()
            self.ui.Call.show()
        else:
            print("Вы с кем-то уже разговариваете")

    def clearLayout(self):
        self.ui.ChatScroll.clear()

    def getNickName(self):
        return self.__friendNickname


    def getChatWidget(self):
        return self.ui

    def getChatId(self):
        return self.__chatId
