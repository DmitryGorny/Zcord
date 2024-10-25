from logic.Main.Chat.ChatClass.ChatGUI import Ui_Chat
from PyQt6 import QtWidgets, QtCore, QtGui

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


    #def sendMessage(self):


    def getNickName(self):
        return self.__friendNickname


    def getChatWidget(self):
        return self.ui
