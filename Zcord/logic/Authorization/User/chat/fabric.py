from abc import ABC, abstractmethod

from logic.Main.Chat.ChatClass.Chat import Chat


class ChatFabric(ABC):
    @abstractmethod
    def create_chat(self, is_dm: bool, **kwargs) -> Chat:
        pass


class CreateChat(ChatFabric):
    def create_chat(self, is_dm: bool, **kwargs) -> Chat:
        if is_dm:
            return Chat(kwargs["chat_id"], kwargs["friend_nick"], kwargs["user_obj"])
