from ..Errors.AuthorizationError import AuthorizationError
import bcrypt
from ..db_handler.api_client import APIClient


class UserAuthorization:
    def __init__(self, nick_name, password):
        self.__nick_name = nick_name
        self.__password = password
        self.__user_id = None

    def login(self):
        users_table = APIClient()

        user = users_table.get_user(self.__nick_name)

        if len(user) == 0: #Проверка наличия логина юзреа в базе
            raise AuthorizationError(self.__nick_name)

        stored_password_hash = user[0]['password'].encode('utf-8')

        valid = bcrypt.checkpw(self.__password.encode('utf-8'), stored_password_hash)

        if valid:
            self.__user_id = user[0]['id']
            return True

        return False

    def get_valid_login(self):
        return self.__nick_name

    def get_valid_password(self):
        return self.__password

    def get_valid_id(self):
        return self.__user_id
