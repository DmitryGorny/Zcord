import bcrypt

from logic.server.Service.core.MessageServiceCommunication.IMessageServiceDispatcher import IMessageServiceDispatcher
from logic.server.Service.core.repositroies.chat_repo.IChatDBRepo import IChatDBRepo
from logic.server.Service.core.repositroies.chat_repo.IChatRepo import IChatRepo
from logic.server.Service.core.repositroies.client_repo.IClientRepo import IClientRepo
from logic.server.Service.core.services.chat.IChatService import IChatService


class ChatService(IChatService):
    def __init__(self,
                 client_repo: IClientRepo,
                 chat_repo: IChatRepo,
                 chat_db_rp: IChatDBRepo,
                 msg_communication: IMessageServiceDispatcher):
        self._chat_repo: IChatRepo = chat_repo
        self._chat_db_repo: IChatDBRepo = chat_db_rp
        self._msg_server_communication: IMessageServiceDispatcher = msg_communication
        self._client_repo: IClientRepo = client_repo

    async def cache_request(self, user_id: str) -> None:
        chats = self._chat_repo.get_chats_by_user_id(user_id)

        chats_ids = []
        for chat in chats:
            chats_ids.append(chat.chat_id)
        await self._msg_server_communication.send_msg_server("CACHE-REQUEST",
                                                             {"chats_ids": ",".join(chats_ids), 'user_id': user_id})

    async def change_chat(self, chat_code: int, user_id: str) -> None:
        current_id = self._client_repo.get_clients_current_chat(client_id=user_id)
        if current_id is None:
            return

        if current_id == 0:
            new_id = self._client_repo.set_client_current_chat(client_id=user_id, chat_id=chat_code)
            if not new_id:
                return  # TODO: Сделать повторынй change_chat

            await self._msg_server_communication.send_msg_server("__change_chat__", {"user_id": user_id,
                                                                                     "current_chat_id": 0,
                                                                                     "chat_code": chat_code})
            return

        new_id = self._client_repo.set_client_current_chat(client_id=user_id, chat_id=chat_code)
        if not new_id:
            return  # TODO: Сделать повторынй change_chat

        await self._msg_server_communication.send_msg_server("__change_chat__", {"user_id": user_id,
                                                                                 "current_chat_id": current_id,
                                                                                 "chat_code": chat_code})

    async def add_user_group(self, request_receiver: str, group_id: str, request_id: str) -> None:
        group = self._chat_db_repo.search_chat_by_id(chat_id=int(group_id), is_group=True)
        for members_id in group['group']['members']:
            try:
                chat = self._chat_repo.get_chat_by_id(group_id)
                await self._client_repo.send_message(members_id, 'USER-JOINED-GROUP', {'user_id': request_receiver,
                                                                                       'group_id': group_id,
                                                                                       'group_name': group['group'][
                                                                                           "group_name"],
                                                                                       'members': group['group'][
                                                                                           'members']})
                chat.create_and_add_member(request_receiver)
            except KeyError as e:
                print(e)

        self._chat_db_repo.add_group_member(int(request_receiver), int(group_id))
        await self._client_repo.send_message(request_receiver, 'USER-JOINED-GROUP',
                                             {'user_id': request_receiver,
                                              'group_id': group_id})

        self._chat_db_repo.delete_group_request(int(request_id))
        nickname = self._client_repo.get_client_nick(client_id=request_receiver)
        await self._msg_server_communication.send_msg_server('CHAT-MESSAGE', {'chat_id': group_id,
                                                                              'user_id': request_receiver,
                                                                              'type': 'service',
                                                                              'service_message': f'Пользователь {nickname} присоединился к группе'})

    def group_request_rejected(self, request_id: str) -> None:
        self._chat_db_repo.delete_group_request(int(request_id))

    async def user_left_group(self, request_receiver: str, group_id: str) -> None:
        group = self._chat_db_repo.search_chat_by_id(chat_id=int(group_id), is_group=True)
        for members_id in group['group']['members']:
            try:
                chat = self._chat_repo.get_chat_by_id(group_id)
                await self._client_repo.send_message(members_id, 'USER-LEFT-GROUP', {'user_id': request_receiver,
                                                                                     'group_id': group_id,
                                                                                     'group_name': group['group'][
                                                                                         "group_name"],
                                                                                     'members': group['group'][
                                                                                         'members']})
                chat.delete_member_by_id(request_receiver)
                if chat.get_members_len() == 0:
                    self._chat_repo.delete_chat(chat.chat_id)
            except KeyError as e:
                print(e)

        row_id = self._chat_db_repo.search_group_member(int(request_receiver), int(group_id))['id']
        self._chat_db_repo.delete_group_member_by_id(row_id)
        await self._client_repo.send_message(request_receiver, 'USER-LEFT-GROUP',
                                             {'user_id': request_receiver,
                                              'group_id': group_id})

        nickname = self._client_repo.get_client_nick(client_id=request_receiver)
        await self._msg_server_communication.send_msg_server('CHAT-MESSAGE', {'chat_id': group_id,
                                                                              'user_id': request_receiver,
                                                                              'type': 'service',
                                                                              'service_message': f'Пользователь {nickname} покинул группу'})

    async def create_group(self, creator_id: str, group_name: str, is_private: bool,
                           is_invite_from_admin: bool, is_password: bool, password: bool) -> None:
        if is_password:
            password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')

        group = self._chat_db_repo.create_group(group_name=group_name,
                                                is_private=is_private,
                                                is_invite_from_admin=is_invite_from_admin,
                                                is_password=is_password,
                                                password=password,
                                                creator_id=creator_id)

        try:
            group_id = group['id']
        except KeyError:
            await self._client_repo.send_message(creator_id, 'GROUP-CREATION-ERROR', extra_data={})
            return

        self._chat_db_repo.create_group_chat(group_id)

        member = self._chat_db_repo.add_group_admin(int(creator_id), group_id)

        try:
            member['id']
            del group['password']
            await self._client_repo.send_message(creator_id, 'GROUP-CREATED-SUCCESS', {'group_json': group})
        except KeyError:
            await self._client_repo.send_message(creator_id, 'GROUP-CREATION-ERROR', extra_data={})
            return

        await self._msg_server_communication.send_msg_server('CREATE-GROUP', {'chat_id': group_id,
                                                                              'creator_id': creator_id})
