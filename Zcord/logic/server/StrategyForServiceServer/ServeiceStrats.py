# Реализации интерфейса Strategy для сервера сервисных сообщений (Server)
from datetime import timedelta

import msgspec

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
        nickname = msg["nickname"]
        client_obj = self._server_pointer.clients[nickname]

        if client_obj.message_chat_id == 0:
            client_obj.message_chat_id = chat_code
            await self._sender_to_msg_server_func("__change_chat__", {"nickname": nickname,
                                                                      "current_chat_id": 0,
                                                                      "chat_code": chat_code})
            return

        await self._sender_to_msg_server_func("__change_chat__", {"nickname": nickname,
                                                                  "current_chat_id": client_obj.message_chat_id,
                                                                  "chat_code": chat_code})

        client_obj.message_chat_id = chat_code
        return


class EndSessionStrategy(ServiceStrategy):
    command_name = "END-SESSION"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        nickname = msg["nickname"]
        if not self._server_pointer.clients[nickname].writer.is_closing():
            self._server_pointer.clients[nickname].writer.close()
            await self._server_pointer.clients[nickname].writer.wait_closed()
        del self._server_pointer.clients[nickname]
        await self._sender_to_msg_server_func("END-SESSION", {"nickname": nickname})
        raise ConnectionResetError  # Чтобы задача стопалась


class RequestCacheStrategy(ServiceStrategy):
    command_name = "CACHE-REQUEST"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        nickname = msg["nickname"]
        client: Client = self._server_pointer.clients[nickname]

        chats_ids = []
        for chat_id in client.friends:
            time_period = timedelta(days=72)
            if client.last_online - client.friends[chat_id].last_online < time_period:
                chats_ids.append(chat_id)

        await self._sender_to_msg_server_func("CACHE-REQUEST", {"chats_ids": ",".join(chats_ids)})
