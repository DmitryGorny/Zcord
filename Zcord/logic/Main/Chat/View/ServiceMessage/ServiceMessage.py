from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QSizePolicy

from logic.Main.Chat.View.ServiceMessage.ServiceMessageQt import Ui_ServiceMessage


class ServiceMessage(QtWidgets.QWidget):
    def __init__(self, text):
        super(ServiceMessage, self).__init__()

        self.ui = Ui_ServiceMessage()
        self.ui.setupUi(self)
        self.ui.Message_Text.setWordWrap(True)
        self.ui.Message_Text.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextBrowserInteraction)
        self.ui.Message_Text.setText(text)
        # self.ui.Message_.setMidLineWidth(400)
        self.ui.Message_.setContentsMargins(0, 0, 0, 0)

    def adjust_message_height(self):
        """Изменяет размер QLabel в зависимости от содержимого."""
        self.ui.Message_Text.adjustSize()  # 🔥 QLabel автоматически принимает нужный размер
        self.setFixedHeight(self.ui.Message_Text.height() + 10)
