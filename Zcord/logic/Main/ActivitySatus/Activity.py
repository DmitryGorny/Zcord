from abc import ABC, abstractmethod
from .Option import Option, OptionDirector


# Родитель статусов
class Status:
    def __init__(self):
        self.color = None
        self.name = None
        self.option = None

    def add_color(self, color) -> None:
        self.color = color

    def set_name(self, name) -> None:
        self.name = name

    def set_option(self, option: Option):
        self.option = option


# Классы под все статусы
class Online(Status):
    def __init__(self):
        super(Online, self).__init__()


class Hidden(Status):
    def __init__(self):
        super(Hidden, self).__init__()


class DisturbBlock(Status):
    def __init__(self):
        super(DisturbBlock, self).__init__()


class AFK(Status):
    def __init__(self):
        super(AFK, self).__init__()


class Custom(Status):
    def __init__(self):
        super(Custom, self).__init__()


# Классы под все статусы

class Builder(ABC):
    @abstractmethod
    def add_color(self, color) -> None:
        pass

    @abstractmethod
    def set_name(self, name) -> None:
        pass

    @abstractmethod
    def set_options(self, option: Option) -> None:
        pass


class CreateStatus(Builder):
    def __init__(self):
        self._status = Status()

    @property
    def status(self) -> Status:
        status = self._status
        self._status = Status()
        return status

    @status.setter
    def status(self, status: Status):
        self._status = status

    def add_color(self, color) -> None:
        self._status.add_color(color)

    def set_name(self, name) -> None:
        self._status.set_name(name)

    def set_options(self, option: Option) -> None:
        self._status.set_option(option)


class Director:
    def __init__(self):
        self._builder = None
        self._option_director = OptionDirector()

    @property
    def builder(self) -> Builder:
        return self._builder

    @builder.setter
    def builder(self, builder: Builder) -> None:
        self._builder = builder

    def build_online_status(self):
        self._builder.add_color("green")
        self._builder.set_name("В сети")
        self._builder.set_options(self._option_director.default_online_option())

    def build_dont_distrub_status(self):
        self._builder.add_color("red")
        self._builder.set_name("Не беспокоить")
        self._builder.set_options(self._option_director.default_dontDistrub_option())

    def build_hidden_status(self):
        self._builder.add_color("grey")
        self._builder.set_name("Невидимка")
        self._builder.set_options(self._option_director.default_hidden_option())

    def build_AFK_status(self):
        self._builder.add_color("yellow")
        self._builder.set_name("Не активен")
        self._builder.set_options(self._option_director.default_AFK_option())
