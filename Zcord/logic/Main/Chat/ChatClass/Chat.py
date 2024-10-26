from logic.Main.Chat.ChatClass.ChatGUI import Ui_Chat
from PyQt6 import QtWidgets, QtCore, QtGui
from logic.Main.Chat.Message.Message import Message

class Chat(QtWidgets.QWidget):
    def __init__(self, chatId, friendNick, user):
        super(Chat, self).__init__()

        self.ui = Ui_Chat()
        self.ui.setupUi(self)

        self.__chatId = chatId
        self.__user = user
        self.__friendNickname = friendNick


        self.ui.UsersNickInChat.setText(friendNick)
        self.ui.UsersLogoinChat.setText(friendNick[0])

        self.ui.Send_button.clicked.connect(self.sendMessage)

    def sendMessage(self):
        messageText = self.ui.Chat_input_.text()

        if len(messageText) == 0:
            return

        message = Message(messageText, self.__user.getNickName())

        widget = QtWidgets.QListWidgetItem(self.ui.ChatScroll)
        widget.setSizeHint(message.ui.Message_.sizeHint())

        self.ui.ChatScroll.setSpacing(10)
        self.ui.ChatScroll.addItem(widget)
        self.ui.ChatScroll.setItemWidget(widget, message.ui.Message_)
        self.ui.Chat_input_.clear()





    def getNickName(self):
        return self.__friendNickname


    def getChatWidget(self):
        return self.ui
