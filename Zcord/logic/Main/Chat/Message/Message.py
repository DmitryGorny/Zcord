from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QSizePolicy
from logic.Main.Chat.Message.MessageWidget import Ui_Form

class Message(QtWidgets.QDialog):
    def __init__(self, text, username):
        super(Message, self).__init__()

        self.ui = Ui_Form()

        self.ui.setupUi(self)

        self.ui.UserLogo.setText(username[0])
        self.ui.Users_Name.setText(username)

        self.ui.Message_Text.setMaximumHeight(50)
        self.ui.Message_Text.setText(text)

        self.ui.Message_.setMidLineWidth(400)
        self.ui.Message_.setContentsMargins(0,0,0,0)


class ExpandingTextEdit(QtWidgets.QTextEdit):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.setMinimumHeight(50)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # Отключаем вертикальную прокрутку
        #self.textChanged.connect(self.adjustHeight)  # Подключаем сигнал изменения текста к методу

    #def adjustHeight(self):
        # Вычисляем высоту содержимого
        #document_height = self.document().size().height()
        #self.setFixedHeight(document_height + 1)




