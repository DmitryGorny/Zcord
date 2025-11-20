# Реализации интерфейса Strategy для сервера сервисных сообщений (Server)
import json

import bcrypt

from logic.db_client.api_client import APIClient
from logic.server.Service.infrastructure.Client.Client import Client
from logic.server.Strategy import Strategy
from abc import abstractmethod, ABC
from typing import Callable


# TODO: Везде добавить проверку на success ответ от БД!!!!!!!!!!!!!!!!!!!!!!

class ChooseStrategy:
    def __init__(self):
        self.__current_strategy = None

    # sender сейчас только для message_server
    def get_strategy(self, command: str, sender: Callable, Server) -> Strategy:
        if self.__current_strategy is not None:
            if self.__current_strategy.command_name == command:
                return self.__current_strategy

        if command not in ServiceStrategy.commands.keys():
            return None

        self.__current_strategy = ServiceStrategy.commands[command]()
        self.__current_strategy.set_data(sender_to_msg_server=sender, Server_pointer=Server)
        return self.__current_strategy  # Возвращается именно объект, а не ссылка на класс


class ServiceStrategy(Strategy):
    commands = {}

    def __init_subclass__(cls, **kwargs):  # Приколдес
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "command_name"):
            cls.commands[cls.command_name] = cls

    def __init__(self):
        self._sender_to_msg_server_func = None
        self._server_pointer = None
        self._api_client: APIClient = APIClient()

    def set_data(self, **kwargs):
        self._sender_to_msg_server_func = kwargs.get("sender_to_msg_server")
        self._server_pointer = kwargs.get("Server_pointer")

    @abstractmethod
    async def execute(self, msg: dict) -> None:
        pass


class ILayer(ABC):
    """Реализация общего для нескольких стратегий функционала"""

    @abstractmethod
    def execute_layer(self, msg: dict) -> None:
        pass


class BaseLayer(ILayer):
    def __init__(self):
        self._api_client = APIClient()
        self._server_pointer = None

    def set_data(self, server_pointer):
        self._server_pointer = server_pointer

    @abstractmethod
    def execute_layer(self, msg: dict) -> None:
        pass


class ChangeChatStrategy(ServiceStrategy):
    command_name = "__change_chat__"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        chat_code = msg["chat_id"]
        user_id = str(msg["user_id"])
        client_obj = self._server_pointer.clients[user_id]

        if client_obj.message_chat_id == 0:
            client_obj.message_chat_id = chat_code
            await self._sender_to_msg_server_func("__change_chat__", {"user_id": user_id,
                                                                      "current_chat_id": 0,
                                                                      "chat_code": chat_code})
            return

        await self._sender_to_msg_server_func("__change_chat__", {"user_id": user_id,
                                                                  "current_chat_id": client_obj.message_chat_id,
                                                                  "chat_code": chat_code})

        client_obj.message_chat_id = chat_code
        return


class EndSessionStrategy(ServiceStrategy):
    command_name = "END-SESSION"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        user_id = str(msg["user_id"])
        for friend_id in self._server_pointer.clients[user_id].friends.keys():
            friend = self._server_pointer.clients[user_id].friends[friend_id]
            if friend.id not in self._server_pointer.clients:
                continue

            if friend.friendship_status == '1':
                continue

            friend_obj = self._server_pointer.clients[friend.id]

            await friend_obj.send_message('USER-STATUS', {
                "user-status": {'color': 'grey', 'user-status': 'Невидимка'},
                "nickname": self._server_pointer.clients[user_id].nick,
            })

        if not self._server_pointer.clients[user_id].writer.is_closing():
            self._server_pointer.clients[user_id].writer.close()
            await self._server_pointer.clients[user_id].writer.wait_closed()
        del self._server_pointer.clients[user_id]
        await self._sender_to_msg_server_func("END-SESSION", {"user_id": user_id})
        raise ConnectionResetError  # Чтобы задача стопалась


class RequestCacheStrategy(ServiceStrategy):
    command_name = "CACHE-REQUEST"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        user_id = str(msg["user_id"])
        client: Client = self._server_pointer.clients[user_id]

        chats_ids = []
        for chat in client.chats:
            chats_ids.append(chat)
        await self._sender_to_msg_server_func("CACHE-REQUEST", {"chats_ids": ",".join(chats_ids), 'user_id': user_id})


class UserInfoStrat(ServiceStrategy):
    command_name = "USER-INFO"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        user_id = msg["user_id"]
        nickname = msg["nickname"]
        writer = msg['writer']
        data = json.loads(msg["message"])
        id = str(data["id"])
        last_online = data["last_online"]
        friends = data["friends"]

        status = data['status']
        chats = data['chats']
        client_obj = Client(id, nickname, last_online, writer)
        client_obj.friends = friends
        client_obj.status = status
        for chat in chats:
            client_obj.add_chat(chat['chat_id'], chat['friends_id'])

        chats = {f'{chat["chat_id"]}': [] for chat in chats}

        self._server_pointer.clients[id] = client_obj
        client_ip = writer.transport.get_extra_info('socket').getpeername()

        await client_obj.send_message("__CONNECT__", {
            "connect": 1
        })

        await self._sender_to_msg_server_func("USER-INFO",
                                              {"serialize_1": self._server_pointer.serialize(chats).decode('utf-8'),
                                               "serialize_2": self._server_pointer.serialize({'user_id': str(user_id),
                                                                                              "IP": client_ip[
                                                                                                  0]}).decode('utf-8')})

        user_status = {'color': status['color'], 'user-status': status['status_name']}
        for chat_id in self._server_pointer.clients[id].friends.keys():
            friend = self._server_pointer.clients[id].friends[chat_id]
            if friend.id not in self._server_pointer.clients:
                continue

            if friend.friendship_status == '1':
                continue

            friend_obj = self._server_pointer.clients[friend.id]

            await friend_obj.send_message('USER-STATUS', {
                "user-status": user_status,
                "nickname": nickname,
            })
            try:
                friend_status = self._server_pointer.clients[friend.id].status
            except KeyError:
                continue

            await self._server_pointer.clients[id].send_message('USER-STATUS', {
                "user-status": friend_status,
                "nickname": friend_obj.nick,
            })


class SendFriendRequest(ServiceStrategy):
    command_name = "FRIENDSHIP-REQUEST-SEND"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        friend_id: str = msg['friend_id']
        user_id: str = msg['user_id']
        receiver_nick = msg['friend_nick']
        sender_nick = msg['sender_nick']

        fr_request = self._api_client.create_friendship_request(user_id, friend_id)
        if fr_request is None:
            friendship = self._api_client.get_friendship_by_id(user_id, friend_id)[0]
            if friend_id != str(friendship['user2']) and user_id != str(friendship['user1']):
                self._api_client.patch_friendship_status(friendship['id'], 2)

        self._api_client.send_friend_request(sender_id=int(user_id), receiver_id=int(friend_id),
                                             friendship_id=fr_request["id"])

        try:
            await self._server_pointer.clients[friend_id].send_message("FRIENDSHIP-REQUEST-SEND",
                                                                       {'sender_id': user_id,
                                                                        'receiver_id': friend_id,
                                                                        'sender_nick': sender_nick})
            self._server_pointer.clients[friend_id].add_friend(sender_nick,
                                                               user_id,
                                                               '1')
        except KeyError:
            pass  # TODO: подумать на очередью????

        await self._server_pointer.clients[user_id].send_message("FRIENDSHIP-REQUEST-SEND", {'sender_id': user_id,
                                                                                             'receiver_id': friend_id,
                                                                                             'receiver_nick': receiver_nick})

        self._server_pointer.clients[user_id].add_friend(receiver_nick,
                                                         friend_id,
                                                         '1')


class RecallFriendRequest(ServiceStrategy):
    command_name = "FRIENDSHIP-REQUEST-RECALL"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        friend_id: str = msg['friend_id']
        sender_id: str = msg['sender_id']

        friendship = self._api_client.get_friendship_by_id(sender_id, friend_id)[0]

        friendship_id = friendship['id']

        delete_friend_request = self._api_client.delete_friendship_request(int(sender_id), int(friend_id),
                                                                           int(friendship_id))

        if delete_friend_request is not None:
            self._api_client.delete_friendship(friendship_id)
        try:
            await self._server_pointer.clients[str(friend_id)].send_message("FRIEND-REQUEST-RECALL",
                                                                            {'sender_id': sender_id,
                                                                             'friend_id': friend_id})
            self._server_pointer.clients[str(friend_id)].delete_friend(sender_id)
        except KeyError:
            pass

        await self._server_pointer.clients[str(sender_id)].send_message("FRIEND-REQUEST-RECALL",
                                                                        {'sender_id': sender_id,
                                                                         'friend_id': friend_id})

        self._server_pointer.clients[str(sender_id)].delete_friend(str(friend_id))


class AcceptFriendRequestStrat(ServiceStrategy):
    command_name = "ACCEPT-FRIEND"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        friend_id: str = msg['receiver_id']
        sender_id: str = msg['sender_id']

        try:
            friendship = self._api_client.get_friendship_by_id(sender_id, friend_id)[0]
        except IndexError as e:
            print(e)
            return

        self._api_client.patch_friendship_status(friendship['id'], 2)
        self._api_client.create_dm_chat(friendship['id'])
        # TODO: Вот это все какая-то полная хуйня, проверить как можно получить ник отправителя на клиенте
        friend = self._api_client.get_user_by_id(int(friend_id))
        sender = self._api_client.get_user_by_id(int(sender_id))
        self._api_client.delete_friendship_request(int(sender_id), int(friend_id), friendship['id'])

        try:
            await self._server_pointer.clients[friend_id].send_message("ACCEPT-FRIEND",
                                                                       {'sender_id': sender_id,
                                                                        'friend_id': friend_id,
                                                                        'chat_id': friendship['id'],
                                                                        'friend_nickname': friend['nickname'],
                                                                        'sender_nickname': sender['nickname']})
            self._server_pointer.clients[friend_id].friends[sender_id].friendship_status = '2'
            self._server_pointer.clients[friend_id].add_chat(str(friendship['id']), [str(sender_id)])
        except KeyError as e:
            print(e)
            pass

        try:
            await self._server_pointer.clients[sender_id].send_message("ACCEPT-FRIEND", {'sender_id': sender_id,
                                                                                         'friend_id': friend_id,
                                                                                         'chat_id': friendship[
                                                                                             'id'],
                                                                                         'friend_nickname': friend[
                                                                                             'nickname'],
                                                                                         'sender_nickname': sender[
                                                                                             'nickname']})
            self._server_pointer.clients[sender_id].friends[friend_id].friendship_status = '2'
            self._server_pointer.clients[sender_id].add_chat(str(friendship['id']), [str(friend_id)])
        except KeyError as e:
            print(e)
            pass

        await self._sender_to_msg_server_func("ADD-FRIEND", {"sender_id": sender_id,
                                                             "receiver_id": friend_id,
                                                             "chat_id": friendship['id']})

        friend_obj = self._server_pointer.clients[friend_id]

        try:
            client_obj = self._server_pointer.clients[sender_id]
        except KeyError:
            return

        await client_obj.send_message('USER-STATUS', {
            "user-status": friend_obj.status,
            "nickname": friend['nickname'],
        })

        await friend_obj.send_message('USER-STATUS', {
            "user-status": client_obj.status,
            "nickname": self._server_pointer.clients[sender_id].nick,
        })


class DeclineFriendRequestStrat(ServiceStrategy):
    command_name = "DECLINE-FRIEND"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        friend_id: str = str(msg['receiver_id'])
        sender_id: str = str(msg['sender_id'])

        try:
            friendship = self._api_client.get_friendship_by_id(int(sender_id), int(friend_id))[0]
        except IndexError as e:
            print(e)
            return

        self._api_client.delete_friendship_request(int(sender_id), int(friend_id), friendship['id'])
        self._api_client.delete_friendship(friendship['id'])
        friend = self._api_client.get_user_by_id(int(friend_id))

        try:
            await self._server_pointer.clients[friend_id].send_message("DECLINE-FRIEND",
                                                                       {'sender_id': sender_id,
                                                                        'friend_id': friend_id,
                                                                        'friend_nickname': friend['nickname']
                                                                        })
            self._server_pointer.clients[friend_id].delete_friend(str(sender_id))
        except KeyError:
            pass

        try:
            await self._server_pointer.clients[sender_id].send_message("DECLINE-FRIEND",
                                                                       {'sender_id': sender_id,
                                                                        'friend_id': friend_id,
                                                                        'friend_nickname': friend['nickname']
                                                                        })
            self._server_pointer.clients[sender_id].delete_friend(str(friend_id))
        except KeyError:
            pass


class DeleteFriendRequestStrat(ServiceStrategy):
    command_name = "DELETE-FRIEND"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        friend_id: str = str(msg['receiver_id'])
        sender_id: str = str(msg['sender_id'])
        try:
            friendship = self._api_client.get_friendship_by_id(int(sender_id), int(friend_id))[0]
        except IndexError as e:
            print(e)
            return
        self._api_client.delete_friendship(friendship['id'])
        friend = self._api_client.get_user_by_id(int(friend_id))
        self._server_pointer.clients[sender_id].delete_friend(friend_id)
        chat_id = self._server_pointer.clients[sender_id].get_chat_by_user_id(friend_id).chat_id
        self._server_pointer.clients[sender_id].delete_chat_by_user_id(friend_id)

        try:
            await self._server_pointer.clients[friend_id].send_message("DELETE-FRIEND",
                                                                       {'friend_id': sender_id,
                                                                        'sender_nickname': msg['sender_nickname'],
                                                                        'chat_id': chat_id
                                                                        })
            self._server_pointer.clients[friend_id].delete_friend(sender_id)
        except KeyError:
            pass

        await self._server_pointer.clients[sender_id].send_message("DELETE-FRIEND",
                                                                   {'friend_id': friend_id,
                                                                    'friend_nickname': friend['nickname'],
                                                                    'chat_id': chat_id
                                                                    })

        await self._sender_to_msg_server_func('DELETE-FRIEND', {'chat_id': chat_id})


class UserStatusStrat(ServiceStrategy):
    command_name = "USER-STATUS"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        user_status = msg['status_name']
        color = msg['color']
        user_id: str = str(msg['user_id'])
        nickname: str = msg['nickname']

        user_status = {'color': color, 'user-status': user_status}
        self._server_pointer.clients[user_id].status = user_status
        await self._server_pointer.clients[user_id].send_message('USER-STATUS', {
            "user-status": user_status,
            "nickname": nickname,
        })

        for chat_id in self._server_pointer.clients[user_id].friends.keys():
            friend = self._server_pointer.clients[user_id].friends[chat_id]

            if str(friend.id) not in self._server_pointer.clients:
                continue

            if str(friend.friendship_status) == '1':
                continue

            friend_obj = self._server_pointer.clients[friend.id]

            await friend_obj.send_message('USER-STATUS', {
                "user-status": user_status,
                "nickname": nickname,
            })


class CallNotificationStrat(ServiceStrategy):
    """Уведомление звонка"""
    command_name = "__CALL-NOTIFICATION__"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        user_id = msg["user_id"]
        chat_id = msg["chat_id"]
        call_flag = msg["call_flg"]
        print("Сервер принял ивент звонка")
        chat = self._server_pointer.clients[str(user_id)].get_chat_by_id(str(chat_id))

        for member in chat.get_members():
            if member.id not in self._server_pointer.clients.keys():
                continue
            await self._server_pointer.clients[member.id].send_message('__CALL-NOTIFICATION__',
                                                                       {'user_id': user_id,
                                                                        'chat_id': chat_id,
                                                                        'call_flg': call_flag})


class AddUserToGroupLayer(BaseLayer):
    def __init__(self):
        super(AddUserToGroupLayer, self).__init__()

    def execute_layer(self, msg: dict) -> None:
        request_receiver = str(msg['user_id'])
        group_id = str(msg['group_id'])

        try:
            group = self._api_client.search_chat_by_id(int(group_id), True)[0]
        except IndexError as e:  # TODO: Придумать че-нить чтобы уведомить пользователя об удалении группы
            print(e)
            return

        # TODO: Везде ли чаты создаются по id из chats db?
        self._server_pointer.clients[request_receiver].add_chat(group['id'], group['group']['members'])

        for members_id in group['group']['members']:
            try:
                member_client = self._server_pointer.clients[str(members_id)]
                member_client.send_message('USER-JOINED-GROUP', {'user_id': request_receiver,
                                                                 'group_id': group_id,
                                                                 'group_name': group['group']["group_name"],
                                                                 'members': group['group']['members']})
                chat = member_client.get_chat_by_id(group_id)
                chat.create_and_add_member(request_receiver)
            except KeyError as e:
                print(e)

        self._api_client.add_group_member(int(request_receiver), int(group_id))
        self._server_pointer.clients[request_receiver].send_message('USER-JOINED-GROUP',
                                                                    {'user_id': request_receiver,
                                                                     'group_id': group_id})


class GroupRequestAcceptStrat(ServiceStrategy):
    command_name = "GROUP-REQUEST-ACCEPTED"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        request_receiver = str(msg['user_id'])
        group_id = str(msg['group_id'])
        request_id = str(msg['request_id'])

        add_user_layer = AddUserToGroupLayer()
        add_user_layer.set_data(self._server_pointer)
        add_user_layer.execute_layer(msg)

        self._api_client.delete_request(request_id)

        nickname = self._server_pointer.clients[request_receiver].nick
        await self._sender_to_msg_server_func('CHAT-MESSAGE', {'chat_id': group_id,
                                                               'user_id': self._server_pointer.clients[
                                                                   request_receiver].id,
                                                               'type': 'service',
                                                               'service_message': f'Пользователь {nickname} присоединился к группе'})


class GroupRejectAcceptStrat(ServiceStrategy):
    command_name = "GROUP-REQUEST-REJECTED"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        request_id = str(msg['request_id'])
        self._api_client.delete_request(request_id)


class UserLeftGroupStrat(ServiceStrategy):
    command_name = "USER-LEFT-GROUP"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        request_receiver = str(msg['user_id'])
        group_id = str(msg['group_id'])

        try:
            group = self._api_client.search_chat_by_id(int(group_id), True)[0]
        except IndexError as e:  # TODO: Придумать че-нить чтобы уведомить пользователя об удалении группы
            print(e)
            return

        # TODO: Везде ли чаты создаются по id из chats?
        self._server_pointer.clients[request_receiver].delete_chat(group['id'])

        for members_id in group['group']['members']:
            try:
                member_client = self._server_pointer.clients[str(members_id)]
                member_client.send_message('USER-LEFT-GROUP', {'user_id': request_receiver,
                                                               'group_id': group_id})
                chat = member_client.get_chat_by_id(group_id)
                chat.delete_member_by_id(request_receiver)
            except KeyError as e:
                print(e)

        row_id = self._api_client.search_group_member(int(request_receiver), int(group_id))['id']
        self._api_client.delete_group_member_by_id(row_id)
        self._server_pointer.clients[request_receiver].send_message('USER-LEFT-GROUP',
                                                                    {'user_id': request_receiver,
                                                                     'group_id': group_id})

        nickname = self._server_pointer.clients[request_receiver].nick
        await self._sender_to_msg_server_func('CHAT-MESSAGE', {'chat_id': group_id,
                                                               'user_id': self._server_pointer.clients[
                                                                   request_receiver].id,
                                                               'type': 'service',
                                                               'service_message': f'Пользователь {nickname} покинул группу'})


class CreateGroupStrat(ServiceStrategy):  # TODO: Добавить создание чата в классе Client
    command_name = "GROUP-CREATE"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        creator_id = str(msg['user_id'])
        group_name = msg['group_name']
        is_private = msg['is_private']
        is_invite_from_admin = msg['is_invite_from_admin']
        is_password = msg['is_password']
        password = msg['password']

        if is_password:
            password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')

        group = self._api_client.create_group(group_name=group_name,
                                              is_private=is_private,
                                              is_invite_from_admin=is_invite_from_admin,
                                              is_password=is_password,
                                              password=password,
                                              admin_id=int(creator_id))

        try:
            group_id = group['id']
        except KeyError:
            self._server_pointer.clients[creator_id].send_message('GROUP-CREATION-ERROR')
            return

        self._api_client.create_group_chat(group_id)

        member = self._api_client.add_group_admin(int(creator_id), group_id)

        try:
            member['id']
            del group['password']
            await self._server_pointer.clients[creator_id].send_message('GROUP-CREATED-SUCCESS', {'group_json': group})
        except KeyError:
            self._server_pointer.clients[creator_id].send_message('GROUP-CREATION-ERROR')
            return

        await self._sender_to_msg_server_func('CREATE-GROUP', {'chat_id': group_id,
                                                               'creator_id': creator_id})
