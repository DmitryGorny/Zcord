#Реализации стратегий для сервера сообщений (message-server)
import json

from logic.server.Strategy import Strategy
from abc import abstractmethod, ABC
from typing import Callable
from logic.server.StrategyForServiceServer.ServeiceStrats import ServiceStrategy

class ChooseStrategy:
    def __init__(self):
        self.__current_strategy = None

    def get_strategy(self, command: str, Server) -> Strategy:
        if self.__current_strategy is not None:
            if self.__current_strategy.command_name == command:
                return self.__current_strategy

        if command not in MessageStrategy.commands.keys():
            return None

        self.__current_strategy = MessageStrategy.commands[command]()
        self.__current_strategy.set_data(messageRoom_pointer=Server)
        return self.__current_strategy

class MessageStrategy(ServiceStrategy):
    def __init__(self):
        super(MessageStrategy, self).__init__()
        self._messageRoom_pointer = None

    def set_data(self, **kwargs):
        self._messageRoom_pointer = kwargs.get("messageRoom_pointer")


class ChangeChatStrategy(MessageStrategy):
    command_name = "__change_chat__"

    def __init__(self):
        super(ChangeChatStrategy, self).__init__()

    def execute(self, msg: dict) -> None:
        server_msg = msg["message"].split("&-&")

        try: #Я боюсь какого-нибудь неотловленного рассинхрона nicknames_in_chats здесь и с сервером, поэтому будем это отлавливать
            if server_msg[1] != server_msg[2]:
                self._messageRoom_pointer.nicknames_in_chats[server_msg[1]].remove(server_msg[0])
            self._messageRoom_pointer.nicknames_in_chats[server_msg[2]].append(server_msg[0])
        except ValueError:
            print(1111111) #Дописать запрос на сервер для синхронизации


class UserInfoStrategy(MessageStrategy):
    command_name = "USER-INFO"

    def __init__(self):
        super(UserInfoStrategy, self).__init__()

    def execute(self,  msg: dict) -> None:
        msg = msg["message"].split("&-&")
        self._messageRoom_pointer.copyCacheChat(json.loads(msg[1]))
        msg = json.loads(msg[2])
        self._messageRoom_pointer.clients[list(msg.keys())[0]] = msg[list(msg.keys())[0]]


class EndSession(MessageStrategy):
    command_name = "END-SESSION"

    def __init__(self):
        super(EndSession, self).__init__()

    def execute(self,  msg: dict) -> None:
        nickname = msg["message"]
        self._messageRoom_pointer.clients[nickname].close()
        self._messageRoom_pointer.clients.pop(nickname)

        print(self._messageRoom_pointer.nicknames_in_chats)
        for id_chat in self._messageRoom_pointer.nicknames_in_chats.keys():  #TODO: Слишком медленно
            if nickname in self._messageRoom_pointer.nicknames_in_chats[id_chat]:
                self._messageRoom_pointer.nicknames_in_chats[id_chat].remove(nickname)

