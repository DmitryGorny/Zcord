import asyncio
import datetime
import json
from typing import List, Dict, Type

from logic.server.Service.core.enteties.Enteties import IClient, IFriend, IChatMember, IChat


class Client(IClient):
    def __init__(self, user_id: str, nick, last_online: str = None, writer: asyncio.StreamWriter = None):
        self._id = user_id
        self._nick = nick
        self._writer = writer
        self._activityStatus = None

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
    def writer(self) -> asyncio.StreamWriter:
        return self._writer

    @property
    def id(self) -> str:
        return self._id

    @property
    def nick(self):
        return self._nick

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


class Friend(IFriend, Client):
    def __init__(self, user_id: str, nick, friendship_status: str, last_online: str):
        super(Friend, self).__init__(user_id, nick, last_online)
        self._friendship_status: str = friendship_status

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


class ChatMember(IChatMember):
    """Класс под пользователя, не являющегося другом"""

    def __init__(self, user_id: str, username: str):
        self._id = user_id
        self._username = username

    @property
    def user_id(self) -> str:
        return self._id

    @property
    def username(self) -> str:
        return self._username


class Chat(IChat):
    def __init__(self, chat_id: str):
        self._chat_id = chat_id

        self._members: List[IChatMember] = []
        self._current_voice_members: List[IChatMember] = []

    @property
    def chat_id(self) -> str:
        return self._chat_id

    def add_member(self, friend: IChatMember) -> None:
        self._members.append(friend)

    def get_members_len(self) -> int:
        return len(self._members)

    def create_and_add_member(self, user_id: str, nickname: str):
        member = ChatMember(user_id, nickname)
        self._members.append(member)

    def get_member_by_id(self, user_id) -> IChatMember | None:
        try:
            return next(filter(lambda x: str(x.user_id) == str(user_id), self._members))
        except StopIteration as e:
            print(e)
            return None

    def get_members(self) -> list[IChatMember]:
        return self._members.copy()

    def delete_member_by_id(self, user_id: str) -> None:
        try:
            member = next(filter(lambda x: x.user_id == user_id, self._members))
        except StopIteration as e:
            print(e)
            return

        self._members.remove(member)

    # Работа с войс румой
    def add_voice_member(self, friend: ChatMember) -> None:
        self._current_voice_members.append(friend)

    def delete_voice_member_by_id(self, user_id: str) -> None:
        for friend in self._current_voice_members:
            if friend.user_id == user_id:
                self._current_voice_members.remove(friend)
                return

    def get_voice_members(self) -> List[ChatMember]:
        return self._current_voice_members.copy()
