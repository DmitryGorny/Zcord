from typing import Dict, List

from logic.server.Service.core.enteties.Enteties import IFriend
from logic.server.Service.core.repositroies.friend_repo.IFriendRepo import IFriendRepo
from logic.server.Service.infrastructure.enteties.Enteties import Friend


class FriendRepo(IFriendRepo):
    def __init__(self):
        self._friends: Dict[str, list[IFriend]] = {}  # client_id: [Friend]

    def add_friend(self, client_id: str, friend_name: str, friend_id: str, status: str = '2') -> None:
        from datetime import datetime
        now = datetime.now()
        time_str = now.strftime("%Y-%m-%dT%H:%M:%S.%f")

        if client_id not in self._friends:
            self._friends[client_id] = []
        self._friends[client_id].append(Friend(user_id=friend_id,
                                               nick=friend_name,
                                               friendship_status=status,
                                               last_online=time_str))

    def add_friends(self, client_id: str, friends: list[dict[str, str]]) -> None:
        if client_id not in self._friends:
            self._friends[client_id] = []

        for friend_attrs in friends:
            fr = Friend(friend_attrs['id'],  # TODO: Подумать над фабрикой
                        friend_attrs['nickname'],
                        str(friend_attrs['status']),
                        friend_attrs["last_online"])

            self._friends[client_id].append(fr)

    def delete_friend(self, client_id: str, friend_id: str) -> None:
        if client_id in self._friends.keys():
            for fr in self._friends[client_id]:
                if fr.id == friend_id:
                    self._friends[client_id].remove(fr)

        if friend_id in self._friends.keys():
            for fr in self._friends[client_id]:
                if fr.id == friend_id:
                    self._friends[client_id].remove(fr)

    def change_friendship_status(self, client_id: str, friend_id: str, status: str) -> None:
        if client_id not in self._friends.keys():
            return
        try:
            friend = next(filter(lambda x: x.id == str(friend_id), self._friends[client_id]))
            friend.friendship_status = status
        except StopIteration as e:
            print(e)
            return

    def get_client_friends(self, client_id: str) -> List[IFriend]:
        return self._friends[client_id]
