from typing import List

from logic.Authorization.User.chat.GroupMember import GroupMember
from logic.Main.Chat.View.group_view.members_column.MembersColumnModel import MembersColumnModel
from logic.Main.Chat.View.group_view.members_column.MembersColumnView.MembersColumnView import MembersColumnView


class MembersColumnController:
    def __init__(self, column_widget, list_widget, user, chat_id):
        self._user = user

        self._view = MembersColumnView(list_widget)
        self._model = MembersColumnModel(self._user.id, chat_id)

        self._model.add_member_view.connect(self._view.add_member)
        self._model.remove_user_view.connect(self._view.remove_user)
        self._model.clear_view.connect(self._view.clear_list)
        self._model.change_activity_view.connect(self._view.change_activity_status)

        self._view.kick_member_model.connect(self._model.remove_user)

        self._column_widget = column_widget

    def setup_members(self, members: List[GroupMember], admin_id: str) -> None:
        self._model.setup_members(members, admin_id)

    def show_hide_members_column(self) -> None:
        if self._column_widget.isHidden():
            self._column_widget.setHidden(False)
        else:
            self._column_widget.setHidden(True)

    def change_activity_color(self, member_id: str, color: str) -> None:
        self._model.change_activity_status(member_id=member_id, color=color)

    def remove_user(self, user_id: str) -> None:
        self._view.remove_user(user_id)

    def add_user(self, member: GroupMember, admin_id: str):
        self._model.add_member(member, admin_id)

    def change_admin(self, members: List[GroupMember], new_admin_id: str) -> None:
        self._model.setup_members(members, new_admin_id)
