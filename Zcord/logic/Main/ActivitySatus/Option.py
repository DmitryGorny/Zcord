from abc import ABC, abstractmethod

class Option:
    def __init__(self):
        self.calls_allowed = False
        self.message_notifications_allowed = False
        self.calls_notifications_allowed = False
        self.auto_answer = False
        self.users_see_me = False

class OptionBuilder(ABC):
    @property
    @abstractmethod
    def option(self) -> Option:
        pass

    @abstractmethod
    def set_calls_allowed(self) -> None:
        pass

    @abstractmethod
    def set_chat_messages_notifications_allowed(self) -> None:
        pass

    @abstractmethod
    def set_calls_chatNotifications_allowed(self) -> None:
        pass

    @abstractmethod
    def set_auto_answer_on(self) -> None:
        pass

    @abstractmethod
    def set_users_see_me(self) -> None:
        pass

class OptionCreator(OptionBuilder):
    def __init__(self):
        self._option = Option()

    @property
    def option(self) -> Option:
        return self._option

    def set_calls_allowed(self) -> None:
        self._option.calls_allowed = True

    def set_chat_messages_notifications_allowed(self) -> None:
        self._option.message_notifications_allowed = True

    def set_calls_chatNotifications_allowed(self) -> None:
        self._option.calls_notifications_allowed = True

    def set_auto_answer_on(self) -> None:
        self._option.auto_answer = True

    def set_users_see_me(self) -> None:
        self._option.users_see_me = True

class OptionDirector:
    def __init__(self):
        self._option_builder = OptionCreator()

    @property
    def _builder(self) -> OptionBuilder:
        return self._option_builder

    def default_online_option(self) -> Option:
        self._builder.set_calls_allowed()
        self._builder.set_users_see_me()
        self._builder.set_calls_chatNotifications_allowed()
        self._builder.set_chat_messages_notifications_allowed()
        return self._builder.option

    def default_dontDistrub_option(self) -> Option:
        self._builder.set_users_see_me()
        return self._builder.option

    def default_hidden_option(self) -> Option:
        self._builder.set_calls_chatNotifications_allowed()
        self._builder.set_chat_messages_notifications_allowed()
        self._builder.set_calls_allowed()
        return self._builder.option

    def default_AFK_option(self) -> Option:
        self._builder.set_calls_allowed()
        self._builder.set_users_see_me()
        self._builder.set_calls_chatNotifications_allowed()
        self._builder.set_chat_messages_notifications_allowed()
        return self._builder.option
