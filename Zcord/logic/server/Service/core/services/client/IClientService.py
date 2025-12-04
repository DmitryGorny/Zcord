import asyncio
from typing import Protocol


class IClientService(Protocol):
    async def user_joined(self, user_id: str, nickname: str, writer: asyncio.StreamWriter, last_online: str,
                          friends: list[dict], status: dict[str, str], chats: list[dict]):
        raise NotImplementedError

    async def user_left(self, client_id: str, status: dict[str, str]):
        raise NotImplementedError

    async def _change_client_activity_status(self, client_id: str, sender_id: str, status: dict[str, str]) -> None:
        raise NotImplementedError

    async def user_status(self, client_id: str, status: dict[str, str]) -> None:
        raise NotImplementedError

    async def call_notification(self, user_id: str, chat_id: str, call_flg) -> None:
        raise NotImplementedError

    async def icon_call_add(self, user_id: str, chat_id: str, username: str) -> None:
        raise NotImplementedError

    async def icon_call_left(self, user_id: str, chat_id: str) -> None:
        raise NotImplementedError

