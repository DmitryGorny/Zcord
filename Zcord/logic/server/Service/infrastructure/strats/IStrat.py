from abc import abstractmethod, ABC
from typing import Protocol

from logic.server.Service.core.services.chat.IChatService import IChatService
from logic.server.Service.core.services.client.IClientService import IClientService
from logic.server.Service.core.services.friend.IFriendService import IFriendService


class IServiceStrat(ABC):

    @abstractmethod
    async def execute(self, msg: dict) -> None:
        raise NotImplementedError


class StratsGroupKeeper:
    groups = {}

    def __init_subclass__(cls, **kwargs):  # Приколдес
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "group_name"):
            cls.groups[cls.group_name] = cls


class ClientStrategyKeeper(StratsGroupKeeper):
    """Группа стратегий для работы с клиентом"""

    group_name = "CLIENT"
    commands = {}

    def __init_subclass__(cls, **kwargs):  # Приколдес
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "command_name"):
            cls.commands[cls.command_name] = cls

    def __init__(self):
        self._service: IClientService | None = None

    def set_service(self, service: IClientService):
        self._service = service


class FriendStrategyKeeper(StratsGroupKeeper):
    """Группа стратегий для работы с друзьями"""

    group_name = "FRIEND"
    commands = {}

    def __init_subclass__(cls, **kwargs):  # Приколдес
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "command_name"):
            cls.commands[cls.command_name] = cls

    def __init__(self):
        self._service: IFriendService | None = None

    def set_service(self, service: IClientService):
        self._service = service


class ChatStrategyKeeper(StratsGroupKeeper):
    """Группа стратегий для работы с чатами"""

    group_name = "CHAT"
    commands = {}

    def __init_subclass__(cls, **kwargs):  # Приколдес
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "command_name"):
            cls.commands[cls.command_name] = cls

    def __init__(self):
        self._service: IChatService | None = None

    def set_service(self, service: IClientService):
        self._service = service
