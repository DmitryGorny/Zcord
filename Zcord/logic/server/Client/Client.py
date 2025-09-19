import asyncio
import datetime
import json
from typing import List, Dict


class Client:
    def __init__(self, user_id: str, nick, last_online: str,  writer: asyncio.StreamWriter = None):
        self._id = user_id
        self._nick = nick
        self._writer = writer
        self._activityStatus = None
        self.__friends: Dict[str, Friend] = {}
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
    def friends(self, friends: List[Dict[str, str]]) -> None: #TODO: Подумать над хранением группы
        for friend_attrs in friends:
            fr = Friend(friend_attrs['id'],  # TODO: Подумать над фабрикой
                        friend_attrs['nickname'],
                        friend_attrs['chat_id'],
                        friend_attrs['status'],
                        friend_attrs["last_online"])

            self.__friends[friend_attrs['chat_id']] = fr #тут зачем-то был статус дружбы в ключе

    @property
    def writer(self) -> asyncio.StreamWriter:
        return self._writer

    @property
    def id(self) -> str:
        return self._id

    @property
    def nick(self):
        return self._nick

    # TODO:Переделать
    def add_friend(self, freind_name: str, chat_id: int) -> None:
        self.__friends[freind_name] = [chat_id, 1]  # 1 - статус друга (по дефолту стоит заявка в друзья)

    def delete_friend(self, friend_name: str) -> None:
        del self.__friends[friend_name]

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
    def __init__(self, user_id: str, nick, chat_id: str, friendship_status: str, last_online: str):
        super(Friend, self).__init__(user_id, nick, last_online)
        self._chat_id = chat_id
        self.friendship_status = friendship_status

    @property
    def writer(self) -> asyncio.StreamWriter:
        return self._writer

    @writer.setter
    def writer(self, writer: asyncio.StreamWriter):
        self._writer = writer
