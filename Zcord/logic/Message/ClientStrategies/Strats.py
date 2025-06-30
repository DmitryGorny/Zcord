from abc import ABC, abstractmethod
from typing import Callable

from logic.Message.ClientStrategies.Strategy import Strategy

class ChooseStrategy:
    def __init__(self):
        self.__current_strategy = None

    def get_strategy(self, header: str, mconnection_obj, nickname_yours: str) -> Strategy:
        if self.__current_strategy is not None:
            if self.__current_strategy.command_name == header:
                return self.__current_strategy

        if header not in ClientsStrategies.headers.keys():
            return None

        self.__current_strategy = ClientsStrategies.headers[header]()
        self.__current_strategy.set_data(message_connection=mconnection_obj, nick=nickname_yours)
        return self.__current_strategy

class ClientsStrategies(Strategy):
    headers = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "header_name"):
            cls.headers[cls.header_name] = cls

    def __init__(self):
        self._message_connection_point = None
        self._nickname_yours: str = None

    def set_data(self, **kwargs):
        self._message_connection_point = kwargs.get("message_connection")
        self._nickname_yours = kwargs.get("nick")

    @abstractmethod
    def execute(self,  msg: dict) -> None:
        pass


class UserStatusRecieve(ClientsStrategies):
    header_name = "USER-STATUS"

    def __init__(self):
        super(UserStatusRecieve, self).__init__()

    def execute(self,  msg: dict) -> None:
        sender_status = msg["user-status"]
        sender_nickname = msg["nickname"]
        reciever_nickname = self._message_connection_point.user.getNickName()

        STATUS_COLORS = {
            "__USER-ONLINE__": "#008000",
            "__USER-DISTRUB-BLOCK__": "red",
            "__USER-HIDDEN__": "grey",
            "__USER-AFK__": "yellow"
        }

        color = STATUS_COLORS.get(sender_status)
        target = "self" if sender_nickname == reciever_nickname else "friend"
        args = ([target, color] + ([sender_nickname] if target == "friend" else []))
        print(args)
        self._message_connection_point.reciever.dynamicInterfaceUpdate.emit("CHANGE-ACTIVITY", (args))


class SendChatsData(ClientsStrategies):
    header_name = "__NICK__"
    
    def __init__(self):
        super(SendChatsData, self).__init__()

    def execute(self,  msg: dict) -> None:
        self._message_connection_point.send_service_message(self._message_connection_point.serialize(self._message_connection_point.cache_chat).decode('utf-8'), self._nickname_yours)


class SendFirstInfo(ClientsStrategies):
    header_name = "__USER-INFO__"

    def __init__(self):
        super(SendFirstInfo, self).__init__()

    def execute(self,  msg: dict) -> None:
        dictToSend = {
            "friends":  self._message_connection_point.user.getFriends(),
            "status": [self._message_connection_point.user.status.name,  self._message_connection_point.user.status.color]
        }
        self._message_connection_point.send_service_message( self._message_connection_point.serialize(dictToSend).decode('utf-8'), self._nickname_yours)

class ConnectToMessageServer(ClientsStrategies):
    header_name = "__CONNECT__"
    def __init__(self):
        super(ConnectToMessageServer, self).__init__()

    def execute(self,  msg: dict) -> None:
        self._message_connection_point.client_tcp.connect((self._message_connection_point.MS_IP,  self._message_connection_point.MS_PORT))
