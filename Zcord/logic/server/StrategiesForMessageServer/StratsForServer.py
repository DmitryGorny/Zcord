# Реализации стратегий для сервера сообщений (message-server)
import json
from datetime import datetime

from logic.db_handler.api_client import APIClient
from logic.server.MessageServer.Cache.Cache import CacheOverloadError
from logic.server.Strategy import Strategy
from abc import abstractmethod, ABC
from typing import Callable, List, Dict, Union
from logic.server.StrategyForServiceServer.ServeiceStrats import ServiceStrategy

CACHE_LIMIT = '15'


class ChooseStrategy:
    def __init__(self):
        self.__current_strategy = None

    def get_strategy(self, command: str, Server) -> Strategy | None:
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

    @abstractmethod
    def execute(self, msg: dict) -> None:
        pass


class ChangeChatStrategy(MessageStrategy):
    command_name = "__change_chat__"

    def __init__(self):
        super(ChangeChatStrategy, self).__init__()

    def execute(self, msg: dict) -> None:
        user_id = str(msg["user_id"])
        current_chat_id = str(msg["current_chat_id"])
        chat_code = str(msg["chat_code"])

        try:
            self._messageRoom_pointer.ids_in_chats[current_chat_id].remove(user_id)
        except ValueError as e:
            print(e)
        except KeyError:
            print("Клик по тому же чату")
        self._messageRoom_pointer.ids_in_chats[chat_code].append(user_id)

        cache = self._messageRoom_pointer.cache_chat.get_cache(chat_code)

        if len(cache["cache"]) == 0:
            return

        ids = []
        count = 0
        for x in cache["cache"]:
            if x["was_seen"]:
                continue

            if x["sender"] == user_id:
                continue

            count += 1
            if x["id"] != "0":
                ids.append({"id": x["id"]})

        self._api_client.update_messages_bulk(ids)

        for user_id in self._messageRoom_pointer.ids_in_chats[chat_code]:
            self._messageRoom_pointer.send_info_message(user_id, "USER-JOINED-CHAT",
                                                        data={"messages_number": count,
                                                              "chat_id": chat_code})

        self._messageRoom_pointer.cache_chat.mark_as_seen(chat_code, user_id, cache["index"])

        self._messageRoom_pointer.send_cache(cache["cache"], user_id, index=cache["index"])


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

        user_id = str(msg["user_id"])
        IP = msg["IP"]

        self._messageRoom_pointer.clients.add_client(client_id=user_id, ip=IP)


class EndSessionStrat(MessageStrategy):
    command_name = "END-SESSION"

    def __init__(self):
        super(EndSessionStrat, self).__init__()

    def execute(self, msg: dict) -> None:
        user_id = str(msg["user_id"])
        self._messageRoom_pointer.clients.remove_client(client_identent=user_id)

        for id_chat in self._messageRoom_pointer.ids_in_chats.keys():  # TODO: Слишком медленно
            if user_id in self._messageRoom_pointer.ids_in_chats[id_chat]:
                self._messageRoom_pointer.ids_in_chats[id_chat].remove(user_id)
                if len(self._messageRoom_pointer.ids_in_chats[id_chat]) == 0:
                    self._api_client.send_messages_bulk(
                        self._messageRoom_pointer.cache_chat.get_cache(chat_id=id_chat, user_out=True)["cache"])
                    self._messageRoom_pointer.cache_chat.clear_cache(chat_id=id_chat)


class EndSession(
    MessageStrategy):  # TODO: Для групп ввести метку is_group = msg["is_group"], придумать что-то для was_seen
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
            self._messageRoom_pointer.send_info_message(user_id, "CACHE-SENT-TO-DB")

        if len(self._messageRoom_pointer.ids_in_chats[chat_code]) > 1:
            message_to_send["was_seen"] = True

        self._messageRoom_pointer.broadcast((chat_code, message, date_now, user_id, message_to_send["was_seen"]))


class RequestCacheStrategy(MessageStrategy):
    command_name = "CACHE-REQUEST"

    def __init__(self):
        super(RequestCacheStrategy, self).__init__()

    def execute(self, msg: dict[str, str]) -> None:
        chats_ids = msg["chats_ids"].split(',')
        if len(chats_ids) == 0:
            return

        for chat_id in chats_ids:
            if len(self._messageRoom_pointer.cache_chat.get_cache(chat_id)["cache"]) > 0:
                continue

            cache = self._api_client.get_messages_limit(chat_id, CACHE_LIMIT).copy()
            self._messageRoom_pointer.cache_chat.add_cache(chat_id, cache)


class ScrollRequestCacheStrategy(MessageStrategy):
    command_name = "SCROLL-CACHE-REQUEST"

    def __init__(self):
        super(ScrollRequestCacheStrategy, self).__init__()

    def execute(self, msg: dict[str, str]) -> None:
        chat_id = str(msg["chat_id"])
        user_id = str(msg["user_id"])
        index = msg["index"]
        db_index = msg["db_index"]

        if index == - 1:
            return

        cache = self._messageRoom_pointer.cache_chat.get_cache_by_scroll(chat_id, index)

        if cache is not None and len(cache["cache"]) > 0:

            ids = []
            count = 0
            for x in cache["cache"]:
                if x["was_seen"]:
                    continue

                if x["sender"] == user_id:
                    continue

                count += 1
                if x["id"] != "0":
                    ids.append({"id": x["id"]})

            self._messageRoom_pointer.cache_chat.mark_as_seen(chat_id, user_id, int(index))

            self._messageRoom_pointer.send_cache(cache_list=cache["cache"],
                                                 client_identent=user_id,
                                                 scroll_cache=True,
                                                 index=cache["index"])

            for user_id in self._messageRoom_pointer.ids_in_chats[chat_id]:
                self._messageRoom_pointer.send_info_message(user_id, "USER-JOINED-CHAT",
                                                            data={"messages_number": count,
                                                                  "chat_id": chat_id})

            return

        # Ниже логика запроса кеша и отслыки клиенту кэша из БД
        cache = self._api_client.get_messages_limit_offset(chat_id, CACHE_LIMIT, db_index)

        if cache is None:
            return
        self._messageRoom_pointer.send_cache(cache[::-1], user_id, scroll_cache=True)

        if len(self._messageRoom_pointer.ids_in_chats[chat_id]) <= 1:
            return

        ids = [{"id": x["id"]} for x in cache if x["was_seen"] == False if str(x["sender"]) != user_id]

        self._api_client.update_messages_bulk(ids)
        count = len(ids)
        for user_id in self._messageRoom_pointer.ids_in_chats[chat_id]:
            self._messageRoom_pointer.send_info_message(user_id, "USER-JOINED-CHAT",
                                                        data={"messages_number": count,
                                                              "chat_id": chat_id})
