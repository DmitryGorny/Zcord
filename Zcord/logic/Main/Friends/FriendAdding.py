from ...db_handler.api_client import APIClient


class FriendAdding:
    """
    Статус 1 - неподтвержденный запрос
    Статус 2 в БД - дружба
    Статус 3 - Блокировка
    """
    def __init__(self, user):
        self.__user = user
        self.db = APIClient()

    def sendRequest(self, nickToSend) -> bool:
        if nickToSend == self.__user.getNickName():
            return False

        userToSend = self.db.get_user(nickToSend)

        # Проверка на существование в базе пользователя, которому отправляется запрос
        if len(userToSend) == 0:
            return False
        else:
            userToSendNickname = userToSend[0]['nickname']
            userToSendId = userToSend[0]['id']

        friendship = self.db.get_friendship_by_nicknames(self.__user.getNickName(), userToSendNickname)
        try:
            # Проверка на блокировку дружбы
            if friendship[0]['status'] != 3:
                return False
        except Exception as e:
            pass

        # Проверка на наличие дружбы
        if not friendship:
            self.db.create_friendship_request(self.__user.get_user_id(), userToSendId)
            return True

        return False

    def acceptRequest(self, NickToAnswer) -> bool:
        """Метод меняет статус в БД с 1 на 2, клиентские части не затрагиваются"""
        friendship = self.db.get_friendship_by_nicknames(self.__user.getNickName(), NickToAnswer)

        if friendship:
            friendship_id = friendship['id']
        else:
            return False

        self.db.patch_friendship_status(friendship_id, status=2)

        self.deleteFriendRequest(NickToAnswer)

        return True

    def rejectRequest(self, FriendToDelete, deleteFriend:bool = False):
        friendship = self.db.get_friendship_by_nicknames(self.__user.getNickName(), FriendToDelete)

        if friendship:
            friendship_id = friendship['id']
        else:
            return False

        self.db.delete_friendship(friendship_id)

        if not deleteFriend:
            self.deleteFriendRequest(FriendToDelete)

    def deleteFriendRequest(self, friendNick):
        friend_request = self.db.get_friend_request(self.__user.getNickName(), friendNick)
        if friend_request:
            friend_requests_id = friend_request['id']
        else:
            return False

        self.db.delete_friend_requests(friend_requests_id)
        return True

    def BlockUser(self, userToBlock):
        """Метод меняет статус в БД на 3, клиентские части не затрагиваются"""
        friendship = self.db.get_friendship_by_nicknames(self.__user.getNickName(), userToBlock)

        if friendship:
            friendship_id = friendship['id']
        else:
            return False

        self.db.patch_friendship_status(friendship_id, status=3)

        return True
