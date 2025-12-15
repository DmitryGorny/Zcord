from typing import Dict

from logic.server.Service.core.enteties.Enteties import IChat


class IChatRepo:
    _chats: Dict[str, IChat]

    def add_chat(self, chat_id: str, friends_id: list[str]) -> None:
        raise NotImplementedError

    def add_chats(self, chats: list[dict]):
        raise NotImplementedError

    def delete_chat(self, chat_id: str) -> None:
        raise NotImplementedError

    def get_chats_by_user_id(self, user_id: str) -> list[IChat]:
        raise NotImplementedError

    def get_chat_by_id(self, chat_id: str):
        raise NotImplementedError
