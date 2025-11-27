from typing import Protocol


class IChatDBRepo(Protocol):
    def get_chats(self, user_id: int, is_group: bool) -> list[dict]:
        raise NotImplementedError

    def create_dm_chat(self, chat_id: int) -> list[dict]:
        raise NotImplementedError

    def create_group_chat(self, group_id: int) -> None:
        raise NotImplementedError

    def delete_dm_chat(self, DM_id: int) -> None:
        raise NotImplementedError

    def search_chat_by_id(self, chat_id: int, is_group: bool) -> list[dict]:
        raise NotImplementedError

    def add_group_member(self, user_id: int, group_id: int) -> None:
        raise NotImplementedError

    def delete_group_request(self, request_id: int) -> None:
        raise NotImplementedError

    def delete_group_member_by_id(self, member_id: int) -> None:
        raise NotImplementedError

    def search_group_member(self, user_id: int, group_id: int) -> None:
        raise NotImplementedError

    def create_group(self, group_name: str, is_private: bool, is_invite_from_admin: bool, is_password: bool,
                     password: str, creator_id: str) -> dict:
        raise NotImplementedError

    def add_group_admin(self, user_id: int, group_id: int) -> dict:
        raise NotImplementedError
