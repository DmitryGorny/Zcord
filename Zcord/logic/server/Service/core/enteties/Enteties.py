import asyncio
from datetime import datetime
from typing import Protocol, Dict, List


class IClient(Protocol):
    _id: str
    _nick: str
    _writer: asyncio.StreamWriter
    _activityStatus: list
    __friends: Dict[str, "IFriend"]
    _chats: Dict[str, "IChat"]
    __message_chat_id: int

    @property
    def message_chat_id(self) -> int:
        raise NotImplementedError

    @property
    def last_online(self) -> datetime:
        raise NotImplementedError

    @message_chat_id.setter
    def message_chat_id(self, val: int) -> None:
        raise NotImplementedError

    @property
    def writer(self) -> asyncio.StreamWriter:
        raise NotImplementedError

    @property
    def id(self) -> str:
        raise NotImplementedError

    @property
    def nick(self):
        raise NotImplementedError

    @property
    def status(self):
        raise NotImplementedError

    @status.setter
    def status(self, status):
        raise NotImplementedError

    async def send_message(self, mes_type: str, mes_data: dict = None) -> None:
        raise NotImplementedError


class IFriend(IClient, Protocol):
    _friendship_status: str

    @property
    def writer(self) -> asyncio.StreamWriter:
        raise NotImplementedError

    @writer.setter
    def writer(self, writer: asyncio.StreamWriter):
        raise NotImplementedError

    @property
    def friendship_status(self) -> str:
        raise NotImplementedError

    @friendship_status.setter
    def friendship_status(self, val: str) -> None:
        raise NotImplementedError


class IChatMember:
    _user_id: str

    @property
    def user_id(self) -> str:
        return self._user_id


class IChat(Protocol):
    _chat_id: str
    _members: List[IChatMember]
    _current_voice_members: List[IChatMember]

    @property
    def chat_id(self) -> str:
        raise NotImplementedError

    def add_member(self, friend: IChatMember) -> None:
        raise NotImplementedError

    def create_and_add_member(self, user_id: str):
        raise NotImplementedError

    def get_member_by_id(self, user_id) -> IChatMember | None:
        raise NotImplementedError

    def get_members(self) -> list[IChatMember]:
        raise NotImplementedError

    def delete_member_by_id(self, user_id: str) -> None:
        raise NotImplementedError

    # Работа с войс румой
    def add_voice_member(self, friend: IChatMember) -> None:
        raise NotImplementedError

    def delete_voice_member_by_id(self, user_id: str) -> None:
        raise NotImplementedError

    def get_voice_members(self) -> List[IChatMember]:
        raise NotImplementedError
