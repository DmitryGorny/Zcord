from typing import List

from PyQt6 import QtCore
from PyQt6.QtCore import pyqtSignal

from logic.Authorization.User.chat.GroupMember import GroupMember


class MembersColumnModel(QtCore.QObject):
    add_member_view = pyqtSignal(str, str, bool, bool)

    def __init__(self, user_id):
        super(MembersColumnModel, self).__init__()
        self._user_id = str(user_id)

    def setup_members(self, members: List[GroupMember], admin_id: str) -> None:
        user_is_admin = False
        if self._user_id == str(admin_id):
            user_is_admin = True
        for member in members:
            add_kick_button = user_is_admin
            if member.user_id == self._user_id:
                add_kick_button = False

            self.add_member_view.emit(member.user_id, member.nickname, member.is_admin, add_kick_button)

