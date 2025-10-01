import typing
from typing import List, Callable, Dict

from PyQt6.QtCore import QObject, pyqtSignal

from logic.Authorization.User.User import User
from logic.client.ClientConnections.ClientConnections import ClientConnections
from logic.db_client.api_client import APIClient


class IAddFriendModel(typing.Protocol):
    user_found_view: pyqtSignal
    request_sent_view: pyqtSignal
    recall_request_view: pyqtSignal
    request_already_sent_view: pyqtSignal

    def get_friend_by_nick(self, nickname: str) -> None:
        pass

    def send_friend_request(self, friend_nick: str, user_id: str) -> None:
        pass

    def recall_friend_request(self, username: str, user_id: int) -> None:
        pass

    def connect_user_found(self, callback: Callable) -> None:
        pass

    def connect_request_sent(self, callback: Callable) -> None:
        pass

    def connect_recall_sent(self, callback: Callable) -> None:
        pass

    def connect_already_friend(self, callback: Callable) -> None:
        pass

    def connect_already_sent_request(self, callback: Callable) -> None:
        pass


class AddFriendModel(QObject):
    user_found_view = pyqtSignal(str, str)
    request_sent_view = pyqtSignal(str)
    recall_request_view = pyqtSignal(str)
    already_friend_view = pyqtSignal(str)
    request_already_sent_view = pyqtSignal(str)

    def __init__(self, user):
        super().__init__()
        self._api_client: APIClient = APIClient()
        self._user = user

    def get_friend_by_nick(self, nickname: str) -> None:
        if len(nickname) != 0:
            try:
                user = self._api_client.get_user(nickname)[0]
            except IndexError:
                # TODO: Сделать вывод виджета для оповещения юзера об отсуствущих найденных юзерах
                return
            print(len(self._api_client.get_friend_request(self._user.id, user['id'])))
            already_exist = self._api_client.get_friend_request(self._user.id, user['id'])

            if user['id'] == self._user.id:
                return

            self.user_found_view.emit(user['nickname'], str(user['id']))

            if len(already_exist) != 0:
                self.request_already_sent_view.emit(nickname)
                return

            if already_exist is None:
                for friend in self._user.getFriends():
                    if friend['id'] == str(user['id']):
                        if friend['status'] == '1':
                            self.request_already_sent_view.emit(nickname)
                            break
                        self.already_friend_view.emit(nickname)
                        break

    def send_friend_request(self, friend_nick: str, user_id: str) -> None:
        try:
            ClientConnections.send_service_message(msg_type="FRIENDSHIP-REQUEST-SEND",
                                                   extra_data={'friend_id': str(user_id),
                                                               'user_id': str(self._user.id),
                                                               'friend_nick': friend_nick,
                                                               'sender_nick': self._user.getNickName()})
        except Exception as e:
            print(e)
            return

        self.request_sent_view.emit(friend_nick)

    def recall_friend_request(self, username: str, user_id: int) -> None:
        try:
            ClientConnections.send_service_message(msg_type="FRIENDSHIP-REQUEST-RECALL",
                                                   extra_data={'friend_id': str(user_id),
                                                               'sender_id': str(self._user.id)})
        except Exception as e:
            print(e)
            return

        self.recall_request_view.emit(username)

    def connect_user_found(self, callback: Callable) -> None:
        self.user_found_view.connect(callback)

    def connect_request_sent(self, callback: Callable) -> None:
        self.request_sent_view.connect(callback)

    def connect_recall_sent(self, callback: Callable) -> None:
        self.recall_request_view.connect(callback)

    def connect_already_friend(self, callback: Callable) -> None:
        self.already_friend_view.connect(callback)

    def connect_already_sent_request(self, callback: Callable) -> None:
        self.request_already_sent_view.connect(callback)
