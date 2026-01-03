from typing import Callable

from PyQt6.QtCore import QObject, pyqtSignal

from logic.client.ClientConnections.ClientConnections import ClientConnections


class GroupSettingsModel(QObject):
    private_group_view = pyqtSignal(bool)
    invite_from_admin_only_view = pyqtSignal(bool)
    is_password_view = pyqtSignal(bool)
    show_hide_password_view = pyqtSignal(bool)
    group_name_view = pyqtSignal(str)

    data_sent_view = pyqtSignal()
    success_sent_view = pyqtSignal()
    error_sent_view = pyqtSignal(str)

    def __init__(self, user_id: str, group_name: str, is_private: bool, is_invite_from_admin: bool, is_password: bool):
        super(GroupSettingsModel, self).__init__()
        self._user_id = user_id

        self._is_private = is_private
        self._is_invite_from_admin = is_invite_from_admin
        self._is_password = is_password
        self._group_name = group_name
        self._data_sent = False

        self._mapping = {
            'is_private': '_is_private',
            'is_password': '_is_password',
            'is_invite_from_admin': '_is_invite_from_admin',
            'group_name': '_group_name',
        }

    def _is_private_setup(self) -> None:
        self.private_group_view.emit(self._is_private)

    def _is_invite_from_admin_setup(self) -> None:
        self.invite_from_admin_only_view.emit(self._is_invite_from_admin)

    def _is_password_setup(self) -> None:
        self.is_password_view.emit(self._is_password)

    def _group_name_setup(self) -> None:
        self.group_name_view.emit(self._group_name)

    def setup_view(self):
        self._is_private_setup()
        self._is_invite_from_admin_setup()
        self._is_password_setup()
        self._group_name_setup()

    def send_changes(self, settings: dict) -> None:
        if self._data_sent:
            return

        new_args = {k: v for k, v in settings.items() if getattr(self, self._mapping[k]) != v}
        if len(new_args.values()) == 0:
            return

        try:
            ClientConnections.send_service_message(group='CHAT', msg_type='CHANGE-GROUP-SETTINGS', extra_data=new_args)
        except Exception as e:
            print('[GroupSettingsModel] {}'.format(e))
            return
        self.data_sent_view.emit()
        self._data_sent = True

    def success(self):
        self.success_sent_view.emit()
        self._data_sent = False
        self.setup_view()

    def error(self, error: str):
        self.error_sent_view.emit(error)
        self._data_sent = False
        self.setup_view()
