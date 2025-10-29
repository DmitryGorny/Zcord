from datetime import datetime
from typing import List, Dict
from logic.Main.Chat.Controller.ChatController import ChatController
from logic.Authorization.User.chat.UserChats import UserChats
from logic.Authorization.User.friend.UserFriends import UserFriends
from logic.Main.ActivitySatus.Activity import Director, CreateStatus, Online, Hidden, DisturbBlock, AFK
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
        self.__password = password
        self._friends_model = UserFriends(self)
        self._chats_model = UserChats(self)

        self.init_friends_and_chats()

    def init_friends_and_chats(self) -> None:
        self._friends_model.init_friends()

        self._chats_model.init_dm_chats()
        self._chats_model.init_groups()

    def add_chat(self, friend_id: str, chat_id: str):
        return self._chats_model.add_dm_chat(chat_id=chat_id, friend_id=friend_id)

    def add_friend(self, username: str,  user_id: str):
        from datetime import datetime
        now = datetime.now()
        time_str = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        self._friends_model.add_friend(user_nickname=username, user_id=user_id, last_online=time_str)

    def get_chats(self, without_ui: bool = False) -> List[dict]:
        attrs_list: List[dict] = []
        if not without_ui:
            for chat_attrs in self._chats_model.chats_props():
                attrs_list.append(chat_attrs)
        else:
            for chat_attrs in self._chats_model.chats_props_without_ui():
                attrs_list.append(chat_attrs)
        return attrs_list

    def delete_chat(self, chat_id: str, is_dm: bool) -> None:
        if is_dm:
            self._chats_model.delete_dm_chat(chat_id)

    def delete_friend(self, friend_id: str) -> None:
        self._friends_model.delete_friend(friend_id)

    def change_chat(self, chat_id: str) -> None:
        ClientConnections.change_chat(chat_id)

    def get_socket_controller(self) -> ChatController.SocketController:
        return self._chats_model.get_socket_controller()

    def getFriends(self) -> List[Dict[str, str]]:
        friends: List[Dict[str, str]] = []
        for friend in self._friends_model.friends_props():
            friends.append(friend)
        return friends

    def get_groups(self) -> List[Dict[str, str]]:
        groups_attrs: List[Dict[str, str]] = []
        for group_view in self._chats_model.get_groups_props():
            groups_attrs.append(group_view)
        return groups_attrs

