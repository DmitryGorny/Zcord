from abc import ABC, abstractmethod

from logic.Main.Chat.View.ChatClass.ChatView import ChatView


class ChatFabric(ABC):
    @abstractmethod
    def create_chat(self, is_dm: bool, **kwargs) -> ChatView:
        pass


class CreateChat(ChatFabric):
    def create_chat(self, is_dm: bool, **kwargs) -> ChatView:
        if is_dm:
            return ChatView(kwargs["chat_id"], kwargs["friend_nick"], kwargs["friend_id"], kwargs["user_obj"], kwargs['controller'])
