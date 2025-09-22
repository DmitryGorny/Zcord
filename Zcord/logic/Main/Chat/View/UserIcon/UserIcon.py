from PyQt6 import QtWidgets

from logic.Main.Chat.View.UserIcon.UserIconQt import Ui_Icon


class UserIcon(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_Icon()
        self.ui.setupUi(self)
