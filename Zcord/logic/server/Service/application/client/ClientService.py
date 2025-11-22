import asyncio

from logic.server.Service.core.repositroies.chat_repo.IChatRepo import IChatRepo
from logic.server.Service.core.repositroies.client_repo.IClientRepo import IClientRepo
from logic.server.Service.core.repositroies.friend_repo.IFriendRepo import IFriendRepo
from logic.server.Service.core.services.client.IClientService import IClientService


class ClientService(IClientService):
    def __init__(self, client_repo: IClientRepo, chat_repo: IChatRepo, friend_repo: IFriendRepo):
        self._client_repo: IClientRepo = client_repo
        self._chat_repo: IChatRepo = chat_repo
        self._friend_repo: IFriendRepo = friend_repo

    async def user_joined(self, user_id: str, nickname: str, writer: asyncio.StreamWriter, last_online: str,
                          friends: list[dict], status: dict[str, str], chats: list[dict]):
        self._client_repo.add_client(client_id=user_id,
                                     client_name=nickname,
                                     writer=writer,
                                     last_online=last_online)
        self._friend_repo.add_friends(client_id=user_id, friends=friends)
        self._chat_repo.add_chats(chats=chats)
        await self._client_repo.connect_message_socket(user_id)
        await self._client_repo.change_client_activity_status(user_id, status)

        for friend_attr in friends:
            await self.change_client_activity_status(friend_attr['id'], status)

        await self._client_repo.notify_message_server_add(user_id, chats, writer)

    async def user_left(self, client_id: str, status: dict[str, str]):
        await self.change_client_activity_status(client_id, status)
        await self._client_repo.close_client_writer(client_id)

    async def change_client_activity_status(self, client_id: str, status: dict[str, str]) -> None:
        await self._client_repo.change_client_activity_status(client_id, status)
