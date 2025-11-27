from typing import Protocol


class IChatService(Protocol):
    async def cache_request(self, user_id: str) -> None:
        raise NotImplementedError

    async def change_chat(self, chat_code: int, user_id: str) -> None:
        raise NotImplementedError

    async def add_user_group(self, request_receiver: str, group_id: str, request_id: str):
        raise NotImplementedError

    def group_request_rejected(self, request_id: str) -> None:
        raise NotImplementedError

    async def user_left_group(self, request_receiver: str, group_id: str) -> None:
        raise NotImplementedError

    async def create_group(self, creator_id: str, group_name: str, is_private: bool,
                           is_invite_from_admin: bool, is_password: bool, password: bool) -> None:
        raise NotImplementedError
