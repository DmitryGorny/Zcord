# Реализации интерфейса Strategy для сервера сервисных сообщений (Server)
import json
from datetime import timedelta

from logic.server.Client.Client import Client
from logic.server.Strategy import Strategy
from abc import abstractmethod
from typing import Callable


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

    def set_data(self, **kwargs):
        self._sender_to_msg_server_func = kwargs.get("sender_to_msg_server")
        self._server_pointer = kwargs.get("Server_pointer")

    @abstractmethod
    async def execute(self, msg: dict) -> None:
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
        for chat_id in client.friends:
            time_period = timedelta(days=72)  # TODO: Переделать на 7 или убрать?????????
            if client.last_online - client.friends[chat_id].last_online < time_period:
                chats_ids.append(chat_id)

        await self._sender_to_msg_server_func("CACHE-REQUEST", {"chats_ids": ",".join(chats_ids), 'user_id': user_id})


class UserInfoStrat(ServiceStrategy):
    command_name = "USER-INFO"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        print(2131)
        user_id = msg["user_id"]
        nickname = msg["nickname"]
        writer = msg['writer']

        data = json.loads(msg["message"])
        id = str(data["id"])
        last_online = data["last_online"]
        friends = data["friends"]
        status = data['status']
        chats = data['chats']
        print(chats)
        client_obj = Client(id, nickname, last_online, writer)
        client_obj.friends = friends
        client_obj.status = status
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


class CallNotificationStrategy(ServiceStrategy):
    """Уведомление звонка"""
    command_name = "__CALL-NOTIFICATION__"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None: #TODO: Переделать список друхей для зранения групп
        user_id = msg["user_id"]
        chat_id = msg["chat_id"]
        call_flag = msg["call_flg"]
        print("Сервер принял ивент звонка")
        friend = self._server_pointer.clients[user_id].friends[str(chat_id)]
        friend_id = friend.id
        await self._server_pointer.clients[int(friend_id)].send_message('__CALL-NOTIFICATION__', {'user_id': user_id,
                                                                                           'chat_id': chat_id,
                                                                                           'call_flg': call_flag})
