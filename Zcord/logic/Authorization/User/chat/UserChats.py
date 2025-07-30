from typing import List
from logic.Main.Chat.ChatClass import Chat
from .fabric import CreateChat


class UserChats:
    def __init__(self, user):
        self._dm_chats: List[Chat] = []
        self.__user = user

    def init_dm_chats(self, friends_list: dict) -> None:
        fabric = CreateChat()
        chat = fabric.create_chat(is_dm=True,
                                      chat_id=friends_list["chat_id"],
                                      friend_nick=friends_list["nickname"],
                                      user_obj=self.__user)
        self._dm_chats.append(chat)

    def chats_props(self) -> dict:
        """Поочередно возвращает атрибуты каждого класса"""
        for chat in self._dm_chats:
            yield {"chat_id": chat.getChatId(), "nickname": chat.getNickName()}
