import os
import socket
from datetime import datetime
import json

from logic.client.Chat.ClientChat import Chat
from logic.client.IConnection.IConnection import IConnection, BaseConnection


class MessageConnection(IConnection, BaseConnection):
    def __init__(self, message_server_tcp: socket.socket, user):
        # self._cache_chat: Dict[str, list] = cache_chat #############################################################
        self._user = user

        # Сокет
        self._message_server_tcp: socket.socket = message_server_tcp  # Для сервера сообщений в чатах

        self._chat: Chat = None

        self._flg = True  # TODO: Сделать флаг false, когда закрывается сокет

    def send_message(self, message, current_chat_id: int):
        msg = {
            "chat_id": current_chat_id,
            "nickname": self._user.getNickName(),
            "message": message}
        self._message_server_tcp.sendall((json.dumps(msg)).encode('utf-8'))

    @property
    def chat(self):
        return self._chat

    @chat.setter
    def chat(self, chat: Chat):
        self._chat = chat

    def recv_server(self) -> None:
        while self.flg:
            try:
                buffer = ''
                msg = self._message_server_tcp.recv(4096).decode('utf-8')
                buffer += msg
                try:
                    arr = self.decode_multiple_json_objects(buffer)
                except json.JSONDecodeError:
                    continue
                for msg in arr:
                    dt = datetime.strptime(msg["date_now"], "%Y-%m-%d %H:%M:%S")
                    date_now = dt.strftime("%d.%m.%Y %H:%M")

                    if self._chat is None:
                        raise ValueError("chat = None, не прошла инициализация")
                    print(msg, "SERVER")
                    self._chat.socket_controller.recieve_message(str(self._chat.chat_id), msg["nickname"],
                                                                 msg["message"], date_now, 1, int(msg["was_seen"]))
                continue
            except os.error as e:
                if not self._flg:
                    print("Сокет закрылся корректно")
                else:
                    print(e)
            except ConnectionResetError:
                print("Ошибка, конец соединения")
                self._message_server_tcp.close()
                break



    @property
    def user(self):
        return self._user

    @property
    def flg(self):
        return self._flg

    def close(self) -> None:
        self._flg = False
