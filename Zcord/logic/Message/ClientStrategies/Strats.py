from abc import ABC, abstractmethod

from logic.Message.ClientStrategies.Strategy import Strategy


class ClientsStrategies(Strategy):
    headers = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "header_name"):
            cls.headers[cls.header_name] = cls

    def __init__(self):
        self._message_connection_point = None
        self._sender_func = None

    def set_data(self, **kwargs):
        self._message_connection_point = kwargs.get("message_connection")
        self._sender_func = kwargs.get("sender")

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
        self._message_connection_point.reciever.dynamicInterfaceUpdate.emit("CHANGE-ACTIVITY", (args))


 #Нужно теперь тестировать в message_client



