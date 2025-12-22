from PyQt6 import QtWidgets
from logic.Main.Chat.View.group_view.UserInviteDialog.UserInviteModel import UserInviteModel
from logic.Main.Chat.View.group_view.UserInviteDialog.view.UserInviteView import UserInviteView


class UserInviteController:
    def __init__(self, user, current_group_id: str, group_members: list):
        self._view: UserInviteView = UserInviteView()
        self._model: UserInviteModel = UserInviteModel(user, current_group_id, group_members)

        self._view.invite_user_model.connect(self._model.invite_user)
        self._model.show_friend_view.connect(self._view.add_friend_option)
        self._model.clear_friend_list_view.connect(self._view.clear_friends_list)

        self._model.show_friends()

    def get_widget(self) -> QtWidgets.QDialog:
        return self._view.get_widget()

    def update_friends(self):
        self._model.show_friends()

    def reload_model(self):
        self._model.reload_flag()
        self._model.show_friends()
