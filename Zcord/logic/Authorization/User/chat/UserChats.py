from typing import List

from logic.Main.Chat.Controller.ChatController import ChatController
from logic.Main.Chat.View.dm_view.ChatClass.ChatView import ChatView

from logic.Main.Chat.View.group_view.Group.GroupView import GroupView
from logic.db_client.api_client import APIClient
from .fabric import CreateChat


class UserChats:
    def __init__(self, user):
        self._dm_chats: List[ChatView] = []
        self._groups: List[GroupView] = []
        self._chats_controller: ChatController = ChatController()  # Класс контроллера
        self.__user = user
        self._db = APIClient()

    def init_dm_chats(self) -> None:
        fabric = CreateChat()

        chat_db = self._db.get_chats(user_id=self.__user.id, is_group=False)

        for chat_attrs in chat_db:
            user1 = chat_attrs['DM']['user1']
            user2 = chat_attrs['DM']['user2']
            friend_id = user2 if str(user1) == str(self.__user.id) else user1
            chat = fabric.create_chat(is_dm=True,
                                      chat_id=str(chat_attrs["id"]),
                                      friend_id=str(friend_id),
                                      user_obj=self.__user,
                                      controller=self._chats_controller)
            self._dm_chats.append(chat)
            self._chats_controller.add_view(str(chat_attrs['id']), chat)

    def init_groups(self):
        fabric = CreateChat()
        groups = self._db.get_chats(user_id=self.__user.id, is_group=True)
        for group in groups:
            group_name = group['group']['group_name']
            group_obj = fabric.create_chat(is_dm=False,
                                           group_id=group['id'],
                                           group_name=group_name,
                                           user_obj=self.__user,
                                           controller=self._chats_controller,
                                           members=group['group']['members'])
            self._groups.append(group_obj)
            self._chats_controller.add_view(str(group['id']), group_obj)

    def add_dm_chat(self, chat_id: str, friend_nick: str):
        fabric = CreateChat()

        chat = fabric.create_chat(is_dm=True,
                                  chat_id=chat_id,
                                  friend_nick=friend_nick,
                                  user_obj=self.__user,
                                  controller=self._chats_controller)
        self._dm_chats.append(chat)
        self._chats_controller.add_view(chat_id, chat)
        return chat

    def get_socket_controller(self) -> ChatController.SocketController:
        return self._chats_controller.get_socket_controller()

    def chats_props(self) -> dict:
        """Поочередно возвращает атрибуты каждого класса"""
        for chat in self._dm_chats:
            yield {"chat_id": chat.chat_id, "nickname": chat.getNickName(), "chat_ui": chat.ui.MAIN, 'is_dm': True}

        for group in self._groups:
            yield {"chat_id": str(group.chat_id), "group_name": group.group_name, "group_ui": group.ui.MAIN, 'is_dm': False}

    def get_dm_chats(self) -> List[ChatView]:
        return self._dm_chats.copy()

    def get_groups_props(self) -> dict:
        for group in self._groups:
            yield {'chat_id': group.chat_id, 'group_name': group.group_name, 'users': group.get_users}

    def delete_dm_chat(self, chat_id: str) -> None:
        chat = list(filter(lambda x: str(x.chat_id) == str(chat_id), self._dm_chats))[0]
        self._dm_chats.remove(chat)
        self._chats_controller.delete_chat(chat_id)
