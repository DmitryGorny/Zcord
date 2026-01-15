from abc import ABC, abstractmethod

from logic.Authorization.User.chat.GroupMember import GroupMember
from logic.Main.Chat.View.IView.IView import BaseChatView
from logic.Main.Chat.View.dm_view.ChatClass.ChatView import ChatView

from logic.Main.Chat.View.group_view.Group.GroupView import GroupView


class ChatFabric(ABC):
    @abstractmethod
    def create_chat(self, **kwargs) -> BaseChatView:
        pass


class CreateDMChat(ChatFabric):
    def create_chat(self, **kwargs) -> ChatView:
        return ChatView(kwargs["chat_id"], kwargs["friend_id"], kwargs["user_obj"], kwargs['controller'], kwargs['is_group'])


class CreateGroupChat(ChatFabric):
    def create_chat(self, **kwargs) -> GroupView:
        return GroupView(kwargs["group_id"],
                         kwargs["group_name"],
                         kwargs["user_obj"],
                         kwargs['controller'],
                         kwargs['members'],
                         kwargs['is_private'],
                         kwargs['is_password'],
                         kwargs['is_admin_invite'],
                         kwargs['admin_id'],
                         kwargs['date_of_creation'],
                         kwargs['is_group'])


class GroupMemberFabric(ABC):
    @abstractmethod
    def create_member(self, **kwargs) -> BaseChatView:
        pass


class GroupMemberCreator(GroupMemberFabric):
    def create_member(self, **kwargs) -> GroupMember:
        return GroupMember(kwargs['user_id'], kwargs['nickname'], kwargs['is_admin'])
