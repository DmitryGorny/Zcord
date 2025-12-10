from typing import List

from PyQt6.QtCore import QObject, pyqtSignal

from logic.client.ClientConnections.ClientConnections import ClientConnections
from logic.db_client.api_client import APIClient


class UserInviteModel(QObject):
    show_friend_view = pyqtSignal(str, str)
    clear_friend_list_view = pyqtSignal()

    def __init__(self, user, current_group_id: str):
        super(UserInviteModel, self).__init__()
        self._user = user

        self._invite_sent = False
        self._api_client = APIClient()
        self._group = self._group_setter(current_group_id)

    def _group_setter(self, current_group_id) -> str:
        group = self._api_client.get_chat_by_id(chat_id=int(current_group_id))
        if group is None:
            print('[UserInviteModel] группа с id {} не найдена'.format(current_group_id))
            return '0'
        return group['group']

    def invite_user(self, ids: List[str]) -> None:
        if self._group == '0':
            return

        if len(ids) == 0 and self._invite_sent:
            return

        friends = self._user.getFriends()
        for fr_id in ids:
            try:
                friend_id = next(filter(lambda x: x['id'] == fr_id, friends))['id']
            except StopIteration:
                continue
            try:
                next(filter(lambda x: str(x['user_id']) == friend_id, self._group['users']))
                print('[UserInviteModel] user is already in group')
                return
            except StopIteration:
                try:
                    ClientConnections.send_service_message(group='CHAT', msg_type='SEND-GROUP-INVITE',
                                                           extra_data={'sender_id': self._user.id,
                                                                       'receiver_id': friend_id,
                                                                       'group_id': self._group['id'],
                                                                       })
                except Exception as e:
                    print('[UserInviteModel] {}'.format(e))
                    return
            self._invite_sent = True

    def show_friends(self) -> None:
        self.clear_friend_list_view.emit()
        for friend in self._user.getFriends():
            try:
                next(filter(lambda x: str(x['user_id']) == friend['id'], self._group['users']))
                print('[UserInviteModel] user is already in group')
                continue
            except StopIteration:
                self.show_friend_view.emit(friend['id'], friend['nickname'])

    def reload_flag(self) -> None:
        self._invite_sent = False
