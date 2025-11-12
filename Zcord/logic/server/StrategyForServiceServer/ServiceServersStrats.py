import json
from datetime import timedelta, datetime

from logic.db_client.api_client import APIClient
from logic.server.Client.Client import Client
from logic.server.Strategy import Strategy
from abc import abstractmethod
from typing import Callable


class ChooseServerStrategy:
    def __init__(self):
        self.__current_strategy = None

    def get_strategy(self, command: str, Server) -> Strategy:
        if self.__current_strategy is not None:
            if self.__current_strategy.command_name == command:
                return self.__current_strategy

        if command not in ServiceStrategy.commands.keys():
            return None

        self.__current_strategy = ServiceStrategy.commands[command]()
        self.__current_strategy.set_data(Server_pointer=Server)
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
        self._server_pointer = kwargs.get("Server_pointer")

    @abstractmethod
    async def execute(self, msg: dict) -> None:
        pass


class CallConnectionIconStrategy(ServiceStrategy):
    """Добавление иконки пользователей которые находятся в звонке"""

    command_name = "__ICON-CALL__"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        user_id = msg["user_id"]
        chat_id = msg["chat_id"]
        username = msg["username"]
        chat = self._server_pointer.clients[str(user_id)].get_chat_by_id(str(chat_id))
        for member in chat.get_members():
            await self._server_pointer.clients[member.id].send_message('__ICON-CALL__',
                                                                            {'user_id': user_id,
                                                                        'username': username,
                                                                        'chat_id': chat_id})


class CallConnectionIconLeftStrategy(ServiceStrategy):
    """Удаление иконки пользователей которые находятся в звонке"""

    command_name = "__LEFT-ICON-CALL__"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        user_id = msg["user_id"]
        chat_id = msg["chat_id"]
        chat = self._server_pointer.clients[str(user_id)].get_chat_by_id(str(chat_id))
        for member in chat.get_members():
            await self._server_pointer.clients[member.id].send_message('__LEFT-ICON-CALL__',
                                                                            {'user_id': user_id,
                                                                        'chat_id': chat_id})
