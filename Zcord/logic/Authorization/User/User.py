
class User:
    def __init__(self, nickname, password):
        self.__nickname = nickname
        self.__password = password
        self.__first_name = ""
        self.__friends = {}

    def getFirstName(self):
        return self.__first_name

    def getNickName(self):
        return self.__nickname

    def setFrinds(self, friends):
        self.__friends = friends

    def getFriends(self):
        return self.__friends
