from typing import List

from PyQt6.QtCore import QObject, pyqtSignal

from logic.client.ClientConnections.ClientConnections import ClientConnections


class GroupInviteModel(QObject):  # TODO: добавить подтверждение создания группы
    show_friend_view = pyqtSignal(str, str)
    clear_friend_list_view = pyqtSignal()

    def __init__(self, user):
        super(GroupInviteModel, self).__init__()
        self._user = user

        self._group_created = False

    def create_group(self, ids: List[str]) -> None:
        if len(ids) == 0 and self._group_created:
            return
        group_name = ''
        friends = self._user.getFriends()
        group_name += self._user.getNickName()
        for fr_id in ids:
            if len(group_name) >= 10:
                break
            try:
                group_name += '_' + next(filter(lambda x: x['id'] == fr_id, friends))['nickname']
            except StopIteration:
                continue

        try:
            ClientConnections.send_service_message(group='CHAT', msg_type='CREATE-GROUP',
                                                   extra_data={'creator_id': self._user.id,
                                                               'group_name': group_name,
                                                               'is_private': True,
                                                               'is_invite_from_admin': False,
                                                               'is_password': False,
                                                               'password': '',
                                                               'members': ids
                                                               })
        except Exception as e:
            print(e)
            return
        self._group_created = True

    def show_friends(self) -> None:
        self.clear_friend_list_view.emit()
        for friend in self._user.getFriends():
            self.show_friend_view.emit(friend['id'], friend['nickname'])

    def reload_flag(self) -> None:
        self._group_created = False
