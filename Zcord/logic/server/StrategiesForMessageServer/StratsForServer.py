# Реализации стратегий для сервера сообщений (message-server)
import json
from datetime import datetime

from logic.db_handler.api_client import APIClient
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
        self._api_client: APIClient = APIClient()

    def set_data(self, **kwargs):
        self._messageRoom_pointer = kwargs.get("messageRoom_pointer")


class ChangeChatStrategy(MessageStrategy):
    command_name = "__change_chat__"

    def __init__(self):
        super(ChangeChatStrategy, self).__init__()

    def execute(self, msg: dict) -> None:
        nickname = msg["nickname"]
        current_chat_id = str(msg["current_chat_id"])
        chat_code = str(msg["chat_code"])

        try:
            self._messageRoom_pointer.nicknames_in_chats[current_chat_id].remove(nickname)
        except ValueError:
            print(1111111)
        except KeyError:
            print("Клик по тому же чату")
        self._messageRoom_pointer.nicknames_in_chats[chat_code].append(nickname)
        print(self._messageRoom_pointer.nicknames_in_chats[chat_code])
        if len(self._messageRoom_pointer.cache_chat[chat_code]) == 0:
            return

        self._messageRoom_pointer.send_cache(self._messageRoom_pointer.cache_chat[chat_code][-20:], nickname)


class UserInfoStrategy(MessageStrategy):
    """Юзер подключается, по нему приходит информаця с основного сервера"""
    command_name = "USER-INFO"

    def __init__(self):
        super(UserInfoStrategy, self).__init__()

    def execute(self, msg: dict) -> None:
        nickname = msg["nickname"]
        serialize_1 = msg["serialize_1"]
        serialize_2 = msg["serialize_2"]

        self._messageRoom_pointer.copyCacheChat(json.loads(serialize_1))
        msg = json.loads(serialize_2)
        self._messageRoom_pointer.clients[list(msg.keys())[0]] = msg[list(msg.keys())[0]]


class EndSessionStrat(MessageStrategy):
    command_name = "END-SESSION"

    def __init__(self):
        super(EndSessionStrat, self).__init__()

    def execute(self, msg: dict) -> None:
        nickname = msg["nickname"]
        self._messageRoom_pointer.clients[nickname].close()
        self._messageRoom_pointer.clients.pop(nickname)

        for id_chat in self._messageRoom_pointer.nicknames_in_chats.keys():  # TODO: Слишком медленно
            if nickname in self._messageRoom_pointer.nicknames_in_chats[id_chat]:
                self._messageRoom_pointer.nicknames_in_chats[id_chat].remove(nickname)


class EndSession(MessageStrategy):
    command_name = "CHAT-MESSAGE"

    def __init__(self):
        super(EndSession, self).__init__()

    def execute(self, msg: dict) -> None:
        chat_code = str(msg["chat_id"])
        nickname = msg["nickname"]
        message = msg["message"]
        date_now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        message_to_send = {  # id 0, потом когда доабвляем в базу AI сам его назначит
            "id": 0,
            "chat": chat_code,
            "message": message,
            "sender": nickname,
            "created_at": date_now,
            "was_seen": False
        }

        self._messageRoom_pointer.cache_chat[chat_code].append(message_to_send)
        self._messageRoom_pointer.broadcast((chat_code, message, date_now, nickname, message_to_send["was_seen"]))


class RequestCacheStrategy(MessageStrategy):
    command_name = "CACHE-REQUEST"

    def __init__(self):
        super(RequestCacheStrategy, self).__init__()
        self._cache_limit = '20'  # Ограничение по единоразовой загрузке сообщений

    def execute(self, msg: dict[str, str]) -> None:
        chats_ids = msg["chats_ids"].split(',')
        if len(chats_ids) == 0:
            return

        for chat_id in chats_ids:
            if len(self._messageRoom_pointer.cache_chat[chat_id]) != 0:
                continue

            self._messageRoom_pointer.cache_chat[chat_id] = self._api_client.get_messages_limit(chat_id,
                                                                                                self._cache_limit).copy()
