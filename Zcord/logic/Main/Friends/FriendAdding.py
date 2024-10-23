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

        rowWithFriends = db.getCertainRow("friend_one_id", self.__user.getNickName(), "friend_one_id,friend_two_id, status")

        friendshipRow = list(filter(lambda x: nickToSend in x, rowWithFriends))


        if len(friendshipRow) == 0:
            addFriends = db.insertDataInTable("(`friend_one_id`,`friend_two_id`, `status`)",
                                                            f"('{self.__user.getNickName()}', '{nickToSend}', '1')" )

            return addFriends

        return False

    def acceptRequest(self, NickToAnswer) -> bool:
        db = db_handler("26.181.96.20", "Dmitry", "gfggfggfg3D-", "zcord", "friendship")

        rowWithFriend = db.getCertainRow("friend_one_id", self.__user.getNickName(), "chat_id, friend_one_id,friend_two_id, status")

        friendshipRow = list(filter(lambda x: NickToAnswer in x, rowWithFriend))


        updatingStatus = db.UpdateRequest("`status`", "2", f"WHERE `chat_id` = {friendshipRow[0][0]}")

        return updatingStatus


    def rejectReques(self, FriendToDelete):
        db = db_handler("26.181.96.20", "Dmitry", "gfggfggfg3D-", "zcord", "friendship")

        rowWithFriend = db.getCertainRow("friend_one_id", self.__user.getNickName(), "chat_id, friend_one_id,friend_two_id, status")

        friendshipRow = list(filter(lambda x: FriendToDelete in x, rowWithFriend))

        db.DeleteRequest("`chat_id`", friendshipRow[0][0])





