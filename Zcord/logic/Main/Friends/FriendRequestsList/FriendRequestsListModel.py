from PyQt6.QtCore import QObject, pyqtSignal
from typing import Dict, Protocol, Callable

from logic.client.ClientConnections.ClientConnections import ClientConnections
from logic.db_client.api_client import APIClient


class IFriendRequestListModel(Protocol):
    get_my_requests_view: pyqtSignal
    get_others_requests_view: pyqtSignal
    remove_others_request_view: pyqtSignal
    remove_your_request_view: pyqtSignal

    def get_your_requests(self) -> None:
        pass

    def get_others_request(self) -> None:
        pass

    def accept_request(self) -> None:
        pass

    def decline_request(self) -> None:
        pass

    def recall_friend_request(self) -> None:
        pass

    def connect_my_requests_view(self, callback: Callable) -> None:
        pass

    def connect_remove_others_request(self, callback: Callable) -> None:
        pass

    def connect_remove_your_request(self, callback: Callable) -> None:
        pass

    def connect_others_requests_view(self, callback: Callable) -> None:
        pass


class FriendRequestListModel(QObject):
    get_my_requests_view = pyqtSignal(str, str)
    remove_others_request_view = pyqtSignal(str)
    remove_your_request_view = pyqtSignal(str)
    get_others_requests_view = pyqtSignal(str, str)

    def __init__(self, user):
        super(FriendRequestListModel, self).__init__()
        self._api_client: APIClient = APIClient()
        self._user = user

    def get_your_requests(self) -> None:
        your_requests = self._api_client.get_your_friend_request(self._user.id)

        if your_requests is None:
            return  # TODO: Сделать вариант без заявки

        for request in your_requests:
            friend = self._api_client.get_user_by_id(request['receiver'])

            self.get_my_requests_view.emit(friend['nickname'], str(friend['id']))

    def get_others_request(self):
        others_requests = self._api_client.get_others_friend_request(self._user.id)

        if others_requests is None:
            return  # TODO: Сделать вариант без заявки

        for request in others_requests:
            friend = self._api_client.get_user_by_id(request['sender'])

            self.get_others_requests_view.emit(friend['nickname'], str(friend['id']))

    def decline_request(self, user_id: str) -> None:
        try:
            ClientConnections.send_service_message(msg_type="DECLINE-FRIEND", extra_data={'receiver_id': self._user.id,
                                                                                          'sender_id': user_id})
            self.remove_others_request_view.emit(user_id)
        except Exception as e:
            print(e)

    def accept_request(self, user_id: str) -> None:
        try:
            ClientConnections.send_service_message(msg_type="ACCEPT-FRIEND", extra_data={'receiver_id': str(self._user.id),
                                                                                         'sender_id': user_id})
            self.remove_others_request_view.emit(user_id)
        except Exception as e:
            print(e)

    def recall_friend_request(self, user_id: str) -> None:
        try:
            ClientConnections.send_service_message(msg_type="FRIENDSHIP-REQUEST-RECALL",
                                                   extra_data={'friend_id': str(user_id),
                                                               'sender_id': str(self._user.id)})
            self.remove_your_request_view.emit(user_id)
        except Exception as e:
            print(e)

    def connect_my_requests_view(self, callback: Callable) -> None:
        self.get_my_requests_view.connect(callback)

    def connect_remove_others_request(self, callback: Callable) -> None:
        self.remove_others_request_view.connect(callback)

    def connect_remove_your_request(self, callback: Callable) -> None:
        self.remove_your_request_view.connect(callback)

    def connect_others_requests_view(self, callback: Callable) -> None:
        self.get_others_requests_view.connect(callback)
