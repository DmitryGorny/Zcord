from typing import List

from logic.Main.Chat.Controller.ChatController import ChatController
from logic.Main.Chat.View.IView.IView import BaseChatView
from logic.Main.Chat.View.dm_view.ChatClass.ChatView import ChatView

from logic.Main.Chat.View.group_view.Group.GroupView import GroupView
from logic.db_client.api_client import APIClient
from .fabric import CreateDMChat, CreateGroupChat, GroupMemberCreator


class UserChats:
    def __init__(self, user):
        self._dm_chats: List[ChatView] = []
        self._groups: List[GroupView] = []
        self._chats_controller: ChatController = ChatController()  # Класс контроллера
        self.__user = user
        self._db = APIClient()

        self._current_dm_chat: ChatView = None

    @property
    def current_chat(self) -> ChatView:
        return self._current_dm_chat

    @current_chat.setter
    def current_chat(self, chat_id: str) -> None:
        try:
            chat = next(filter(lambda x: x.chat_id == chat_id, self._dm_chats))
        except StopIteration:
            return
        self._current_dm_chat = chat

    def init_dm_chats(self) -> None:
        fabric = CreateDMChat()

        chat_db = self._db.get_chats(user_id=self.__user.id, is_group=False)
        for chat_attrs in chat_db:
            user1 = chat_attrs['DM']['user1']
            user2 = chat_attrs['DM']['user2']
            friend_id = user2 if str(user1) == str(self.__user.id) else user1
            chat = fabric.create_chat(is_dm=True,
                                      chat_id=str(chat_attrs["id"]),
                                      friend_id=str(friend_id),
                                      user_obj=self.__user,
                                      controller=self._chats_controller)
            self._dm_chats.append(chat)
            self._chats_controller.add_view(str(chat_attrs['id']), chat)

    def group_request_sent(self, group_id: str) -> None:
        group = self._db.search_chat_by_id(int(group_id), True)[0]
        try:
            group = next(filter(lambda x: x.chat_id == group['id'], self._groups))
        except StopIteration as e:
            print('[UserChats] {}'.format(e))
            return None

        group.close_invite_dialog()

    def init_groups(self):
        fabric = CreateGroupChat()
        member_fabric = GroupMemberCreator()
        groups = self._db.get_chats(user_id=self.__user.id, is_group=True)
        for group in groups:  # TODO: Оптимизация
            members = []
            for user in group['group']['users']:
                members.append(member_fabric.create_member(nickname=user['nickname'], user_id=str(user['user_id'])))

            group_name = group['group']['group_name']
            group_obj = fabric.create_chat(is_dm=False,
                                           group_id=group['id'],
                                           group_name=group_name,
                                           user_obj=self.__user,
                                           controller=self._chats_controller,
                                           members=members,
                                           is_private=group['group']['is_private'],
                                           is_password=group['group']['is_password'],
                                           is_admin_invite=group['group']['is_invite_from_admin'],
                                           admin_id=group['group']['user_admin'])
            group_obj.group_member_online(str(self.__user.id))
            self._groups.append(group_obj)
            self._chats_controller.add_view(str(group['id']), group_obj)

    def add_dm_chat(self, chat_id: str, friend_id: str):
        fabric = CreateDMChat()

        chat = fabric.create_chat(is_dm=True,
                                  chat_id=str(chat_id),
                                  friend_id=str(friend_id),
                                  user_obj=self.__user,
                                  controller=self._chats_controller)
        self._dm_chats.append(chat)
        self._chats_controller.add_view(chat_id, chat)
        return chat

    def add_group_chat(self, chat_id: str, group_name: str, is_private: bool, is_password: bool, is_admin_invite: bool,
                       admin_id: str):
        fabric = CreateGroupChat()
        members = []
        member_fabric = GroupMemberCreator()
        groups = self._db.get_chat_by_id(chat_id=chat_id)
        for user in groups['group']['users']:
            members.append(member_fabric.create_member(nickname=user['nickname'], user_id=str(user['user_id'])))

        group = fabric.create_chat(is_dm=False,
                                   group_id=str(chat_id),
                                   group_name=group_name,
                                   user_obj=self.__user,
                                   controller=self._chats_controller,
                                   members=members,
                                   is_private=is_private,
                                   is_admin_invite=is_admin_invite,
                                   is_password=is_password,
                                   admin_id=admin_id)
        group.group_member_online(str(self.__user.id))
        self._groups.append(group)
        self._chats_controller.add_view(chat_id, group)
        return group

    def get_socket_controller(self) -> ChatController.SocketController:
        return self._chats_controller.get_socket_controller()

    def chats_props(self) -> dict:
        """Поочередно возвращает атрибуты каждого класса"""
        for chat in self._dm_chats:
            yield {"chat_id": chat.chat_id, "nickname": chat.getNickName(), 'friends_id': [chat.friend_id],
                   "chat_ui": chat.ui.MAIN, 'is_dm': True}

        for group in self._groups:
            yield {"chat_id": str(group.chat_id), "group_name": group.group_name, 'friends_id': group.get_users,
                   "group_ui": group.ui.MAIN, 'is_dm': False}

    def chats_props_without_ui(self) -> dict:
        """Поочередно возвращает атрибуты каждого класса"""
        for chat in self._dm_chats:
            yield {"chat_id": chat.chat_id, "nickname": chat.getNickName(),
                   'friends_id': [chat.friend_id, self.__user.id],
                   'is_dm': True}

        for group in self._groups:
            yield {"chat_id": str(group.chat_id), "group_name": group.group_name,
                   'friends_id': [str(member) for member in group.get_users],
                   'is_dm': False}

    def get_dm_chats(self) -> List[ChatView]:
        return self._dm_chats.copy()

    def get_groups_props(self) -> dict:
        for group in self._groups:
            yield {'chat_id': group.chat_id, 'group_name': group.group_name, 'users': group.get_users}

    def delete_dm_chat(self, chat_id: str) -> None:
        chat = list(filter(lambda x: str(x.chat_id) == str(chat_id), self._dm_chats))[0]
        self._dm_chats.remove(chat)
        self._chats_controller.delete_chat(chat_id)

    def get_group_by_id(self, group_id: str) -> dict | None:
        try:
            group = next(filter(lambda x: x.chat_id == group_id, self._groups))
            return {'chat_id': group.chat_id, 'group_name': group.group_name, 'users': group.get_users,
                    'ui': group.ui.MAIN}
        except StopIteration as e:
            print(e)
            return None

    def add_member_to_group(self, member_id: str, group_id: str) -> None:
        user = self._db.get_user_by_id(user_id=int(member_id))
        member_fabric = GroupMemberCreator()
        member = member_fabric.create_member(nickname=user['nickname'], user_id=str(user['id']))
        try:
            group = next(filter(lambda x: str(x.chat_id) == group_id, self._groups))
            group.add_member_to_group(member)
            group.show_number_of_members()
        except StopIteration as e:
            print('[UserChats] {}'.format(e))
            return None

    def chat_member_offline(self, user_id: str, chat_id: str):
        try:
            group = next(filter(lambda g: str(g.chat_id) == str(chat_id), self._groups))
        except StopIteration as e:
            print('[UserChats] {}'.format(e))
            return
        group.group_member_offline(user_id)

    def chat_member_online(self, member_id: str, chat_id: str) -> None:
        try:
            group = next(filter(lambda g: str(g.chat_id) == str(chat_id), self._groups))
        except StopIteration as e:
            print('[UserChats] {}'.format(e))
            return
        group.group_member_online(member_id)
