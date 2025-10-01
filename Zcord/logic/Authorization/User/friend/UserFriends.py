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
            friend_data = self._db.get_user_by_id(friendship['user1'] if friendship['user1'] != self._user.id else friendship['user2'])
            friend = fabric.create_friend(chat_id=chat_id,
                                          user_nickanme=friend_data["nickname"],
                                          status=status,
                                          user_id=friend_data["id"],
                                          last_online=friend_data["last_online"])
            self._friends.append(friend)

    def friends_props(self) -> dict[str, str]:
        """Поочередно возвращает атрибуты каждого класса"""
        for friend in self._friends:
            yield {"id": str(friend.id),
                   "chat_id": str(friend.chat_id),
                   "nickname": friend.getNickName(),
                   "status": str(friend.status),
                   "last_online": friend.last_online}
