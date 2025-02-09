from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QSizePolicy
from logic.Main.Chat.Message.MessageWidget import Ui_Form

class Message(QtWidgets.QWidget):
    def __init__(self, text, username):
        super(Message, self).__init__()

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.ui.UserLogo.setText(username[0])
        self.ui.Users_Name.setText(username)
        self.ui.Message_.setStyleSheet("background-color:none;")
        self.ui.Message_.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.ui.Message_.setMaximumWidth(400)
        self.ui.Message_Text.setWordWrap(True)  # 🔥 Теперь текст переносится по словам!
        self.ui.Message_Text.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.MinimumExpanding)
        self.ui.Message_Text.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextBrowserInteraction)
        self.ui.Message_Text.setText(text)
        self.ui.Message_Text.setMaximumWidth(400)
        #self.ui.Message_.setMidLineWidth(400)
        self.ui.Message_.setContentsMargins(0,0,0,0)



    def adjust_message_height(self):
        """Изменяет размер QLabel в зависимости от содержимого."""
        self.ui.Message_Text.adjustSize()  # 🔥 QLabel автоматически принимает нужный размер
        self.setFixedHeight(self.ui.Message_Text.height() + 30)

