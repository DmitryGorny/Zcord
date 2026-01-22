import json
from typing import Union

import bcrypt

from logic.server.Service.core.MessageServiceCommunication.IMessageServiceDispatcher import IMessageServiceDispatcher
from logic.server.Service.core.repositroies.chat_repo.IChatDBRepo import IChatDBRepo
from logic.server.Service.core.repositroies.chat_repo.IChatRepo import IChatRepo
from logic.server.Service.core.repositroies.client_repo.IClientDBRepo import IClientDBRepo
from logic.server.Service.core.repositroies.client_repo.IClientRepo import IClientRepo
from logic.server.Service.core.services.chat.IChatService import IChatService


class ChatService(IChatService):
    def __init__(self,
                 client_repo: IClientRepo,
                 chat_repo: IChatRepo,
                 chat_db_rp: IChatDBRepo,
                 client_db_repo: IClientDBRepo,
                 msg_communication: IMessageServiceDispatcher):
        self._chat_repo: IChatRepo = chat_repo
        self._chat_db_repo: IChatDBRepo = chat_db_rp
        self._msg_server_communication: IMessageServiceDispatcher = msg_communication
        self._client_repo: IClientRepo = client_repo
        self._client_db_repo = client_db_repo

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

    async def add_user_group(self, request_receiver: str, group_id: str, receiver_nick: str,
                             request_id: str = None) -> None:
        self._chat_db_repo.add_group_member(int(request_receiver), int(group_id))
        if request_id is not None:
            self._chat_db_repo.delete_group_request(int(request_id))

        group = self._chat_db_repo.search_chat_by_inner_id(chat_id=int(group_id), is_group=True)[0]

        members_activity = {}
        chat = self._chat_repo.get_chat_by_id(str(group['id']))
        if chat is None:
            chat_created = await self._init_group_by_inner_id(group_id, request_receiver)
            if not chat_created:
                print('[ChatService] Chat wasnt created')
                return
            chat = self._chat_repo.get_chat_by_id(str(group['id']))

        chat.create_and_add_member(request_receiver, receiver_nick)
        members = chat.get_members()
        for member in members:
            client_status = self._client_repo.get_client_online_stat(client_id=member.user_id)
            if client_status is None:
                members_activity[member.user_id] = 'hidden'
                continue
            members_activity[member.user_id] = client_status['status_instance']

            if member.user_id == request_receiver:
                continue

            await self._client_repo.send_message(str(member.user_id), 'USER-JOINED-GROUP',
                                                 {'user_id': request_receiver,
                                                  'group_id': group['id'],
                                                  'group_name': group['group']["group_name"],
                                                  'is_private': group['group']['is_private'],
                                                  'is_password': group['group']['is_password'],
                                                  'is_admin_invite': group['group']['is_invite_from_admin'],
                                                  'admin_id': group['group']['user_admin'],
                                                  'status_instance': self._client_repo.get_client_online_stat(
                                                      request_receiver)
                                                  })

        await self._client_repo.send_message(request_receiver, 'USER-JOINED-GROUP',
                                             {'user_id': request_receiver,
                                              'group_id': group['id'],
                                              'group_name': group['group']["group_name"],
                                              'is_private': group['group']['is_private'],
                                              'is_password': group['group']['is_password'],
                                              'is_admin_invite': group['group']['is_invite_from_admin'],
                                              'admin_id': group['group']['user_admin'],
                                              'members_activity': members_activity
                                              })

        nickname = self._client_repo.get_client_nick(client_id=request_receiver)
        await self._msg_server_communication.send_msg_server(msg_type='CHAT-MESSAGE', mes_data={'chat_id': group['id'],
                                                                                                'user_id': request_receiver,
                                                                                                'type': 'service',
                                                                                                'service_message': f'Пользователь {nickname} присоединился к группе'})

    async def group_request_rejected(self, request_id: str, receiver_id: str, group_id: str) -> None:
        self._chat_db_repo.delete_group_request(int(request_id))

        await self._client_repo.send_message(receiver_id, 'GROUP-REQUEST-REJECTED',
                                             {'user_id': receiver_id})

        receiver_nickname = self._client_repo.get_client_nick(receiver_id)
        if receiver_nickname is None:
            receiver_nickname = self._client_db_repo.get_user_by_id(int(receiver_id))['nickname']

        chat = self._chat_db_repo.search_chat_by_inner_id(chat_id=int(group_id), is_group=True)[0]

        await self._msg_server_communication.send_msg_server('CHAT-MESSAGE', {'chat_id': chat['id'],
                                                                              'user_id': receiver_id,
                                                                              'type': 'service',
                                                                              'service_message': f'Пользователь {receiver_nickname} отклонил приглашение'})

    async def user_left_group(self, request_receiver: str, group_id: str) -> None:  #### Сделать проверку на админа
        group = self._chat_db_repo.get_chat_by_id(chat_id=int(group_id))  # TODO: Отработать ошибку
        nickname: str
        try:
            chat = self._chat_repo.get_chat_by_id(group_id)
            user = chat.get_member_by_id(request_receiver)
            nickname = user.username
        except KeyError as e:
            print('[ChatService] {}'.format(e))
            return

        for user in group['group']['users']:
            members_id = user.get('user_id')
            try:
                await self._client_repo.send_message(members_id, 'USER-LEFT-GROUP', {'user_id': request_receiver,
                                                                                     'group_id': group_id,
                                                                                     })
                chat.delete_member_by_id(request_receiver)
                if chat.get_members_len() == 0:
                    self._chat_repo.delete_chat(chat.chat_id)
            except KeyError as e:
                print('[ChatService] {}'.format(e))

        row_id = self._chat_db_repo.search_group_member(int(request_receiver), group['group']['id'])[0]['id']
        self._chat_db_repo.delete_group_member_by_id(row_id)
        await self._msg_server_communication.send_msg_server('CHAT-MESSAGE', {'chat_id': group_id,
                                                                              'user_id': request_receiver,
                                                                              'type': 'service',
                                                                              'service_message': f'Пользователь {nickname} покинул группу'})
        if group['group']['user_admin'] == int(request_receiver):
            try:
                await self.change_admin(str(group_id), str(group['group']['id']), chat.get_members()[0].user_id)
            except Exception as e:
                print('[ChatService] {}'.format(e))

    async def send_group_request(self, sender_id: str, receiver_id: str, group_id: str) -> None:
        request = self._chat_db_repo.send_group_request(group_id=int(group_id),
                                                        sender_id=int(sender_id),
                                                        receiver_id=int(receiver_id))
        if request is None:
            return

        await self._client_repo.send_message(sender_id, 'GROUP-REQUEST-SENT',
                                             {'group_id': group_id})

        await self._client_repo.send_message(receiver_id, 'GROUP-REQUEST',
                                             {'sender_id': sender_id,
                                              'group_id': group_id,
                                              'request_id': request['id'],
                                              'group_name': request['group']['group_name']})

        sender_nickname = self._client_repo.get_client_nick(sender_id)

        receiver_nickname = self._client_repo.get_client_nick(receiver_id)
        if receiver_nickname is None:
            receiver_nickname = self._client_db_repo.get_user_by_id(int(receiver_id))['nickname']

        chat = self._chat_db_repo.search_chat_by_inner_id(chat_id=int(group_id), is_group=True)[0]

        await self._msg_server_communication.send_msg_server('CHAT-MESSAGE', {'chat_id': str(chat['id']),
                                                                              'user_id': sender_nickname,
                                                                              'type': 'service',
                                                                              'service_message': f'Пользователь {sender_nickname} пригласил {receiver_nickname} в группу'})

    async def create_group(self, creator_id: str, group_name: str, is_private: bool,
                           is_invite_from_admin: bool, is_password: bool, password: bool, members: list[str]) -> None:
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

        group_chat = self._chat_db_repo.create_group_chat(group_id)

        member = self._chat_db_repo.add_group_admin(int(creator_id), group_id)

        try:
            member['id']
            del group['password']
            await self._client_repo.send_message(creator_id, 'GROUP-CREATED-SUCCESS', {'group_json': group_chat})
        except KeyError:
            await self._client_repo.send_message(creator_id, 'GROUP-CREATION-ERROR', extra_data={})
            return

        await self._msg_server_communication.send_msg_server('CREATE-GROUP', {'chat_id': group_chat['id'],
                                                                              'creator_id': creator_id})
        if len(members) > 0:
            for member_id in members:
                await self.send_group_request(receiver_id=member_id, group_id=group_id, sender_id=creator_id)

    async def change_admin(self, chat_id: str, group_id: str, new_admin_id: str) -> None:
        try:
            chat = self._chat_repo.get_chat_by_id(chat_id)
        except KeyError as e:
            print('[ChatService] {}'.format(e))
            return
        admin = chat.get_member_by_id(str(new_admin_id))

        if admin is None:
            return

        self._chat_db_repo.change_group_admin(int(group_id), int(new_admin_id))

        for member in chat.get_members():
            try:
                await self._client_repo.send_message(member.user_id, 'GROUP-ADMIN-CHANGED',
                                                     {'new_admin_id': new_admin_id,
                                                      'chat_id': chat_id,
                                                      })
            except KeyError as e:
                print('[ChatService] {}'.format(e))

        nickname = admin.username
        await self._msg_server_communication.send_msg_server('CHAT-MESSAGE', {'chat_id': chat_id,
                                                                              'user_id': new_admin_id,
                                                                              'type': 'service',
                                                                              'service_message': f'Пользователь {nickname} новый администратор'})

    async def change_group_settings(self, group_id: str, sender_id: str, new_settings: dict[str, Union[str, bool]],
                                    flags: dict[str, bool]):
        chat = self._chat_db_repo.get_chat_by_id(int(group_id))

        if chat is None or not chat['is_group']:
            await self._client_repo.send_message(sender_id, 'SETTINGS-CHANGE-ERROR',
                                                 {'error_name': 'Ошибка', 'chat_id': group_id})
            return

        if chat['group']['user_admin'] != int(sender_id):
            await self._client_repo.send_message(sender_id, 'SETTINGS-CHANGE-ERROR',
                                                 {'error_name': 'Вы не администратор', 'chat_id': group_id})
            return

        if len(new_settings.keys()) == 0:
            await self._client_repo.send_message(sender_id, 'SETTINGS-CHANGE-ERROR',
                                                 {'error_name': 'Ошибка', 'chat_id': group_id})
            return

        if not flags.get('password_changed'):
            new_settings.pop('password')

        changed = self._chat_db_repo.change_group_settings(chat['group']['id'], new_settings)

        if changed is None:
            await self._client_repo.send_message(sender_id, 'SETTINGS-CHANGE-ERROR',
                                                 {'error_name': 'Ошибка', 'chat_id': group_id})
            return

        chat = self._chat_repo.get_chat_by_id(group_id)

        name_changed = False
        for member in chat.get_members():
            await self._client_repo.send_message(member.user_id, 'GROUP-CHANGED-SETTINGS',
                                                 extra_data={'chat_id': group_id,
                                                             'new_settings': json.dumps(new_settings)})

            if flags.get('name_changed'):
                name_changed = True
                await self._client_repo.send_message(member.user_id, 'GROUP-CHANGED-NAME',
                                                     extra_data={'chat_id': group_id,
                                                                 'new_name': new_settings.get('group_name')})

        if name_changed:
            await self._msg_server_communication.send_msg_server('CHAT-MESSAGE', {'chat_id': group_id,
                                                                                  'user_id': sender_id,
                                                                                  'type': 'service',
                                                                                  'service_message': f'Название группы было изменено на {new_settings.get("group_name")}'})

    async def _init_group_by_inner_id(self, group_id: str, user_id: str) -> bool:
        try:
            group = self._chat_db_repo.search_chat_by_inner_id(chat_id=int(group_id), is_group=True)[0]
        except KeyError as e:
            print('[ChatService] {}'.format(e))
            return False
        self._chat_repo.add_chat(str(group['id']), group['group']['users'])
        await self._msg_server_communication.send_msg_server("INIT-CHAT", {"users_id": [user_id],
                                                                           "chat_id": group['id']})
        return True
