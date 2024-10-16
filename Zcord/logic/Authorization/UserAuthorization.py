from logic.db_handler.db_handler import db_handler
from logic.Errors.AuthorizationError import AuthorizationError
import bcrypt

class UserAuthorization:
    def __init__(self, nick_name, password):
        self.__nick_name = nick_name
        self.__password = password

    def login(self):
        users_table = db_handler("127.0.0.1", "Dmitry", "gfggfggfg3D-", "zcord", "users")

        nickname_column = users_table.getDataFromTableColumn("nickname")

        found_user = list(filter(lambda x: self.__nick_name in x, nickname_column))

        if len(found_user) == 0: #Проверка наличия логина юзреа в базе
            raise AuthorizationError(self.__nick_name)

        password = users_table.getCertainRow("nickname", found_user[0][0], "password")[0][0]

        valid = bcrypt.checkpw(self.__password.encode('utf-8'), password.encode('utf-8'))

        if valid:
            return True

        return False








