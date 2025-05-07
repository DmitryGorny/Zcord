# Реализации интерфейса Strategy для сервера сервисных сообщений (Server)
from logic.server.Strategy import Strategy
from abc import abstractmethod
from typing import Callable


class ChooseStrategy:
    def __init__(self):
        self.__current_strategy = None

    def get_strategy(self, command: str, sender: Callable, Server) -> Strategy:
        if self.__current_strategy is not None:
            if self.__current_strategy.command_name == command:
                return self.__current_strategy
        print(ServiceStrategy.commands)
        print(command)
        if command not in ServiceStrategy.commands.keys():
            return None

        self.__current_strategy = ServiceStrategy.commands[command]()
        self.__current_strategy.set_data(sender, Server)
        return self.__current_strategy  # Возвращается именно объект, а не ссылка на класс


class ServiceStrategy(Strategy):
    commands = {}

    def __init_subclass__(cls, **kwargs):  # Приколдес
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "command_name"):
            cls.commands[cls.command_name] = cls

    def __init__(self):
        self._sender_func = None
        self._server_pointer = None

    def set_data(self, sender: Callable, Server_pointer):
        self._sender_func = sender
        self._server_pointer = Server_pointer

    @abstractmethod
    async def execute(self, **kwargs) -> None:
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
            await self._sender_func(f"__change_chat__&-&{nickname}&-&{client_obj.message_chat_id}&-&{chat_code}")
            return

        client_chatID = str(client_obj.message_chat_id)
        if nickname not in self._server_pointer.nicknames_in_chats[client_chatID]:
            self._server_pointer.nicknames_in_chats[client_chatID].append(nickname)

        try:
            if chat_code != client_chatID:
                index = self._server_pointer.nicknames_in_chats[client_chatID].index(nickname)
                self._server_pointer.nicknames_in_chats[client_chatID].pop(index)
        except UnboundLocalError as e:
            print(e)
        except KeyError as e:
            print(e)
        await self._sender_func(f"__change_chat__&-&{nickname}&-&{client_obj.message_chat_id}&-&{chat_code}")

        client_obj.message_chat_id = chat_code
        return


class EndSessionStrategy(ServiceStrategy):
    command_name = "END-SESSION"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        nickname = msg["nickname"]
        del self._server_pointer.clients[nickname]
        await self._sender_func(f"__END-SESSION__&-&{nickname}")
