from abc import abstractmethod
from datetime import datetime

from logic.client.Strats.Strategy import Strategy


class ChooseStrategy:
    def __init__(self):
        self.__current_strategy = None

    def get_strategy(self, header: str, message_conn_obj) -> Strategy:
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
        for message in msg["cache"]:
            print(message)
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
                message["was_seen"]) #пофиксить и переделать change_chat
