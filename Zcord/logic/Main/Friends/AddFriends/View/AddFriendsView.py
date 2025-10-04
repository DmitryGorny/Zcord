import typing
from abc import ABC, abstractmethod
from typing import Dict, Callable

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import pyqtSignal, QTimer

from logic.Main.Friends.AddFriends.View.AddFriendQt import Ui_AddFriend
from logic.Main.Friends.AddFriends.View.friend_request.FriendRequest import FriendRequest


class IAddFriendView(typing.Protocol):
    send_request_model: pyqtSignal
    find_user_model: pyqtSignal
    recall_request_model: pyqtSignal

    def add_found_friend(self, friend_nick: str, friend_id: str) -> None:
        pass

    def request_sent(self, username: str) -> None:
        pass

    def recall_request(self, username: str) -> None:
        pass

    def get_widget(self) -> QtWidgets.QFrame:
        pass

    def get_nickname_data(self) -> str:
        pass

    def user_is_already_friend(self) -> None:
        pass

    def request_already_sent(self) -> None:
        pass

    def remove_request_widget(self, username: str) -> None:
        pass

    def connect_send_signal(self, callback: Callable) -> None:
        pass

    def connect_find_user_signal(self, callback: Callable) -> None:
        pass

    def connect_recall_request_signal(self, callback: Callable) -> None:
        pass


class AddFriendView(QtWidgets.QWidget):
    send_request_model = pyqtSignal(str, str)
    find_user_model = pyqtSignal(str)
    recall_request_model = pyqtSignal(str, str)

    def __init__(self):
        super(AddFriendView, self).__init__()

        self._ui = Ui_AddFriend()
        self._ui.setupUi(self)

        self._ui.FriendScroll.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self._ui.FriendScroll.setSelectionMode(QtWidgets.QListWidget.SelectionMode.NoSelection)

        self._friends_requests: Dict[str, FriendRequest] = {}

        def search():
            self._ui.FriendScroll.clear()
            self._friends_requests.clear()
            self.find_user_model.emit(self._ui.nickname_input.text().strip())

        self._ui.Search_button.clicked.connect(search)

    def add_found_friend(self, friend_nick: str, friend_id: str) -> None:
        item = QtWidgets.QListWidgetItem(self._ui.FriendScroll)
        friend_widget = FriendRequest(friend_nick, friend_id)

        def on_send():
            self.send_request_model.emit(friend_nick, friend_id)
            if friend_widget.ui.recall_request:
                self._block_button(friend_widget.ui.recall_request)

        def on_recall():
            self.recall_request_model.emit(friend_nick, friend_id)
            if friend_widget.ui.send_request:
                self._block_button(friend_widget.ui.send_request)

        friend_widget.ui.send_request.clicked.connect(on_send)
        friend_widget.ui.recall_request.clicked.connect(on_recall)

        item.setSizeHint(friend_widget.sizeHint())
        self._ui.FriendScroll.addItem(item)
        self._ui.FriendScroll.setItemWidget(item, friend_widget.ui.Friend_wrapper)

        if friend_nick not in self._friends_requests.keys():
            self._friends_requests[friend_nick] = friend_widget
            friend_widget.index = self._ui.FriendScroll.count() - 1

    def _block_button(self, button: QtWidgets.QPushButton, delay: int = 3000) -> None:
        button.setEnabled(False)

        def enable_button():
            try:
                button.setEnabled(True)
            except RuntimeError:
                return

        QTimer.singleShot(delay, enable_button)

    def request_sent(self, username: str) -> None:
        self._friends_requests[username].ui.send_request.setHidden(True)
        self._friends_requests[username].ui.recall_request.setHidden(False)

    def recall_request(self, username: str) -> None:
        self._friends_requests[username].ui.send_request.setHidden(False)
        self._friends_requests[username].ui.recall_request.setHidden(True)

    def get_widget(self) -> QtWidgets.QFrame:
        return self._ui.Column

    def request_already_sent(self, username: str) -> None:
        self._friends_requests[username].ui.send_request.setHidden(True)
        self._friends_requests[username].ui.recall_request.setHidden(True)
        self._friends_requests[username].ui.AlreadyFriend.setText("Заявка отправлена")
        self._friends_requests[username].ui.AlreadyFriend.setHidden(False)

    def remove_request_widget(self, username: str) -> None:
        try:
            fr_widget = self._friends_requests[username]
            item = self._ui.FriendScroll.takeItem(fr_widget.index)
            widget = self._ui.FriendScroll.itemWidget(item)
            self._ui.FriendScroll.removeItemWidget(item)
            if widget:
                widget.deleteLater()
            del self._friends_requests[username]
        except Exception: #TODO: Выбрать правильный тип ошибки
            return

    def get_nickname_data(self) -> str:
        return self._ui.nickname_input.text().strip()

    def user_is_already_friend(self, username) -> None:
        self._friends_requests[username].ui.send_request.setHidden(True)
        self._friends_requests[username].ui.recall_request.setHidden(True)
        self._friends_requests[username].ui.AlreadyFriend.setHidden(False)

    def connect_send_signal(self, callback: Callable) -> None:
        self.send_request_model.connect(callback)

    def connect_find_user_signal(self, callback: Callable) -> None:
        self.find_user_model.connect(callback)

    def connect_recall_request_signal(self, callback: Callable) -> None:
        self.recall_request_model.connect(callback)
