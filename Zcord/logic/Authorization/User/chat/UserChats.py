from typing import List

from logic.Main.Chat.Controller.ChatController import ChatController
from logic.Main.Chat.View.ChatClass import ChatView
from .fabric import CreateChat


class UserChats:
    def __init__(self, user):
        self._dm_chats: List[ChatView] = []
        self._dm_chats_controller: ChatController = ChatController()  # Класс контроллера
        self.__user = user

    def init_dm_chats(self, friends_list: dict) -> None:
        fabric = CreateChat()
        if friends_list['status'] == '1' or friends_list['status'] == '3':
            return

        chat = fabric.create_chat(is_dm=True,
                                  chat_id=friends_list["chat_id"],
                                  friend_nick=friends_list["nickname"],
                                  user_obj=self.__user,
                                  controller=self._dm_chats_controller)
        self._dm_chats.append(chat)

    def add_DM_chat(self, chat_id: str, friend_nick: str):
        fabric = CreateChat()

        chat = fabric.create_chat(is_dm=True,
                                  chat_id=chat_id,
                                  friend_nick=friend_nick,
                                  user_obj=self.__user,
                                  controller=self._dm_chats_controller)
        self._dm_chats.append(chat)
        self._dm_chats_controller.add_view(chat_id, chat)
        return chat

    def get_socket_controller(self) -> ChatController.SocketController:
        return self._dm_chats_controller.get_socket_controller()

    def init_controller_views_list(self):
        self._dm_chats_controller.set_views(self._dm_chats)

    def chats_props(self) -> dict:
        """Поочередно возвращает атрибуты каждого класса"""
        for chat in self._dm_chats:
            yield {"chat_id": chat.getChatId(), "nickname": chat.getNickName(), "chat_ui": chat.ui.MAIN}

    def delete_DM_chat(self, chat_id: str) -> None:
        chat = list(filter(lambda x: str(x.getChatId()) == str(chat_id), self._dm_chats))[0]
        self._dm_chats.remove(chat)
        self._dm_chats_controller.delete_chat(chat_id)

    def get_DM_hat_by_id(self, chat_id: str) -> ChatView:
        chat = list(filter(lambda x: x.getChatId() == chat_id, self._dm_chats))
        return chat[0] if len(chat) > 0 else None
