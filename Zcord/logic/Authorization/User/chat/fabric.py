from abc import ABC, abstractmethod

from logic.Main.Chat.View.IView.IView import BaseChatView
from logic.Main.Chat.View.dm_view.ChatClass.ChatView import ChatView

from logic.Main.Chat.View.group_view.Group.GroupView import GroupView


class ChatFabric(ABC):
    @abstractmethod
    def create_chat(self, is_dm: bool, **kwargs) -> BaseChatView:
        pass


class CreateChat(ChatFabric):
    def create_chat(self, is_dm: bool, **kwargs) -> BaseChatView:
        if is_dm:
            print(kwargs['chat_id'])
            return ChatView(kwargs["chat_id"], kwargs["friend_id"], kwargs["user_obj"], kwargs['controller'])
        else:
            return GroupView(kwargs["group_id"], kwargs["group_name"], kwargs["user_obj"], kwargs['controller'], kwargs['members'])
