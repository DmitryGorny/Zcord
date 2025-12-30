class GroupMember:
    def __init__(self, user_id: str, nickname: str, is_admin: bool):  # TODO: Это сырая весрия, потом переработать под другие роли
        self._id = user_id
        self._nickname = nickname
        self._is_admin = is_admin
        self._online_status: str = 'grey'

    @property
    def user_id(self) -> str:
        return self._id

    @property
    def nickname(self) -> str:
        return self._nickname

    @property
    def online_status(self) -> str:
        return self._online_status

    @online_status.setter
    def online_status(self, color: str) -> None:
        self._online_status = color

    @property
    def is_admin(self):
        return self._is_admin

    @is_admin.setter
    def is_admin(self, val: bool):
        self._is_admin = val

    def get_props(self) -> dict[str]:
        return {'member_id': self._id, 'member_nickname': self._nickname}

    def __str__(self):
        return f'{self.user_id}'
