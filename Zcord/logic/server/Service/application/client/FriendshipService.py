from logic.server.Service.core.repositroies.chat_repo.IChatRepo import IChatRepo
from logic.server.Service.core.repositroies.client_repo.IClientRepo import IClientRepo
from logic.server.Service.core.repositroies.friend_repo.IFriendRepo import IFriendRepo


class FriendshipService:
    def __init__(self, client_repo: IClientRepo, friend_repo: IFriendRepo, chat_repo: IChatRepo):
        self._client_repo: IClientRepo = client_repo
        self._friend_repo: IFriendRepo = friend_repo
        self._chat_repo: IChatRepo = chat_repo
