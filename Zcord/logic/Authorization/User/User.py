from datetime import datetime
from typing import List, Dict
from logic.Main.Chat.Controller.ChatController import ChatController
from logic.Authorization.User.chat.UserChats import UserChats
from logic.Authorization.User.friend.UserFriends import UserFriends
from logic.Main.ActivitySatus.Activity import Director, CreateStatus, Online, Hidden, DisturbBlock, AFK
from logic.Message.message_client import MainInterface
from logic.client.ClientConnections.ClientConnections import ClientConnections


class BaseUser:
    def __init__(self, user_id, nickname, last_online: str):
        self._id = user_id
        self._nickname = nickname
        self._status = None
        self._statuses = []
        self._last_online: datetime = datetime.strptime(last_online, "%Y-%m-%dT%H:%M:%S.%fZ")
        self.create_default_statuses()

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

    @property
    def id(self):
        return self._id

    @property
    def statuses(self):
        return self._statuses

    def getNickName(self):
        return self._nickname

    @property
    def last_online(self) -> datetime:
        return self._last_online


class User(BaseUser):
    def __init__(self, user_id, nickname, password, last_online):
        super(User, self).__init__(user_id, nickname, last_online)
        self.__friends = {}
        self.__password = password
        self._friends_model = UserFriends(self)
        self._chats_model = UserChats(self)

        self.init_friends_and_chats()

    def init_friends_and_chats(self) -> None:
        self._friends_model.init_friends()

        for friend in self._friends_model.friends_props():
            self._chats_model.init_dm_chats(friend)
        self._chats_model.init_controller_views_list()

    def get_chats(self) -> List[dict]:
        attrs_list: List[dict] = []
        for chat_attrs in self._chats_model.chats_props():
            attrs_list.append(chat_attrs)
        return attrs_list

    def delete_chat(self, chat_id: str, is_dm: bool) -> None:
        if is_dm:
            self._chats_model.delete_DM_chat(chat_id)

    def change_chat(self, chat_id: str) -> None:
        ClientConnections.change_chat(chat_id)

    def get_socket_controller(self) -> ChatController.SocketController:
        return self._chats_model.get_socket_controller()

    def getFriends(self) -> List[Dict[str, str]]:
        friends: List[Dict[str, str]] = []
        for friend in self._friends_model.friends_props():
            friends.append(friend)
        return friends
