from PyQt6.QtCore import QObject, pyqtSignal

from logic.client.ClientConnections.ClientConnections import ClientConnections
from logic.db_client.api_client import APIClient


class GroupListModel(QObject):
    add_group_view = pyqtSignal(str, str, str, bool)
    remove_group_view = pyqtSignal(str)
    show_password_dialog = pyqtSignal(str)

    def __init__(self, user_id: str, user_nickname: str):
        super(GroupListModel, self).__init__()

        self._user_id = user_id
        self._user_nickname = user_nickname
        self._api_client = APIClient()

    def get_group(self, group_name: str) -> None:
        try:
            ClientConnections.send_service_message(group='CHAT', msg_type='FIND-GROUP',
                                                   extra_data={'group_name': group_name})
        except Exception as e:
            print('[GroupListModel] {}'.format(e))

    def show_group(self, group_id: str, group_name: str, users_number: str, is_password: bool):
        self.add_group_view.emit(group_id,
                                 group_name,
                                 users_number,
                                 is_password)

    def join_group(self, group_id: str, is_password: bool) -> None:
        if is_password:
            self.show_password_dialog.emit(group_id)

        try:
            ClientConnections.send_service_message(group='CHAT', msg_type='JOIN-GROUP',
                                                   extra_data={'group_id': group_id,
                                                               'nickname': self._user_nickname,
                                                               'user_id': self._user_id})
        except Exception as e:
            print(e)
        self.remove_group_view.emit(group_id)

    def send_password(self, group_id: str, password: str):
        try:
            ClientConnections.send_service_message(group='CHAT', msg_type='CHECK-GROUP-PASSWORD',
                                                   extra_data={'group_id': group_id,
                                                               'password': password,
                                                               'user_id': self._user_id})
        except Exception as e:
            print(e)
