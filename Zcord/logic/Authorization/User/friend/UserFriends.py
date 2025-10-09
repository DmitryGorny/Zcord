from typing import List

from logic.db_client.api_client import APIClient


class UserFriends:
    def __init__(self, user):
        from logic.Authorization.User.friend.Friend import Friend
        self._friends: List[Friend] = []
        self._db = APIClient()
        self._user = user

    def init_friends(self):
        from logic.Authorization.User.friend.fabric import CreateFriend
        fabric = CreateFriend()
        for friendship in self._db.get_friendships_by_nickname(self._user.getNickName()):
            chat_id = friendship['id']
            status = friendship['status']
            friend_data = self._db.get_user_by_id(
                friendship['user1'] if friendship['user1'] != self._user.id else friendship['user2'])
            friend = fabric.create_friend(chat_id=chat_id,
                                          user_nickanme=friend_data["nickname"],
                                          status=status,
                                          user_id=friend_data["id"],
                                          last_online=friend_data["last_online"])
            self._friends.append(friend)

    def add_friend(self, chat_id: str, user_nickname: str, user_id: str, last_online: str, status: str = '2'):
        from logic.Authorization.User.friend.fabric import CreateFriend
        fabric = CreateFriend()
        friend = fabric.create_friend(chat_id=chat_id,
                                      user_nickanme=user_nickname,
                                      status=status,
                                      user_id=user_id,
                                      last_online=last_online)
        self._friends.append(friend)

    def friends_props(self) -> dict[str, str]:
        """Поочередно возвращает атрибуты каждого класса"""
        for friend in self._friends:
            yield {"id": str(friend.id),
                   "chat_id": str(friend.chat_id),
                   "nickname": friend.getNickName(),
                   "status": str(friend.status),
                   "last_online": friend.last_online}

    def delete_friend(self, friend_id: str):
        try:
            friend = next(filter(lambda x: int(friend_id) == int(x.id), self._friends))
        except StopIteration as e:
            print(e)
            return

        self._friends.remove(friend)
