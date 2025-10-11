from typing import Callable

from PyQt6.QtCore import pyqtSignal, QObject
from typing_extensions import Protocol

from logic.client.ClientConnections.ClientConnections import ClientConnections


class IFriendListModel(Protocol):
    add_friend_view: pyqtSignal
    remove_friend_view: pyqtSignal

    def get_friends(self) -> None:
        pass

    def remove_friend(self, friend_id: str) -> None:
        pass

    def connect_remove_friend(self, callback: Callable) -> None:
        pass

    def connect_add_friend(self, callback: Callable) -> None:
        pass


class FriendListModel(QObject):
    add_friend_view = pyqtSignal(str, str)
    remove_friend_view = pyqtSignal(str)

    def __init__(self, user):
        super(FriendListModel, self).__init__()
        self._user = user

    def get_friends(self) -> None:
        if len(self._user.getFriends()) == 0:
            return #TODO: Сделать виджет отсутсвия друзей

        for friend_attrs in self._user.getFriends():
            if friend_attrs['status'] == '2':
                self.add_friend_view.emit(friend_attrs['nickname'], friend_attrs['id'])

    def remove_friend(self, friend_id) -> None:
        try:
            ClientConnections.send_service_message(msg_type="DELETE-FRIEND", extra_data={'receiver_id': friend_id,
                                                                                         'sender_id': str(self._user.id),
                                                                                         'sender_nickname': self._user.getNickName()})
            self.remove_friend_view.emit(friend_id)
        except Exception as e:
            print(e)

    def connect_remove_friend(self, callback: Callable) -> None:
        self.remove_friend_view.connect(callback)

    def connect_add_friend(self, callback: Callable) -> None:
        self.add_friend_view.connect(callback)

