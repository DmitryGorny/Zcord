from abc import abstractmethod, ABC

from logic.server.Service.domain.session_domain.services.SessionService import ISessionService


class IServiceStrat(ABC):

    @abstractmethod
    async def execute(self, msg: dict) -> None:
        pass


class ServiceStrategy(IServiceStrat):
    commands = {}

    def __init_subclass__(cls, **kwargs):  # Приколдес
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "command_name"):
            cls.commands[cls.command_name] = cls

    def __init__(self, service: ISessionService):
        self._service: ISessionService = service

    @abstractmethod
    async def execute(self, msg: dict) -> None:
        pass
