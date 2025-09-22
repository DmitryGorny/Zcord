import threading
import time
from abc import abstractmethod
from datetime import datetime

from logic.client.Strats.Strategy import Strategy

CACHE_LIMIT = 15


class ChooseStrategy:
    def __init__(self):
        self.__current_strategy = None

    def get_strategy(self, header: str, message_conn_obj) -> Strategy | None:
        if self.__current_strategy is not None:
            if self.__current_strategy.header_name == header:
                return self.__current_strategy

        if header not in ClientsStrategies.headers.keys():
            return None

        self.__current_strategy = ClientsStrategies.headers[header]()
        self.__current_strategy.set_data(message_connection=message_conn_obj)
        return self.__current_strategy


class ClientsStrategies(Strategy):
    headers = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "header_name"):
            cls.headers[cls.header_name] = cls

    def __init__(self):
        self._message_connection_pointer = None

    def set_data(self, **kwargs):
        self._message_connection_pointer = kwargs.get("message_connection")

    @abstractmethod
    def execute(self, msg: dict) -> None:
        pass


class ReceiveChatMessageStrat(ClientsStrategies):
    header_name = "CHAT-MESSAGE"

    def __init__(self):
        super(ReceiveChatMessageStrat, self).__init__()

    def execute(self, msg: dict) -> None:
        dt = datetime.strptime(msg["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
        date_now = dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        friends = self._message_connection_pointer.user.getFriends()

        if self._message_connection_pointer.chat is None:
            raise ValueError("chat = None, не прошла инициализация")

        try:
            nickname = next((fr["nickname"] for fr in friends if fr["id"] == str(msg["sender"])))
        except StopIteration:
            nickname = self._message_connection_pointer.user.getNickName()

        self._message_connection_pointer.chat.socket_controller.recieve_message(
            str(self._message_connection_pointer.chat.chat_id),
            nickname,
            msg["message"],
            date_now,
            1,
            msg["was_seen"])


class ReceiveCacheStrat(ClientsStrategies):
    header_name = "RECEIVE-CACHE"

    def __init__(self):
        super(ReceiveCacheStrat, self).__init__()

    def execute(self, msg: dict) -> None:
        friends = self._message_connection_pointer.user.getFriends()
        try:
            index = msg["index"]
            self._message_connection_pointer.chat.scroll_index = index
        except KeyError:
            self._message_connection_pointer.chat.scroll_index = 0

        scroll_db_counter = 0
        for message in msg["cache"]:
            try:
                nickname = next((fr["nickname"] for fr in friends if fr["id"] == str(message["sender"])))
            except StopIteration:
                nickname = self._message_connection_pointer.user.getNickName()

            message["sender"] = nickname

            dt = datetime.strptime(message["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
            date_now = dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

            if self._message_connection_pointer.chat is None:
                raise ValueError("chat = None, не прошла инициализация")

            self._message_connection_pointer.chat.socket_controller.recieve_message(
                str(self._message_connection_pointer.chat.chat_id),
                message["sender"],
                message["message"], date_now, 1,
                message["was_seen"])  # пофиксить и переделать change_chat

            if message["id"] != "0":
                scroll_db_counter += 1

        if scroll_db_counter > 0:
            self._message_connection_pointer.chat.scroll_db_index = scroll_db_counter


class ReceiveScrollCache(ClientsStrategies):
    header_name = "RECEIVE-CACHE-SCROLL"

    def __init__(self):
        super(ReceiveScrollCache, self).__init__()

    def execute(self, msg: dict) -> None:
        flg = True
        message_from_db = False
        friends = self._message_connection_pointer.user.getFriends()
        try:
            index = msg["index"]
            self._message_connection_pointer.chat.scroll_index = index
        except KeyError:
            message_from_db = True
            if len(msg["cache"]) >= CACHE_LIMIT:
                self._message_connection_pointer.chat.scroll_db_index = len(msg["cache"])
            else:
                self._message_connection_pointer.chat.socket_controller.stop_requesting_cache()
                flg = False

        counter_for_db_scroll_index = 0
        for message in msg["cache"]:
            try:
                nickname = next((fr["nickname"] for fr in friends if fr["id"] == str(message["sender"])))
            except StopIteration:
                nickname = self._message_connection_pointer.user.getNickName()

            message["sender"] = nickname

            dt = datetime.strptime(message["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
            date_now = dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

            if self._message_connection_pointer.chat is None:
                raise ValueError("chat = None, не прошла инициализация")

            event = threading.Event()
            self._message_connection_pointer.chat.socket_controller.awaited_receive_message(
                # TODO: Нужна ли awaited версия?
                str(self._message_connection_pointer.chat.chat_id),
                message["sender"],
                message["message"],
                date_now,
                0,
                message["was_seen"],
                event)

            if message["id"] != "0":
                counter_for_db_scroll_index += 1

        if not message_from_db:
            self._message_connection_pointer.chat.scroll_db_index = counter_for_db_scroll_index

        if flg:
            self._message_connection_pointer.chat.socket_controller.enable_scroll_bar(
                chat_id=str(self._message_connection_pointer.chat.chat_id))


class CacheSentToDBStrat(ClientsStrategies):
    header_name = "CACHE-SENT-TO-DB"

    def __init__(self):
        super(CacheSentToDBStrat, self).__init__()

    def execute(self, msg: dict) -> None:
        self._message_connection_pointer.chat.scroll_index = 0
        self._message_connection_pointer.chat.scroll_db_index = 0


class UserJoinedStrat(ClientsStrategies):
    header_name = "USER-JOINED-CHAT"

    def __init__(self):
        super(UserJoinedStrat, self).__init__()

    def execute(self, msg: dict) -> None:
        self._message_connection_pointer.chat.socket_controller.change_unseen_status(
            msg["chat_id"],
            int(msg["messages_number"]))


class UnseenCounterStrat(ClientsStrategies):
    header_name = "UNSEEN-COUNTER"

    def __init__(self):
        super(UnseenCounterStrat, self).__init__()

    def execute(self, msg: dict) -> None:
        chat_id = str(msg['chat_id'])
        message_number = int(msg["message_number"])
        self._message_connection_pointer.call_main_dynamic_update('UPDATE-MESSAGE-NUMBER', (chat_id, message_number))
