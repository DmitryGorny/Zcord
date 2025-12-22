from typing import List

from PyQt6 import QtCore
from PyQt6.QtCore import pyqtSignal

from logic.Authorization.User.chat.GroupMember import GroupMember
from logic.client.ClientConnections.ClientConnections import ClientConnections


class MembersColumnModel(QtCore.QObject):
    add_member_view = pyqtSignal(str, str, bool, bool)
    remove_user_view = pyqtSignal(str)

    def __init__(self, user_id: str, chat_id: str):
        super(MembersColumnModel, self).__init__()
        self._user_id = str(user_id)
        self._chat_id = chat_id

    def setup_members(self, members: List[GroupMember], admin_id: str) -> None:
        user_is_admin = False
        if self._user_id == str(admin_id):
            user_is_admin = True
        for member in members:
            add_kick_button = user_is_admin
            if member.user_id == self._user_id:
                add_kick_button = False

            self.add_member_view.emit(member.user_id, member.nickname, member.is_admin, add_kick_button)

    def remove_user(self, user_id: str):
        try:
            ClientConnections.send_service_message(group='CHAT', msg_type='USER-LEFT-GROUP', extra_data={'request_receiver': user_id,
                                                                                                         'group_id': self._chat_id})
        except Exception as e:
            print('[MembersColumnModel] {}'.format(e))
            return

        self.remove_user_view.emit(user_id)
