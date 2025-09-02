from abc import abstractmethod

from logic.client.Strats.Strategy import Strategy


class ChooseStrategy:
    def __init__(self):
        self.__current_strategy = None

    def get_strategy(self, header: str, service_conn_obj, nickname_yours: str) -> Strategy:
        if self.__current_strategy is not None:
            if self.__current_strategy.header_name == header:
                return self.__current_strategy

        if header not in ClientsStrategies.headers.keys():
            return None

        self.__current_strategy = ClientsStrategies.headers[header]()
        self.__current_strategy.set_data(service_connection=service_conn_obj, nick=nickname_yours)
        return self.__current_strategy


class ClientsStrategies(Strategy):
    headers = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "header_name"):
            cls.headers[cls.header_name] = cls

    def __init__(self):
        self.service_connection_pointer = None
        self._nickname_yours: str = None

    def set_data(self, **kwargs):
        self.service_connection_pointer = kwargs.get("service_connection")
        self._nickname_yours = kwargs.get("nick")

    @abstractmethod
    def execute(self, msg: dict) -> None:
        pass


class UserStatusRecieve(ClientsStrategies):
    header_name = "USER-STATUS"

    def __init__(self):
        super(UserStatusRecieve, self).__init__()

    def execute(self, msg: dict) -> None:
        sender_status = msg["user-status"]
        sender_nickname = msg["nickname"]
        reciever_nickname = self.service_connection_pointer.user.getNickName()

        STATUS_COLORS = {
            "__USER-ONLINE__": "#008000",
            "__USER-DISTRUB-BLOCK__": "red",
            "__USER-HIDDEN__": "grey",
            "__USER-AFK__": "yellow"
        }

        color = STATUS_COLORS.get(sender_status)
        target = "self" if sender_nickname == reciever_nickname else "friend"
        args = ([target, color] + ([sender_nickname] if target == "friend" else []))
        self.service_connection_pointer.reciever.dynamicInterfaceUpdate.emit("CHANGE-ACTIVITY", (args))


class SendChatsData(ClientsStrategies):
    header_name = "__NICK__"

    def __init__(self):
        super(SendChatsData, self).__init__()

    def execute(self, msg: dict) -> None:
        self.service_connection_pointer.send_message(
            self.service_connection_pointer.serialize(self.service_connection_pointer._cache_chat).decode('utf-8'))


class SendFirstInfo(ClientsStrategies):
    header_name = "__USER-INFO__"

    def __init__(self):
        super(SendFirstInfo, self).__init__()

    def execute(self, msg: dict) -> None:
        dictToSend = {
            "friends": self.service_connection_pointer.user.getFriends(),
            "status": [self.service_connection_pointer.user.status.name,
                       self.service_connection_pointer.user.status.color],
            "id": self.service_connection_pointer.user.id,
            "last_online": self.service_connection_pointer.user.last_online
        }

        self.service_connection_pointer.send_message(
            self.service_connection_pointer.serialize(dictToSend).decode('utf-8'))


class ConnectToMessageServer(ClientsStrategies):
    header_name = "__CONNECT__"

    def __init__(self):
        super(ConnectToMessageServer, self).__init__()

    def execute(self, msg: dict) -> None:
        self.service_connection_pointer.connect_to_msg_server()  # TODO: Отловить ошибки подключения
        self.service_connection_pointer.send_message(message="CACHE-REQUEST")
