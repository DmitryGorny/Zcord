from typing import List

from logic.Authorization.User.chat.GroupMember import GroupMember
from logic.Main.Chat.View.group_view.members_column.MembersColumnModel import MembersColumnModel
from logic.Main.Chat.View.group_view.members_column.MembersColumnView.MembersColumnView import MembersColumnView


class MembersColumnController:
    def __init__(self, column_widget, list_widget, user):
        self._user = user

        self._view = MembersColumnView(list_widget)
        self._model = MembersColumnModel(self._user.id)

        self._model.add_member_view.connect(self._view.add_member)

        self._column_widget = column_widget

    def setup_members(self, members: List[GroupMember], admin_id: str) -> None:
        self._model.setup_members(members, admin_id)

    def show_hide_members_column(self) -> None:
        if self._column_widget.isHidden():
            self._column_widget.setHidden(False)
        else:
            self._column_widget.setHidden(True)

    def change_activity_color(self, member_id: str, color: str) -> None:
        self._view.change_activity_status(member_id=member_id, color=color)
