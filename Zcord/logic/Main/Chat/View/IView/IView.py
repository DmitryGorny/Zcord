from abc import ABC, abstractmethod, ABCMeta

from PyQt6 import QtWidgets


class QWidgetABCMeta(type(QtWidgets.QWidget), ABCMeta):
    pass


class IView(QtWidgets.QWidget, metaclass=QWidgetABCMeta):
    @abstractmethod
    def ask_for_cached_messages(self, val):
        pass

    @abstractmethod
    def enable_scroll(self):
        pass

    @abstractmethod
    def send_message(self):
        pass

    @abstractmethod
    def receive_message(self, sender, text, date, messageIndex=1, wasSeen: bool = False):  # Нужно еще 20 аргументов
        pass

    @abstractmethod
    def change_unseen_status(self, number_of_widgets):
        pass

    @abstractmethod
    def clear_unseen_messages(self):
        pass

    @abstractmethod
    def clear_chat_layout(self):
        pass

    @property
    @abstractmethod
    def chat_id(self) -> str:
        pass
