from typing import Callable

from PyQt6.QtWidgets import QDialog

from logic.Main.Chat.View.group_view.GroupSettings.GroupSettingsModel import GroupSettingsModel, GroupSettings
from logic.Main.Chat.View.group_view.GroupSettings.view.GroupInfoView.GroupInfoView import GroupInfoView
from logic.Main.Chat.View.group_view.GroupSettings.view.GroupSettingsView import GroupSettingsView


class GroupSettingsController:
    def __init__(self, date_of_creation: str):
        self._model: GroupSettingsModel | None = None
        self._settings_view = GroupSettingsView()
        self._info_view = GroupInfoView(date_of_creation)

    def init_model(self, user_id: str, group_id: str, group_name: str, is_private: bool,
                   is_invite_from_admin: bool, is_password: bool) -> None:
        self._model = GroupSettingsModel(user_id, group_id,
                                         GroupSettings(group_name=group_name,
                                                       is_private=is_private,
                                                       is_invite_from_admin=is_invite_from_admin,
                                                       is_password=is_password))
        self._connect_signals()

    def connect_permissions(self, invite_button_cb: Callable, show_settings: Callable):
        self._model.allow_invite_main_view.connect(invite_button_cb)
        self._model.show_settings_main_view.connect(show_settings)

    def setup_permissions(self, admin_id: str):
        self._model.permissions_setup(admin_id)

    def connect_allow_invite(self, cb: Callable) -> None:
        self._model.allow_invite_main_view.connect(cb)

    def _connect_signals(self):
        if self._model is None:
            return

        self._settings_view.save_settings_model.connect(self._model.send_changes)

        self._model.group_name_view.connect(self._settings_view.group_name)
        self._model.invite_from_admin_only_view.connect(self._settings_view.invite_from_admin_only)
        self._model.is_password_view.connect(self._settings_view.is_password)
        self._model.private_group_view.connect(self._settings_view.private_group)
        self._model.success_sent_view.connect(self._settings_view.data_sent_success)
        self._model.data_sent_view.connect(self._settings_view.data_sent)
        self._model.error_sent_view.connect(self._settings_view.data_sent_error)

        self._model.is_password_InfoView.connect(self._info_view.is_password)
        self._model.invite_from_admin_only_InfoView.connect(self._info_view.invite_from_admin_only)
        self._model.private_group_InfoView.connect(self._info_view.private_group)
        self._model.group_name_InfoView.connect(self._info_view.group_name)

    def reload_settings_model(self):
        self._model.setup_settings_view()

    def reload_info_model(self):
        self._model.setup_info_view()

    def data_sent_error(self, error_text: str):
        self._model.error(error_text)

    def get_settings_widget(self) -> QDialog:
        return self._settings_view.show_widget()

    def get_info_widget(self) -> QDialog:
        return self._info_view.show_widget()

    def admin_changed_settings(self, new_settings: dict) -> None:
        self._model.admin_changed_settings(new_settings)
