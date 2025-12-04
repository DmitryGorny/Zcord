import asyncio
from typing import Protocol, Dict

from logic.server.Service.core.MessageServiceCommunication.IMessageServiceDispatcher import IMessageServiceDispatcher
from logic.server.Service.core.enteties.Enteties import IClient


class IClientRepo(Protocol):
    _clients: Dict[str, IClient]
    _service_message_connection: IMessageServiceDispatcher

    def _get_client(self, client_id: str) -> IClient | None:
        raise NotImplementedError

    async def send_message(self, client_id: str, msg_type: str, extra_data: dict) -> None:
        pass

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

    async def change_client_activity_status(self, client_id: str, sender_id: str, status: dict[str, str]) -> None:
        raise NotImplementedError

    def get_clients_current_chat(self, client_id: str) -> int | None:
        raise NotImplementedError

    def set_client_current_chat(self, client_id: str, chat_id: int) -> bool:
        raise NotImplementedError

    def get_client_online_stat(self, client_id: str) -> dict:
        raise NotImplementedError

    def get_client_nick(self, client_id: str) -> str:
        raise NotImplementedError

    async def notify_message_server_left(self, user_id: str):
        raise NotImplementedError


