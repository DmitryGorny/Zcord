from PyQt6 import QtWidgets, QtCore, QtGui
from logic.Main.Chat.Message.MessageWidget import Ui_Form

class Message(QtWidgets.QWidget):
    def __init__(self, text, username):
        super(Message, self).__init__()

        self.ui = Ui_Form()

        self.ui.setupUi(self)

        self.ui.UserLogo.setText(username[0])
        self.ui.Users_Name.setText(username)
        self.ui.Message_Text.setText(text)




