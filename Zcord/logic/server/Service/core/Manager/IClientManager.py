from typing import Protocol, Dict

from logic.server.Service.core.Client.Client import Client


class IClientManager(Protocol):
    clients: Dict[str, Client]

    def get_client(self, client_id: str) -> Client | None:
        raise NotImplementedError

    def add_client(self, client_id: str, client_name: str, last_online: str, writer: asyncio.StreamWriter) -> None:
        raise NotImplementedError

    def delete_client(self, client_id: str) -> None:
        raise NotImplementedError

    def in_clients(self, client_id: str) -> bool:
        raise NotImplementedError
