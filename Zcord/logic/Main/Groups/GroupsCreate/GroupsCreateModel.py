from PyQt6.QtCore import QObject, pyqtSignal

from logic.client.ClientConnections.ClientConnections import ClientConnections
from logic.db_client.api_client import APIClient


class GroupsCreateModel(QObject):
    group_is_being_created_view = pyqtSignal()
    name_is_not_unique_view = pyqtSignal()
    group_created_view = pyqtSignal()

    def __init__(self, user):
        super(GroupsCreateModel, self).__init__()
        self._api_client = APIClient()
        self._user = user
        self._form_sent = False

    def send_form(self, group_name: str, is_private: bool, is_invite_from_admin: bool, is_password: bool,
                  password: str = None) -> None:
        if self._form_sent:
            return

        unique = self.check_group_name(group_name)
        if not unique:
            return

        try:
            ClientConnections.send_service_message(group='CHAT', msg_type='GROUP-CREATE',
                                                   extra_data={'group_name': group_name,
                                                               'is_private': is_private,
                                                               'is_invite_from_admin': is_invite_from_admin,
                                                               'is_password': is_password,
                                                               'password': password,
                                                               'members': []})
        except Exception as e:
            print(e)
            return
        self.group_is_being_created_view.emit()
        self._form_sent = True

    def check_group_name(self, group_name: str) -> bool:
        result = self._api_client.check_unique_group_name(group_name)
        if not result['unique']:
            self.name_is_not_unique_view.emit()
            return False
        return True

    def group_created(self) -> None:
        self.group_created_view.emit()
        self._form_sent = False
