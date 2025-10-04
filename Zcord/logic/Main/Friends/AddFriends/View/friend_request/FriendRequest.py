from PyQt6 import QtWidgets

from logic.Main.Friends.AddFriends.View.friend_request.FriendQt import Ui_Form


class FriendRequest(QtWidgets.QWidget):
    def __init__(self, username, id):
        super(FriendRequest, self).__init__()

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.ui.UserIcon.setText(username[0])
        self.ui.UserNick.setText(username)

        self._friend_id = id

        self.index = 0

        self.ui.recall_request.setHidden(True) #По дефолту всегда
        self.ui.AlreadyFriend.setHidden(True)

    @property
    def friend_id(self):
        return self._friend_id

