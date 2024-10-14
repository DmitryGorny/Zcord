
class AuthorizationError(Exception):
    def __init__(self, user):
        self.__user = user

    def __str__(self):
        return f"{self.__user} не существует в БД"
