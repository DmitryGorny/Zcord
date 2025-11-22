import asyncio
from typing import Protocol


class IClientService(Protocol):
    async def user_joined(self, user_id: str, nickname: str, writer: asyncio.StreamWriter, last_online: str,
                          friends: list[dict], status: dict[str, str], chats: list[dict]):
        pass

    async def user_left(self, client_id: str, status: dict[str, str]):
        pass

    async def change_client_activity_status(self, client_id: str, status: dict[str, str]) -> None:
        pass
