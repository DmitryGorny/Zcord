from typing import Dict

from logic.server.Service.core.enteties.Enteties import IChat
from logic.server.Service.core.repositroies.chat_repo.IChatRepo import IChatRepo
from logic.server.Service.infrastructure.enteties.Enteties import Chat, ChatMember


class ChatRepo(IChatRepo):
    def __init__(self):
        self._chats: Dict[str, IChat] = {}

    def add_chat(self, chat_id: str, friends_id: list[int]) -> None:
        chat = Chat(chat_id)
        for friend_id in friends_id:
            chat.add_member(ChatMember(str(friend_id)))

        self._chats[chat_id] = chat

    def add_chats(self, chats: list[dict]):
        for chat in chats:
            self.add_chat(chat_id=chat['chat_id'], friends_id=chat['friends_id'])

    def delete_chat(self, chat_id: str) -> None:
        if chat_id not in self._chats.keys():
            raise ValueError("Чат с таким id не существует")
        del self._chats[chat_id]

    def get_chat_by_user_id(self, user_id: str):
        for chat in self._chats.values():
            if chat.get_member_by_id(user_id) is not None:
                return chat

    def delete_chat_by_user_id(self, user_id: str) -> None:
        for chat_id in self._chats.keys():
            if self._chats[chat_id].get_member_by_id(user_id) is not None:
                del self._chats[chat_id]
                return

    def get_chat_by_id(self, chat_id: str):
        return self._chats[chat_id]
