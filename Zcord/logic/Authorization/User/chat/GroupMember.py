class GroupMember:
    def __init__(self, user_id: str, nickname: str, ):
        self._id = user_id
        self._nickname = nickname

    @property
    def user_id(self) -> str:
        return self._id

    @property
    def nickname(self) -> str:
        return self._nickname

    def __str__(self):
        return f'{self._id}'
