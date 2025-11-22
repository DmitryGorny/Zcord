from typing import Dict, List

from logic.server.Service.core.enteties.Enteties import IFriend
from logic.server.Service.core.repositroies.friend_repo.IFriendRepo import IFriendRepo
from logic.server.Service.infrastructure.enteties.Enteties import Friend


class FriendRepo(IFriendRepo):
    def __init__(self):
        self._friends: Dict[str, IFriend] = {} # client_id: Friend

    @property
    def friends(self) -> dict:
        return self._friends

    def add_friend(self, client_id: str, friend_name: str, friend_id: str, status: str = '2') -> None:
        from datetime import datetime
        now = datetime.now()
        time_str = now.strftime("%Y-%m-%dT%H:%M:%S.%f")
        self._friends[client_id] = Friend(user_id=friend_id,
                                          nick=friend_name,
                                          friendship_status=status,
                                          last_online=time_str)

    def add_friends(self, client_id: str, friends: list[dict[str, str]]) -> None:
        for friend_attrs in friends:
            fr = Friend(friend_attrs['id'],  # TODO: Подумать над фабрикой
                        friend_attrs['nickname'],
                        str(friend_attrs['status']),
                        friend_attrs["last_online"])

            self._friends[client_id] = fr

    def delete_friend(self, client_id: str, friend_id: str) -> None:
        del self._friends[client_id]
