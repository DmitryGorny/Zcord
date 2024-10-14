from logic.db_handler.db_tables.Users import Users
from logic.Errors.AuthorizationError import AuthorizationError

class UserAuthorization:
    def __init__(self, nick_name, password):
        self.__nick_name = nick_name
        self.__password = password

    def login(self):
        users_table = Users("127.0.0.1", "Dmitry", "gfggfggfg3D-", "zcord", "users")

        nickname_column = users_table.getDataFromTableColumn("nickname")

        found_user = list(filter(lambda x: self.__nick_name in x, nickname_column))

        if len(found_user) == 0: #Проверка наличия логина юзреа в базе
            raise AuthorizationError(self.__nick_name)

        password = users_table.getCertainRow("nickname", found_user[0][0], "password")[0][0]

        if self.__password == password:
            return True

        return False








