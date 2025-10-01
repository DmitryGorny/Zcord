from typing import Callable

from PyQt6 import QtWidgets

from logic.Main.Friends.FriendRequestsList.View.OthersRequest.OthersRequestQt import Ui_Form


class OtherRequest(QtWidgets.QWidget):
    def __init__(self, nickname: str, user_id: str):
        super(OtherRequest, self).__init__()

        self._ui = Ui_Form()
        self._ui.setupUi(self)

        self._nickname = nickname
        self._user_id = user_id
        self._index = 0

        self._ui.UserNick.setText(nickname)
        self._ui.UserIcon.setText(nickname[0])

    def connect_decline_request(self, callback: Callable):
        self._ui.decline_request.clicked.connect(callback)

    def connect_accept_request(self, callback: Callable):
        self._ui.accept_request.clicked.connect(callback)

    @property
    def nickname(self):
        return self._nickname

    @property
    def user_id(self):
        return self.user_id

    @property
    def index(self) -> int:
        return self._index

    @index.setter
    def index(self, val: int) -> None:
        self._index = val

    def get_widget(self) -> QtWidgets.QFrame:
        return self._ui.Friend_wrapper
