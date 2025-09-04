# Реализации стратегий для сервера сообщений (message-server)
import json
from datetime import datetime

from logic.db_handler.api_client import APIClient
from logic.server.MessageServer.Cache.Cache import CacheOverloadError
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

        cache = self._messageRoom_pointer.cache_chat.get_cache(chat_code)

        if len(cache) == 0:
            return

        self._messageRoom_pointer.send_cache(cache, nickname)


class UserInfoStrategy(MessageStrategy):
    """Юзер подключается, по нему приходит информаця с основного сервера"""
    command_name = "USER-INFO"

    def __init__(self):
        super(UserInfoStrategy, self).__init__()

    def execute(self, msg: dict) -> None:
        serialize_1 = json.loads(msg["serialize_1"])
        serialize_2 = msg["serialize_2"]

        self._messageRoom_pointer.copyCacheChat(serialize_1)
        for chat_id in serialize_1.keys():
            self._messageRoom_pointer.cache_chat.init_cache(chat_id)

        msg = json.loads(serialize_2)
        self._messageRoom_pointer.clients[list(msg.keys())[0]] = msg[list(msg.keys())[0]]


class EndSessionStrat(MessageStrategy):
    command_name = "END-SESSION"

    def __init__(self):
        super(EndSessionStrat, self).__init__()

    def execute(self, msg: dict) -> None: #TODO: Дублируется хуйня при добавлении в базу из добавочного кэша
        nickname = msg["nickname"]
        self._messageRoom_pointer.clients[nickname].close()
        self._messageRoom_pointer.clients.pop(nickname)

        for id_chat in self._messageRoom_pointer.nicknames_in_chats.keys():  # TODO: Слишком медленно
            if nickname in self._messageRoom_pointer.nicknames_in_chats[id_chat]:
                self._messageRoom_pointer.nicknames_in_chats[id_chat].remove(nickname)

            self._api_client.send_messages_bulk(self._messageRoom_pointer.cache_chat.get_cache(chat_id=id_chat, user_out=True))

class EndSession(MessageStrategy):
    command_name = "CHAT-MESSAGE"

    def __init__(self):
        super(EndSession, self).__init__()

    def execute(self, msg: dict) -> None:
        chat_code = str(msg["chat_id"])
        user_id = str(msg["user_id"])
        message = msg["message"]
        date_now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        message_to_send = {  # id 0, потом когда доабвляем в базу AI сам его назначит
            "id": '0',
            "chat": chat_code,
            "message": message,
            "sender": user_id,
            "created_at": date_now,
            "was_seen": False
        }

        result = self._messageRoom_pointer.cache_chat.add_value(chat_code, message_to_send)

        if result is not None:
            self._api_client.send_messages_bulk(result)
            self._messageRoom_pointer.cache_chat.add_value(chat_code, message_to_send)

        self._messageRoom_pointer.broadcast((chat_code, message, date_now, user_id, message_to_send["was_seen"]))


class RequestCacheStrategy(MessageStrategy):
    command_name = "CACHE-REQUEST"

    def __init__(self):
        super(RequestCacheStrategy, self).__init__()
        self._cache_limit = '15'  # Ограничение по единоразовой загрузке сообщений

    def execute(self, msg: dict[str, str]) -> None:
        chats_ids = msg["chats_ids"].split(',')
        if len(chats_ids) == 0:
            return

        for chat_id in chats_ids:
            if len(self._messageRoom_pointer.cache_chat.get_cache(chat_id)) != 0:
                continue

            self._messageRoom_pointer.cache_chat.add_cache(chat_id, self._api_client.get_messages_limit(chat_id,
                                                                                                        self._cache_limit).copy())
