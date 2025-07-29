from logic.Main.ActivitySatus.Activity import Director, CreateStatus, Online, Hidden, DisturbBlock, AFK
from logic.Message.message_client import MessageConnection


class User:
    def __init__(self, user_id, nickname, password):
        self.__id = user_id
        self.__nickname = nickname
        self.__friends = {}
        self.__password = password
        self._status = None
        self._statuses = []
        self.create_default_statuses()

    @property
    def statuses(self):
        return self._statuses
    def create_default_statuses(self):
        status_director = Director()
        status_director.builder = CreateStatus()

        status_director.builder.status = Online()
        status_director.build_online_status()
        online = status_director.builder.status

        status_director.builder.status = DisturbBlock()
        status_director.build_dont_distrub_status()
        distrub = status_director.builder.status

        status_director.builder.status = Hidden()
        status_director.build_hidden_status()
        hidden = status_director.builder.status

        status_director.builder.status = AFK()
        status_director.build_AFK_status()
        afk = status_director.builder.status

        self._statuses = [online, distrub, hidden, afk]
        self._status = online
    @property
    def status(self):
        return self._status
    @status.setter
    def status(self, status) -> None:
        self._status = status

    def getNickName(self):
        return self.__nickname

    def get_user_id(self):
        return self.__id

    def setFrinds(self, friends):
        self.__friends = friends

    def getFriends(self):
        return self.__friends

