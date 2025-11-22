from typing import Dict

from logic.client.Chat.ClientChat import IChat


class IChatRepo:
    _chats: Dict[str, IChat]

    def add_chat(self, chat_id: str, friends_id: list[int]) -> None:
        raise NotImplementedError

    def add_chats(self, chats: list[dict]):
        raise NotImplementedError

    def delete_chat(self, chat_id: str) -> None:
        raise NotImplementedError

    def get_chat_by_user_id(self, user_id: str):
        raise NotImplementedError

    def delete_chat_by_user_id(self, user_id: str) -> None:
        raise NotImplementedError

    def get_chat_by_id(self, chat_id: str):
        raise NotImplementedError
