from PyQt6.QtWidgets import QDialog

from logic.Main.Chat.View.group_view.GroupSettings.GroupSettingsModel import GroupSettingsModel
from logic.Main.Chat.View.group_view.GroupSettings.view.GroupSettingsView import GroupSettingsView


class GroupSettingsController:
    def __init__(self, user_id: str, group_name: str, is_private: bool, is_invite_from_admin: bool, is_password: bool):
        self._model = GroupSettingsModel(user_id, group_name, is_private, is_invite_from_admin, is_password)
        self._view = GroupSettingsView()

        self._view.save_settings_model.connect(self._model.send_changes)

        self._model.group_name_view.connect(self._view.group_name)
        self._model.is_password_view.connect(self._view.is_password)
        self._model.private_group_view.connect(self._view.private_group)
        self._model.success_sent_view.connect(self._view.data_sent_success)
        self._model.data_sent_view.connect(self._view.data_sent)
        self._model.error_sent_view.connect(self._view.data_sent_error)

    def reload_model(self):
        self._model.setup_view()

    def data_sent_success(self):
        self._model.success()

    def data_sent_error(self):
        self._model.success()

    def get_widget(self) -> QDialog:
        return self._view.show_widget()
