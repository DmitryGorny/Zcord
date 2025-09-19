from logic.Authorization.User.User import BaseUser


class Friend(BaseUser):
    def __init__(self, user_id: int, user_nickname: str, chat_id: int, status: int, last_online):
        super(Friend, self).__init__(user_id, user_nickname, last_online)
        self._chat_id: int = chat_id
        self._status = status

    @property
    def chat_id(self):
        return self._chat_id

    @property
    def status(self):
        return self._status
