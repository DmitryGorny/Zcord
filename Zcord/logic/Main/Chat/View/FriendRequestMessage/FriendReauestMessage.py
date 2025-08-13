from PyQt6 import QtWidgets
from logic.Main.Chat.View.FriendRequestMessage.FriendRequest import Ui_Form

class FriendRequestMessage(QtWidgets.QWidget):
    def __init__(self, username, AcceptCallback, RejectCallback):
        super(FriendRequestMessage, self).__init__()

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.ui.UserLogo.setText(username[0])
        self.ui.Users_Name.setText(username)

        self.ui.Message_.setFixedWidth(500)

        self.ui.AcceptButton.clicked.connect(AcceptCallback)

        self.ui.RejectButton.clicked.connect(RejectCallback)
