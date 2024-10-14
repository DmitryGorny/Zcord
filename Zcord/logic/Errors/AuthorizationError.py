
class AuthorizationError(Exception):
    def __init__(self, user):
        self.__user = user

    def __str__(self):
        return f"Пользователя с никнеймом {self.__user} не существует"
