from ..db_handler.api_client import APIClient
import bcrypt


class UserRegistration:
    def __init__(self, name, nickname, password):
        self.__nickname = nickname
        self.__name = name
        self.__password = password

    def register(self):
        users_table = APIClient()

        newPass = bcrypt.hashpw(self.__password.encode(), bcrypt.gensalt()).decode('utf-8')

        UserWasAdded = users_table.create_user(self.__nickname, newPass, self.__name)

        if UserWasAdded:
            return True

        return False

