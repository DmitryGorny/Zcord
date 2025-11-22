import asyncio
from typing import Protocol, Dict

from logic.server.Service.core.MessageServiceCommunictaion.IMessageServiceDispatcher import IMessageServiceDispatcher
from logic.server.Service.core.enteties.Enteties import IClient


class IClientRepo(Protocol):
    _clients: Dict[str, IClient]
    _service_message_connection: IMessageServiceDispatcher

    def get_client(self, client_id: str) -> IClient | None:
        raise NotImplementedError

    def add_client(self, client_id: str, client_name: str, last_online: str, writer: asyncio.StreamWriter) -> None:
        raise NotImplementedError

    def delete_client(self, client_id: str) -> None:
        raise NotImplementedError

    def in_clients(self, client_id: str) -> bool:
        raise NotImplementedError

    async def close_client_writer(self, client_id: str) -> None:
        raise NotImplementedError

    async def connect_message_socket(self, client_id: str) -> None:
        raise NotImplementedError

    async def notify_message_server_add(self, client_id: str, chats: list[dict], writer: asyncio.StreamWriter) -> None:
        raise NotImplementedError

    async def change_client_activity_status(self, client_id: str, status: dict[str, str]) -> None:
        raise NotImplementedError

