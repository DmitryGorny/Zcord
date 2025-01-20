from logic.db_handler.db_handler import db_handler
import bcrypt
class UserRegistration:
    def __init__(self, name, nickname, password):
        self.__nickname = nickname
        self.__name = name
        self.__password = password

    def register(self):
        users_table = db_handler("26.181.96.20", "Dmitry", "gfggfggfg3D-", "zcord", "users")

        newPass = bcrypt.hashpw(self.__password.encode(), bcrypt.gensalt())

        UserWasAdded = users_table.insertDataInTable("(`nickname`,`firstname`, `password`)", f"('{self.__nickname}', '{self.__name}', '{newPass.decode()}')")

        if UserWasAdded:
            return True

        return False

