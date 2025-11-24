from typing import List, Dict

from logic.server.Service.core.enteties.Enteties import IFriend


class IFriendRepo:
    _clients_friends: Dict[str, IFriend]  # client_id: Friend

    def add_friend(self, client_id: str, friend_name: str, friend_id: str, status: str = '2') -> None:
        raise NotImplementedError

    def add_friends(self, client_id: str, friends: list[dict[str, str]]) -> None:
        raise NotImplementedError

    def delete_friend(self, client_id: str, friend_id: str) -> None:
        raise NotImplementedError

    def change_friendship_status(self, client_id: str, friend_id: str, status: str) -> None:
        raise NotImplementedError
