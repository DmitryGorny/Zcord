from typing import Protocol


class IChatService(Protocol):
    async def cache_request(self, user_id: str) -> None:
        raise NotImplementedError

    async def change_chat(self, chat_code: int, user_id: str) -> None:
        raise NotImplementedError

    async def add_user_group(self, request_receiver: str, group_id: str, receiver_nick: str, request_id: str = None):
        raise NotImplementedError

    async def group_request_rejected(self, request_id: str, receiver_id: str, group_id: str) -> None:
        raise NotImplementedError

    async def user_left_group(self, request_receiver: str, group_id: str) -> None:
        raise NotImplementedError

    async def create_group(self, creator_id: str, group_name: str, is_private: bool,
                           is_invite_from_admin: bool, is_password: bool, password: bool, members: list[str]) -> None:
        raise NotImplementedError

    async def change_admin(self, chat_id: str, group_id: str, new_admin_id: str) -> None:
        raise NotImplementedError

    async def send_group_request(self, sender_id: str, receiver_id: str, group_id: str) -> None:
        raise NotImplementedError

    async def change_group_settings(self, group_id: str, sender_id: str, new_settings: dict[str, bool], flags: dict[str, bool]):
        raise NotImplementedError

    async def _init_group_by_inner_id(self, group_id: str, user_id: str) -> bool:
        raise NotImplementedError

    async def find_group(self, group_name: str, user_id: str) -> None:
        raise NotImplementedError
