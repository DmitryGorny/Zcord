
class User:
    def __init__(self, nickname, password):
        self.__nickname = nickname
        self.__password = password
        self.__first_name = ""

    def getFirstName(self):
        return self.__first_name

    def getNickName(self):
        return self.__nickname
