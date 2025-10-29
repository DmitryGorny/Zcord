from abc import ABC, abstractmethod
from logic.Authorization.User.friend.Friend import Friend


class FriendFabric(ABC):
    @abstractmethod
    def create_friend(self, **kwargs) -> Friend:
        pass


class CreateFriend(FriendFabric):
    def create_friend(self, **kwargs) -> Friend:
        return Friend(kwargs['user_id'], kwargs['user_nickname'], kwargs['status'], kwargs['last_online'])
