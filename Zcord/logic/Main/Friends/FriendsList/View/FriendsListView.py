from typing import Dict, Callable

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import pyqtSignal
from typing_extensions import Protocol

from logic.Main.Friends.FriendsList.View.FriendWidget.FriendWidget import FriendWidget
from logic.Main.Friends.FriendsList.View.FriendsListQt import Ui_Form


class IFriendListView(Protocol):
    remove_friend_model: pyqtSignal
    add_friends: pyqtSignal

    def add_friend(self, username: str, friend_id: str) -> None:
        pass

    def remove_friend(self, friend_id: str) -> None:
        pass

    def get_widget(self) -> QtWidgets.QFrame:
        pass

    def clear_scroll(self) -> None:
        pass

    def connect_remove_friend(self, callback: Callable) -> None:
        pass

    def connect_add_friends(self, callback: Callable) -> None:
        pass


class FriendListView(QtWidgets.QWidget):
    add_friends = pyqtSignal()
    remove_friend_model = pyqtSignal(str)

    def __init__(self):
        super(FriendListView, self).__init__()

        self._ui = Ui_Form()
        self._ui.setupUi(self)

        self._friends: Dict[str, QtWidgets.QWidget] = {}

        self._ui.friends_list.setSpacing(10)
        self._ui.friends_list.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self._ui.friends_list.setSelectionMode(QtWidgets.QListWidget.SelectionMode.NoSelection)

    def add_friend(self, username: str, friend_id: str) -> None:
        req = FriendWidget(username, friend_id)

        if friend_id not in self._friends.keys():
            self._friends[friend_id] = req

        req.connect_delete_friend_button(lambda: self.remove_friend_model.emit(friend_id))

        item = QtWidgets.QListWidgetItem()
        item.setSizeHint(req.get_widget().sizeHint())
        self._ui.friends_list.addItem(item)
        self._ui.friends_list.setItemWidget(item, req.get_widget())
        req.index = self._ui.friends_list.count() - 1

    def remove_friend(self, friend_id: str) -> None:
        if friend_id not in self._friends.keys():
            return

        widget = self._friends[friend_id]

        item = self._ui.friends_list.takeItem(widget.index)
        widget = self._ui.friends_list.itemWidget(item)
        self._ui.friends_list.removeItemWidget(item)
        if widget:
            widget.deleteLater()
        del self._friends[friend_id]

    def get_widget(self) -> QtWidgets.QFrame:
        return self._ui.Column

    def connect_remove_friend(self, callback: Callable) -> None:
        self.remove_friend_model.connect(callback)

    def clear_scroll(self) -> None:
        self._ui.friends_list.clear()

    def connect_add_friends(self, callback: Callable) -> None:
        self.add_friends.connect(callback)
