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

    def get_groups(self) -> None:
        groups = self._api_client.get_groups()
        for group in groups:
            try:
                next(filter(lambda x: x.get('user_id') == str(self._user_id), group.get("users")))
            except StopIteration:
                self.add_group_view.emit(str(group.get('id')),
                                         group.get('group_name'),
                                         str(len(group.get('users'))),
                                         group.get('is_password'))

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
