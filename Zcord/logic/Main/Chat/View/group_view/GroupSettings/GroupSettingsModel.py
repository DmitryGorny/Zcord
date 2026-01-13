import json
from dataclasses import dataclass
from typing import Callable

from PyQt6.QtCore import QObject, pyqtSignal
from logic.client.ClientConnections.ClientConnections import ClientConnections


@dataclass
class GroupSettings:
    group_name: str
    is_private: bool
    is_invite_from_admin: bool
    is_password: bool


class GroupSettingsModel(QObject):
    # Сигналы для отображения данных в окне настройки группы
    private_group_view = pyqtSignal(bool)
    invite_from_admin_only_view = pyqtSignal(bool)
    is_password_view = pyqtSignal(bool)
    show_hide_password_view = pyqtSignal(bool)
    group_name_view = pyqtSignal(str)
    data_sent_view = pyqtSignal()
    success_sent_view = pyqtSignal()
    error_sent_view = pyqtSignal(str)

    # Сигналы для отображения данных в окне информации о группе
    private_group_InfoView = pyqtSignal(bool)
    invite_from_admin_only_InfoView = pyqtSignal(bool)
    is_password_InfoView = pyqtSignal(bool)
    group_name_InfoView = pyqtSignal(str)

    # Сигналы изменения интерфейса в зависимости от настроек группы
    allow_invite_main_view = pyqtSignal(bool)
    show_settings_main_view = pyqtSignal(bool)

    def __init__(self, user_id: str, group_id: str, settings: GroupSettings):
        super(GroupSettingsModel, self).__init__()
        self._user_id = user_id

        self._settings_dto = settings

        self._group_id = group_id

        self._data_sent = False

    def _is_private_setup(self) -> None:
        self.private_group_view.emit(self._settings_dto.is_private)

    def _is_invite_from_admin_setup(self) -> None:
        self.invite_from_admin_only_view.emit(self._settings_dto.is_invite_from_admin)

    def _is_password_setup(self) -> None:
        self.is_password_view.emit(self._settings_dto.is_password)

    def _group_name_setup(self) -> None:
        self.group_name_view.emit(self._settings_dto.group_name)

    def _is_private_info_setup(self) -> None:
        self.private_group_InfoView.emit(self._settings_dto.is_private)

    def _is_invite_from_admin_info_setup(self) -> None:
        self.invite_from_admin_only_InfoView.emit(self._settings_dto.is_invite_from_admin)

    def _is_password_info_setup(self) -> None:
        self.is_password_InfoView.emit(self._settings_dto.is_password)

    def _group_name_info_setup(self) -> None:
        self.group_name_InfoView.emit(self._settings_dto.group_name)

    def _allow_invites(self):
        self.allow_invite_main_view.emit(self._settings_dto.is_invite_from_admin)

    def setup_settings_view(self):
        self._is_private_setup()
        self._is_invite_from_admin_setup()
        self._is_password_setup()
        self._group_name_setup()

    def setup_info_view(self):
        self._is_private_info_setup()
        self._is_invite_from_admin_info_setup()
        self._is_password_info_setup()
        self._group_name_info_setup()

    def permissions_setup(self, admin_id: str):
        if str(admin_id) == str(self._user_id):
            self.allow_invite_main_view.emit(False)
            self.show_settings_main_view.emit(True)
            return
        self.allow_invite_main_view.emit(self._settings_dto.is_invite_from_admin)
        self.show_settings_main_view.emit(False)

    def send_changes(self, settings: dict, flags: dict) -> None:
        if self._data_sent:
            return

        new_args = {k: v for k, v in settings.items() if getattr(self._settings_dto, k) != v}
        if len(new_args.values()) == 0:
            return
        flags = json.dumps(flags)
        new_args = json.dumps(settings)
        try:
            ClientConnections.send_service_message(group='CHAT', msg_type='CHANGE-GROUP-SETTINGS', extra_data={
                'new_settings': new_args,
                'group_id': self._group_id,
                'flags': flags})
        except Exception as e:
            print('[GroupSettingsModel] {}'.format(e))
            return
        self.data_sent_view.emit()
        self._data_sent = True

    def success(self):
        self.success_sent_view.emit()
        self._data_sent = False

    def error(self, error: str):
        self.error_sent_view.emit(error)
        self._data_sent = False
        self.setup_info_view()
        self.setup_settings_view()

    def admin_changed_settings(self, new_settings: dict):
        for k, v in new_settings.items():
            value = getattr(self._settings_dto, k, None)
            if value is None:
                continue
            if value != v:
                setattr(self._settings_dto, k, v)
        self.setup_settings_view()
        self.setup_info_view()
        self.success()

