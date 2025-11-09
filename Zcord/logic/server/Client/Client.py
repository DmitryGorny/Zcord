import asyncio
import datetime
import json
from typing import List, Dict, Type


class Client:
    def __init__(self, user_id: str, nick, last_online: str = None, writer: asyncio.StreamWriter = None):
        self._id = user_id
        self._nick = nick
        self._writer = writer
        self._activityStatus = None
        self.__friends: Dict[str, Friend] = {}
        self._chats: Dict[str, Chat] = {}

        if last_online is not None:
            self._last_online = datetime.datetime.strptime(last_online, "%Y-%m-%dT%H:%M:%S.%f")

        self.__message_chat_id = 0  # id чата, в котором сейчас пользователь (аналог old_chat_code из message_server)

    @property
    def message_chat_id(self) -> int:
        return self.__message_chat_id

    @property
    def last_online(self) -> datetime.datetime:
        return self._last_online

    @message_chat_id.setter
    def message_chat_id(self, val: int) -> None:
        self.__message_chat_id = val

    @property
    def friends(self) -> dict:
        return self.__friends

    @friends.setter
    def friends(self, friends: List[Dict[str, str]]) -> None:  # TODO: Подумать над хранением группы
        for friend_attrs in friends:
            fr = Friend(friend_attrs['id'],  # TODO: Подумать над фабрикой
                        friend_attrs['nickname'],
                        str(friend_attrs['status']),
                        friend_attrs["last_online"])

            self.__friends[friend_attrs['id']] = fr  # тут зачем-то был статус дружбы в ключе

    @property
    def writer(self) -> asyncio.StreamWriter:
        return self._writer

    @property
    def id(self) -> str:
        return self._id

    @property
    def nick(self):
        return self._nick

    def add_friend(self, friend_name: str, friend_id: str, status: str = '2') -> None:
        from datetime import datetime
        now = datetime.now()
        time_str = now.strftime("%Y-%m-%dT%H:%M:%S.%f")
        self.__friends[friend_id] = Friend(user_id=friend_id,
                                           nick=friend_name,
                                           friendship_status=status,
                                           last_online=time_str)

    def add_chat(self, chat_id: str, friends_id: list[int]) -> None:
        chat = Chat(chat_id)
        for friend_id in friends_id:
            if str(friend_id) not in self.__friends.keys():
                chat.add_member(GroupMember(str(friend_id)))
                continue
            chat.add_member(self.__friends[str(friend_id)])

        self._chats[chat_id] = chat

    def delete_chat(self, chat_id: str) -> None:
        del self._chats[chat_id]

    def get_chat_by_user_id(self, user_id: str):
        for chat in self._chats.values():
            if chat.get_member_by_id(user_id) is not None:
                return chat

    def delete_chat_by_user_id(self, user_id: str) -> None:
        for chat_id in self._chats.keys():
            if self._chats[chat_id].get_member_by_id(user_id) is not None:
                del self._chats[chat_id]
                return

    def get_chat_by_id(self, chat_id: str):
        return self._chats[chat_id]

    @property
    def chats(self):
        return self._chats

    def delete_friend(self, user_id: str) -> None:
        del self.__friends[user_id]

    @property
    def status(self):
        return self._activityStatus

    @status.setter
    def status(self, status):
        self._activityStatus = status

    async def send_message(self, mes_type: str, mes_data: dict = None) -> None:
        message_header = {
            "message_type": mes_type,
        }

        if mes_data is not None:
            message = message_header | mes_data
        else:
            message = message_header

        self._writer.write(json.dumps(message).encode('utf-8'))
        await self._writer.drain()


class Friend(Client):
    def __init__(self, user_id: str, nick, friendship_status: str, last_online: str):
        super(Friend, self).__init__(user_id, nick, last_online)
        self._friendship_status = friendship_status

    @property
    def writer(self) -> asyncio.StreamWriter:
        return self._writer

    @writer.setter
    def writer(self, writer: asyncio.StreamWriter):
        self._writer = writer

    @property
    def friendship_status(self) -> str:
        return self._friendship_status

    @friendship_status.setter
    def friendship_status(self, val: str) -> None:
        self._friendship_status = val


class GroupMember(Client):
    """Класс под пользователя, не являющегося другом"""
    def __init__(self, user_id: str, nick: str = 'Undefined', last_online=''):
        super(GroupMember, self).__init__(user_id, nick)


class Chat:  # TODO: Проверить добавляются ли Friend в группу
    def __init__(self, chat_id: str):
        self._chat_id = chat_id

        self._members: List[Client] = []
        self._current_voice_members: List[Client] = []

    @property
    def chat_id(self) -> str:
        return self._chat_id

    def add_member(self, friend: Client) -> None:
        self._members.append(friend)

    def create_and_add_member(self, user_id: str):
        member = GroupMember(user_id)
        self._members.append(member)

    def get_member_by_id(self, user_id) -> Client | None:
        try:

            return next(filter(lambda x: str(x.id) == str(user_id), self._members))
        except StopIteration as e:
            print(e)
            return None

    def get_members(self) -> list[Client]:
        return self._members.copy()

    # Работа с войс румой
    def add_voice_member(self, friend: Client) -> None:
        self._current_voice_members.append(friend)

    def delete_voice_member_by_id(self, user_id: str) -> None:
        for friend in self._current_voice_members:
            if friend.id == user_id:
                self._current_voice_members.remove(friend)
                return

    def get_voice_members(self) -> List[Client]:
        return self._current_voice_members.copy()
