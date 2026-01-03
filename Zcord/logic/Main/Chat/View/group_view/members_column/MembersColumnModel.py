from typing import List

from PyQt6 import QtCore
from PyQt6.QtCore import pyqtSignal

from logic.Authorization.User.chat.GroupMember import GroupMember
from logic.client.ClientConnections.ClientConnections import ClientConnections


class MembersColumnModel(QtCore.QObject):
    add_member_view = pyqtSignal(str, str, bool, bool)
    remove_user_view = pyqtSignal(str)
    clear_view = pyqtSignal()
    change_activity_view = pyqtSignal(str, str)

    def __init__(self, user_id: str, chat_id: str):
        super(MembersColumnModel, self).__init__()
        self._user_id = str(user_id)
        self._chat_id = chat_id
        self._users: List[GroupMember] | None = None

    def setup_members(self, members: List[GroupMember], admin_id: str) -> None:
        self.clear_view.emit()
        self._users = members
        for member in members:
            self.add_member(member, admin_id)

    def remove_user(self, user_id: str):
        try:
            ClientConnections.send_service_message(group='CHAT', msg_type='USER-LEFT-GROUP', extra_data={'request_receiver': user_id,
                                                                                                         'group_id': self._chat_id})
        except Exception as e:
            print('[MembersColumnModel] {}'.format(e))
            return

        self.remove_user_view.emit(user_id)

    def change_activity_status(self, member_id: str, color: str):
        for user in self._users:
            if user.user_id == member_id:
                user.online_status = color
        self.change_activity_view.emit(member_id, color)

    def add_member(self, member: GroupMember, admin_id: str) -> None:
        user_is_admin = False
        if self._user_id == str(admin_id):
            user_is_admin = True
        if member.user_id == self._user_id:
            user_is_admin = False

        self.add_member_view.emit(member.user_id, member.nickname, member.is_admin, user_is_admin)
        self.change_activity_view.emit(member.user_id, member.online_status)

