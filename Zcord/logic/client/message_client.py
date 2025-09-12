import os
import socket
from datetime import datetime
import json

from logic.client.Chat.ClientChat import Chat
from logic.client.IConnection.IConnection import IConnection, BaseConnection
from logic.client.Strats.MessageStrats import ChooseStrategy


class MessageConnection(IConnection, BaseConnection):
    def __init__(self, message_server_tcp: socket.socket, user):
        self._choose_strategy: ChooseStrategy = ChooseStrategy()
        self._user = user

        # Сокет
        self._message_server_tcp: socket.socket = message_server_tcp  # Для сервера сообщений в чатах

        self._chat: Chat = None

        self._flg = True

        self._block_scroll_cache = False

    def send_message(self, current_chat_id: int, message=None, msg_type: str = "CHAT-MESSAGE",
                     extra_data: dict = None) -> None:
        msg = {
            "type": msg_type,
            "chat_id": current_chat_id,
            "user_id": self._user.id,
        }

        if extra_data is None:
            msg["message"] = message
        else:
            msg = msg | extra_data

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
                    #try:
                        #print(msg)
                        strategy = self._choose_strategy.get_strategy(msg["type"], self)
                        strategy.execute(msg)
                    #except TypeError as e:
                        #print(e, 11111)
                        #pass
                    #except KeyError as i:
                        #print(i, 22222)
                        #pass
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
