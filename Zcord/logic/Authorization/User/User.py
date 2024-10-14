
class User:
    def __init__(self,firstName, nickname, password):
        self.__first_name = firstName
        self.__nickname = nickname
        self.__password = password


    def getFirstName(self):
        return self.__first_name

    def getNickName(self):
        return self.__nickname
