import asyncio
from typing import Protocol

from logic.server.Service.core.Manager.ClientManager import Client
from logic.server.Service.core.Manager.IClientManager import IClientManager
from logic.server.Service.core.MessageServiceCommunictaion.MessageServiceDispatcher import IMessageServiceDispatcher


class ISessionRepo(Protocol):
    _client_manager: IClientManager
    _message_service_dispatcher: IMessageServiceDispatcher

    def _get_client(self, client_id: str) -> Client:
        raise NotImplementedError

    def add_client(self, client_id: str, client_name: str, last_online: str, writer: asyncio.StreamWriter) -> None:
        raise NotImplementedError

    def remove_client(self, client_id: str) -> None:
        raise NotImplementedError

    def add_friends(self, client_id: str, friends: list[dict[str, str]]) -> None:
        raise NotImplementedError

    def add_chats(self, client_id: str, chats: list[dict]) -> None:
        raise NotImplementedError

    async def connect_message_socket(self, client_id: str) -> None:
        raise NotImplementedError

    async def change_activity_status(self, client_id: str, status: dict[str, str]) -> None:
        raise NotImplementedError

    async def notify_message_server_add(self, client_id: str, chats: list[dict], writer: asyncio.StreamWriter) -> None:
        raise NotImplementedError


class SessionRepo(ISessionRepo):
    def __init__(self, client_manager: IClientManager, message_service_dispatcher: IMessageServiceDispatcher):
        self._client_manager: IClientManager = client_manager
        self._message_service_dispatcher: IMessageServiceDispatcher = message_service_dispatcher

    def _get_client(self, client_id: str) -> Client:
        return self._client_manager.get_client(client_id=client_id)

    def add_client(self, client_id: str, client_name: str, last_online: str, writer: asyncio.StreamWriter) -> None:
        self._client_manager.add_client(client_id, client_name, last_online, writer)

    def remove_client(self, client_id: str) -> None:
        self._client_manager.delete_client(client_id)

    def add_friends(self, client_id: str, friends: list[dict[str, str]]) -> None:
        client = self._get_client(client_id)
        client.friends = friends

    def add_chats(self, client_id: str, chats: list[dict]) -> None:
        client = self._get_client(client_id)
        for chat in chats:
            client.add_chat(chat_id=chat['chat_id'], friends_id=chat['friends_id'])

    async def connect_message_socket(self, client_id: str) -> None:
        await self._get_client(client_id).send_message("__CONNECT__", {
            "connect": 1
        })

    async def change_activity_status(self, client_id: str, status: dict[str, str]) -> None:
        user_status = {'color': status['color'], 'user-status': status['status_name']}

        client = self._get_client(client_id)

        if len(client.friends) == 0:  #######
            raise ValueError("Friends не были инициализированы")

        for friend_id in client.friends.keys():

            friend = client.friends[friend_id]
            if self._client_manager.in_clients(friend_id):
                continue

            if friend.friendship_status == '1':
                continue

            friend_obj = self._get_client(friend.id)

            await friend_obj.send_message('USER-STATUS', {
                "user-status": user_status,
                "nickname": friend_obj.nick,
            })
            try:
                friend_status = friend_obj.status
            except KeyError:
                continue

            await client.send_message('USER-STATUS', {
                "user-status": friend_status,
                "nickname": friend_obj.nick,
            })

    async def notify_message_server_add(self, client_id: str, chats: list[dict], writer: asyncio.StreamWriter) -> None:
        client_ip = writer.transport.get_extra_info('socket').getpeername()
        chats = {f'{chat["chat_id"]}': [] for chat in chats}
        await self._message_service_dispatcher.sender_func(msg_type="USER-INFO",
                                                           mes_data={"serialize_1": chats,
                                                                     "serialize_2": {'user_id': str(client_id),
                                                                                     "IP": client_ip[0]}})
