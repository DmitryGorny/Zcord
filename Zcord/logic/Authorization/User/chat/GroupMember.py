class GroupMember:
    def __init__(self, user_id: str, nickname: str, is_admin: bool):  # TODO: Это сырая весрия, потом переработать под другие роли
        self._id = user_id
        self._nickname = nickname
        self._is_admin = is_admin

    @property
    def user_id(self) -> str:
        return self._id

    @property
    def nickname(self) -> str:
        return self._nickname

    @property
    def is_admin(self):
        return self._is_admin

    def __str__(self):
        return f'{self._id}'
