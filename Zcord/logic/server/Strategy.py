from abc import abstractmethod, ABC

class Strategy(ABC):
    """Интерфейс стратегий, от него наследуются все стратегии"""
    @abstractmethod
    async def execute(self, msg: dict) -> None: #Логика обрабоки команды
        pass

