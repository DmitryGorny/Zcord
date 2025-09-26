import json
import os
import socket
from typing import Dict

from logic.client.Chat.ClientChat import Chat
from logic.client.IConnection.IConnection import IConnection, BaseConnection
from logic.client.Strats.ClientServiceStrats import ChooseStrategy


class ServiceConnection(IConnection, BaseConnection):
    def __init__(self, tcp: socket.socket, msg_srv_tcp: socket.socket, ip_data: Dict[str, str], user):
        self._user = user

        self._flg = True

        self._service_tcp: socket.socket = tcp

        self._choose_strategy: ChooseStrategy = ChooseStrategy()

        self._cache_chat: Dict[str, list] = {}

        self._chat: Chat = None

        self._msg_srv_tcp: socket.socket = msg_srv_tcp
        self._ip_data = ip_data

    @property
    def chat(self) -> Chat:
        return self._chat

    @chat.setter
    def chat(self, chat: Chat) -> None:
        self._chat = chat

    @property
    def cache_chat(self) -> Dict[str, list]:
        return self._cache_chat

    def send_message(self, msg_type: str, message=None, current_chat_id: int = 0, extra_data: Dict[str, str] = None): # = 0 в случае, когда chat_id не играет роли
        msg = {
            'msg_type': msg_type,
            "chat_id": current_chat_id,
            "user_id": self._user.id,
            "nickname": self.user.getNickName(),
            "message": message if message is not None else '0'}

        if extra_data is not None:
            msg = msg | extra_data

        self._service_tcp.sendall((json.dumps(msg)).encode('utf-8'))

    def connect_to_msg_server(self):
        self._msg_srv_tcp.connect((self._ip_data["IP"], self._ip_data["PORT"]))

    def cache_chat(self, chat_id: str) -> None:
        self._cache_chat[chat_id] = []

    cache_chat = property(fset=cache_chat)

    def recv_server(self) -> None:
        while self._flg:
            try:
                buffer = ''
                msg = self._service_tcp.recv(4096).decode('utf-8')
                buffer += msg
                try:
                    arr = self.decode_multiple_json_objects(buffer)
                except json.JSONDecodeError:
                    continue
                for msg in arr:
                    strategy = self._choose_strategy.get_strategy(msg["message_type"], self, self._user.getNickName())
                    strategy.execute(msg)
                continue
            except os.error as e:
                if not self._flg:
                    print("Сокет закрылся корректно")
                else:
                    print(e)
            except ConnectionResetError:
                print("Ошибка, конец соединения")
                self._service_tcp.close()
                break

    @property
    def user(self):
        return self._user

    @property
    def flg(self):
        return self._flg

    def close(self) -> None:
        self._flg = False
