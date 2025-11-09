from typing import Protocol, Callable

from PyQt6.QtCore import QObject, pyqtSignal

from logic.client.ClientConnections.ClientConnections import ClientConnections
from logic.db_client.api_client import APIClient


class IGroupRequestModel(Protocol):
    add_request_view: pyqtSignal
    remove_request_view: pyqtSignal

    def accept_request(self) -> None:
        pass

    def reject_request(self) -> None:
        pass

    def get_groups_rejects(self) -> None:
        pass

    def connect_add_requests(self, cb: Callable) -> None:
        pass

    def connect_remove_requests(self, cb: Callable) -> None:
        pass


class GroupRequestModel(QObject):
    add_request_view = pyqtSignal(str, str, str)
    remove_request_view = pyqtSignal(str)

    def __init__(self, user):
        super(GroupRequestModel, self).__init__()
        self._api_client = APIClient()
        self._user = user

    def accept_request(self, group_id: str, request_id: str) -> None:
        try:
            ClientConnections.send_service_message(msg_type='GROUP-REQUEST-ACCEPTED',
                                                   extra_data={'group_id': group_id,
                                                               'request_id': request_id})
        except Exception as e:
            print(e)
        self.remove_request_view.emit(group_id)

    def reject_request(self, group_id: str, request_id: str) -> None:
        try:
            ClientConnections.send_service_message(msg_type='GROUP-REQUEST-REJECTED',
                                                   extra_data={'group_id': group_id,
                                                               'request_id': request_id})
        except Exception as e:
            print(e)
        self.remove_request_view.emit(group_id)

    def get_groups_rejects(self) -> None:
        group_requests = self._api_client.get_groups_requests_by_receiver_id(str(self._user.id))
        for request in group_requests:
            self.add_request_view.emit(str(request['group']['id']), request['group']['group_name'], str(request['id']))

    def connect_add_requests(self, cb: Callable) -> None:
        self.add_request_view.connect(cb)

    def connect_remove_requests(self, cb: Callable) -> None:
        self.remove_request_view.connect(cb)
