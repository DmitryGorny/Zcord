import mysql
from logic.db_handler.db_handler import db_handler
from logic.Authorization.User.User import User

class FriendAdding:
    """
    Статус 1 - неподтвержденный запрос
    Статус 2 в БД - дружба
    """
    def __init__(self, user):
        self.__user = user


    def sendRequest(self, nickToSend) -> bool:
        db = db_handler("26.181.96.20", "Dmitry", "gfggfggfg3D-", "zcord", "friendship")

        db_users = db_handler("26.181.96.20", "Dmitry", "gfggfggfg3D-", "zcord", "users")

        userToSend = db_users.getCertainRow("nickname", nickToSend, "id, nickname, firstname, password")

        if len(userToSend) == 0:
            return False

        #Код проверки наличия дружбы перед отправкой запроса. Может работать медленно при большом количестве данных
        rowWithFriends1 = db.getCertainRow("friend_one_id", self.__user.getNickName(), "friend_one_id,friend_two_id, status")

        rowWithFriends2 = db.getCertainRow("friend_one_id", nickToSend, "friend_one_id,friend_two_id, status")

        friendshipRow1 = list(filter(lambda x: nickToSend in x, rowWithFriends1))

        friendshipRow2 = list(filter(lambda x: self.__user.getNickName() in x, rowWithFriends2))


        if len(friendshipRow1) == 0 and len(friendshipRow2) == 0:
            addFriends = db.insertDataInTable("(`friend_one_id`,`friend_two_id`, `status`)",
                                                            f"('{self.__user.getNickName()}', '{nickToSend}', '1')" )

            return addFriends

        return False

    def acceptRequest(self, NickToAnswer) -> bool:
        """Метод меняет статус в БД с 1 на 2, клиентские части не затрагиваются"""
        db = db_handler("26.181.96.20", "Dmitry", "gfggfggfg3D-", "zcord", "friendship")
        rowWithFriend = db.getDataFromTableColumn("*", f"WHERE friend_one_id = '{self.__user.getNickName()}' "
                                                       f"or friend_two_id = '{self.__user.getNickName()}'")

        friendshipRow = list(filter(lambda x: NickToAnswer in x, rowWithFriend))

        updatingStatus = db.UpdateRequest("`status`", "2", f"WHERE `chat_id` = {friendshipRow[0][0]}")

        self.deleteFriendRequest(NickToAnswer)

        return updatingStatus


    def rejectReques(self, FriendToDelete):
        db = db_handler("26.181.96.20", "Dmitry", "gfggfggfg3D-", "zcord", "friendship")

        rowWithFriend = db.getDataFromTableColumn("*", f"WHERE friend_one_id = '{self.__user.getNickName()}' "
                                                       f"or friend_two_id = '{self.__user.getNickName()}'")

        friendshipRow = list(filter(lambda x: FriendToDelete in x, rowWithFriend))

        db.DeleteRequest("`chat_id`", friendshipRow[0][0])

        self.deleteFriendRequest(FriendToDelete)

    def deleteFriendRequest(self, friendNick):
        db = db_handler("26.181.96.20", "Dmitry", "gfggfggfg3D-", "zcord", "friends_adding")
        id = db.getDataFromTableColumn("`id`", f"WHERE sender_nick = '{self.__user.getNickName()}' AND friend_nick = '{friendNick}' "
                                        f"OR sender_nick = '{friendNick}' AND friend_nick = '{self.__user.getNickName()}'")
        print(id, self.__user.getNickName(), friendNick)
        db.DeleteRequest("id", id[0][0])





