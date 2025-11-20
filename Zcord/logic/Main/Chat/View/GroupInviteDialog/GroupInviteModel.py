from typing import List

from PyQt6.QtCore import QObject

from logic.client.ClientConnections.ClientConnections import ClientConnections


class GroupInviteModel(QObject):# TODO: добавить подтверждение создания группы
    def __init__(self, user):
        super(GroupInviteModel, self).__init__()
        self._user = user

    def create_group(self, ids: List[str], group_name: str) -> None:
        if len(ids) == 0:
            return

        try:
            ClientConnections.send_service_message('CREATE-GROUP', extra_data={'creator_id': self._user.id,
                                                                               'group_name': group_name,
                                                                               'is_private': True,
                                                                               'is_invite_from_admin': False,
                                                                               'is_password': False,
                                                                               'password': '',
                                                                               })
        except Exception as e:
            print(e)
