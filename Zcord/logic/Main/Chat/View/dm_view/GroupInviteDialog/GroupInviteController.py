from PyQt6 import QtWidgets

from logic.Main.Chat.View.dm_view.GroupInviteDialog.GroupInviteModel import GroupInviteModel
from logic.Main.Chat.View.dm_view.GroupInviteDialog.view.GroupInviteView import GroupInviteView


class GroupInviteController:
    def __init__(self, user, current_friend_id: str):
        self._view: GroupInviteView = GroupInviteView(current_friend_id)
        self._model: GroupInviteModel = GroupInviteModel(user)

        self._view.create_group_model.connect(self._model.create_group)
        self._model.show_friend_view.connect(self._view.add_friend_option)
        self._model.clear_friend_list_view.connect(self._view.clear_friends_list)

        self._model.show_friends()

    def get_widget(self) -> QtWidgets.QDialog:
        return self._view.get_widget()

    def update_friends(self):
        self._model.show_friends()

    def reload_model(self):
        self._model.reload_flag()
