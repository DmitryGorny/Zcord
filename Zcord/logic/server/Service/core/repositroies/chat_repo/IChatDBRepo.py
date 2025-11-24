from typing import Protocol


class IChatDBRepo(Protocol):
    def get_chats(self, user_id: int, is_group: bool) -> list[dict]:
        raise NotImplementedError

    def create_dm_chat(self, chat_id: int) -> None:
        raise NotImplementedError

    def create_group_chat(self, group_id: int) -> None:
        raise NotImplementedError

    def delete_dm_chat(self, DM_id: int) -> None:
        raise NotImplementedError

    def search_chat_by_id(self, chat_id: int, is_group: bool) -> list[dict]:
        raise NotImplementedError
