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

        await self._client_repo.change_client_activity_status(user_id, user_id, status)
        await self._client_repo.notify_message_server_add(user_id, chats, writer)

        notified_users = set()
        for friend_attr in friends:  # TODO: В случае кастомных статусов присылать еще и онлайн статус друга
            await self._change_client_activity_status(friend_attr['id'], user_id, status)
            notified_users.add(friend_attr['id'])
            await self._change_client_activity_status(user_id, friend_attr['id'],
                                                      self._client_repo.get_client_online_stat(friend_attr['id']))

        chats = self._chat_repo.get_chats_by_user_id(user_id=user_id)
        for chat in chats: # TODO: Оптимизация
            members = chat.get_members()
            for member in members:
                if member.user_id == user_id:
                    continue

                if member.user_id in notified_users:
                    continue
                await self._change_client_activity_status(member.user_id, user_id, status)
                await self._change_client_activity_status(user_id, member.user_id, status)

    async def user_left(self, client_id: str):
        friends = self._friend_repo.get_client_friends(client_id=client_id)
        chats = self._chat_repo.get_chats_by_user_id(user_id=client_id)
        status = {'status_name': "Невидимка", 'status_instance': 'hidden'}

        notified_users = set()
        for friend in friends:
            notified_users.add(friend.id)
            await self._change_client_activity_status(friend.id, client_id, status)

        for chat in chats: # TODO: Оптимизация
            members = chat.get_members()
            for member in members:
                if member.user_id == client_id:
                    continue
                if member.user_id in notified_users:
                    continue
                await self._change_client_activity_status(member.user_id, client_id, status)

        await self._client_repo.close_client_writer(client_id)
        self._client_repo.delete_client(client_id)
        await self._client_repo.notify_message_server_left(client_id)

    async def _change_client_activity_status(self, client_id: str, sender_id: str, status: dict[str, str]) -> None:
        await self._client_repo.change_client_activity_status(client_id, sender_id, status)

    async def user_status(self, client_id: str, status: dict[str, str]) -> None:
        friends = self._friend_repo.get_client_friends(client_id)
        await self._change_client_activity_status(client_id=client_id, sender_id=client_id, status=status)
        notified_users = set()
        for friend in friends:
            notified_users.add(friend.id)
            await self._change_client_activity_status(client_id=friend.id, sender_id=client_id, status=status)

        chats = self._chat_repo.get_chats_by_user_id(user_id=client_id)
        for chat in chats: # TODO: Оптимизация
            members = chat.get_members()
            for member in members:
                if member.user_id == client_id:
                    continue
                if member.user_id in notified_users:
                    continue
                await self._change_client_activity_status(member.user_id, client_id, status)

    async def call_notification(self, user_id: str, chat_id: str, call_flg) -> None:
        chat = self._chat_repo.get_chat_by_id(chat_id=chat_id)

        for member in chat.get_members():
            await self._client_repo.send_message(client_id=member.user_id, msg_type='__CALL-NOTIFICATION__',
                                                 extra_data={'user_id': user_id,
                                                             'chat_id': chat_id,
                                                             'call_flg': call_flg})

    async def icon_call_add(self, user_id: str, chat_id: str, username: str) -> None:
        chat = self._chat_repo.get_chat_by_id(chat_id)
        for member in chat.get_members():
            await self._client_repo.send_message(client_id=member.user_id, msg_type='__ICON-CALL__',
                                                 extra_data={'user_id': user_id,
                                                             'username': username,
                                                             'chat_id': chat_id})

    async def icon_call_left(self, user_id: str, chat_id: str) -> None:
        chat = self._chat_repo.get_chat_by_id(chat_id)
        for member in chat.get_members():
            await self._client_repo.send_message(client_id=member.user_id, msg_type='__LEFT-ICON-CALL__',
                                                 extra_data={'user_id': user_id,
                                                             'chat_id': chat_id})


