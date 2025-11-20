import asyncio
from typing import Dict

from logic.server.Service.core.Client.Client import Client
from logic.server.Service.core.Manager.IClientManager import IClientManager


class ClientManager(IClientManager):
    def __init__(self):
        # {client_id: Client}
        self._clients: Dict[str, Client] = {}

    def get_client(self, client_id: str) -> Client | None:
        return self._clients.get(client_id, None)

    def add_client(self, client_id: str, client_name: str, last_online: str, writer: asyncio.StreamWriter) -> None:
        client = Client(user_id=client_id,
                        nick=client_name,
                        last_online=last_online,
                        writer=writer)
        if client_id in self._clients.keys():
            raise ConnectionError('Двойное подключение')

        self._clients[client_id] = client

    def delete_client(self, client_id: str) -> None:
        if client_id not in self._clients.keys():
            raise ValueError("Такого юзера нет")

        del self._clients[client_id]

    def in_clients(self, client_id: str) -> bool:
        if client_id not in self._clients:
            return False
        return True
