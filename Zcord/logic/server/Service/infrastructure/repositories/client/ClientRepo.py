import asyncio
from typing import Dict

from logic.server.Service.core.enteties.Enteties import IClient
from logic.server.Service.core.repositroies.client_repo.IClientRepo import IClientRepo
from logic.server.Service.infrastructure.MessageServiceCommunication.MessageServiceDispatcher import \
    MessageServiceDispatcher
from logic.server.Service.infrastructure.enteties.Enteties import Client


class ClientRepo(IClientRepo):
    def __init__(self, service_message_connection):
        self._clients: Dict[str, IClient]
        self._service_message_connection: MessageServiceDispatcher = service_message_connection

    def add_client(self, client_id: str, client_name: str, last_online: str, writer: asyncio.StreamWriter) -> None:
        client = Client(user_id=client_id,
                        nick=client_name,
                        last_online=last_online,
                        writer=writer)
        if client_id in self._clients.keys():
            raise ConnectionError('Двойное подключение')

        self._clients[client_id] = client

    async def send_message(self, client_id: str, msg_type: str, extra_data: dict) -> None:
        client = self.get_client(client_id)
        if client is None:
            print('Client doesnt exist')
            return
        await client.send_message(msg_type, extra_data)

    def delete_client(self, client_id: str) -> None:
        if client_id not in self._clients.keys():
            raise ValueError("Такого юзера нет")

        del self._clients[client_id]

    def in_clients(self, client_id: str) -> bool:
        if client_id not in self._clients:
            return False
        return True

    async def close_client_writer(self, client_id: str) -> None:
        client = self.get_client(client_id)

        if client is None:
            raise ValueError('Такого клиента не существует')

        if not client.writer.is_closing():  # TODO: Нужно ли отслеживать
            client.writer.close()
            await client.writer.wait_closed()

    async def connect_message_socket(self, client_id: str) -> None:
        await self.get_client(client_id).send_message("__CONNECT__", {
            "connect": 1
        })

    async def notify_message_server_add(self, client_id: str, chats: list[dict], writer: asyncio.StreamWriter) -> None:
        client_ip = writer.transport.get_extra_info('socket').getpeername()
        chats = {f'{chat["chat_id"]}': [] for chat in chats}
        await self._service_message_connection.sender_func(msg_type="USER-INFO",
                                                           mes_data={"serialize_1": chats,
                                                                     "serialize_2": {'user_id': str(client_id),
                                                                                     "IP": client_ip[0]}})

    def get_client(self, client_id: str) -> Client | None:
        return self._clients.get(client_id, None)

    async def change_client_activity_status(self, client_id: str, status: dict[str, str]) -> None:
        client = self.get_client(client_id)
        if client is None:
            print('Client doesnt exist')
            return

        await client.send_message('USER-STATUS', {
            "user-status": status,
            "nickname": client.nick,
        })
