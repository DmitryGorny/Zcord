from typing import Callable

from PyQt6 import QtWidgets

from logic.Main.Friends.FriendsList.View.FriendWidget.FriendWidgetQt import Ui_FriendWidgetQt


class FriendWidget(QtWidgets.QWidget):
    def __init__(self, username: str, user_id: str):
        super(FriendWidget, self).__init__()

        self._ui = Ui_FriendWidgetQt()
        self._ui.setupUi(self)

        self._username = username
        self._user_id = user_id

        self._ui.UserNick.setText(self._username)
        self._ui.UserIcon.setText(self._username[0])
        self.index = 0

    def connect_delete_friend_button(self, callback: Callable) -> None:
        self._ui.delete_friend.clicked.connect(callback)

    @property
    def username(self) -> str:
        return self._username

    @property
    def user_id(self) -> str:
        return self._user_id

    def get_widget(self) -> QtWidgets.QFrame:
        return self._ui.Friend_wrapper
