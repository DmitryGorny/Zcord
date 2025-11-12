import os
import socket
import json
from typing import Callable

from logic.client.Chat.ClientChat import Chat
from logic.client.IConnection.IConnection import IConnection, BaseConnection
from logic.client.Strats.MessageStrats import ChooseStrategy


class MessageConnection(IConnection, BaseConnection):
    def __init__(self, message_server_tcp: socket.socket, user, main_callback: Callable):
        self._choose_strategy: ChooseStrategy = ChooseStrategy()
        self._user = user

        # Сокет
        self._message_server_tcp: socket.socket = message_server_tcp  # Для сервера сообщений в чатах

        self._chat: Chat = None

        self._flg = True

        self._main_window_dynamic_update = main_callback

    def send_message(self, current_chat_id: int, message: str) -> None:
        """Метод для отпраки сообщений с флагом text"""
        msg = {
            "msg_type": 'CHAT-MESSAGE',
            "chat_id": current_chat_id,
            "user_id": self._user.id,
            "message": message,
            "type": 'text'
        }

        self._message_server_tcp.sendall((json.dumps(msg)).encode('utf-8'))

    def send_service_message(self, current_chat_id: str, service_message: str):
        """Метод для отправки сообщений с флагом service"""
        msg = {
            "msg_type": 'CHAT-MESSAGE',
            "chat_id": current_chat_id,
            "user_id": self._user.id,
            'service_message': service_message,
            "type": 'service'
        }
        self._message_server_tcp.sendall((json.dumps(msg)).encode('utf-8'))

    def send_message_server_service(self, current_chat_id: str, msg_type: str, data: dict):
        """Метод для отправки сервисных сообщений на message-server"""
        msg = {
            "msg_type": msg_type,
            "chat_id": current_chat_id,
            "user_id": self._user.id,
        }

        msg = msg | data
        self._message_server_tcp.sendall((json.dumps(msg)).encode('utf-8'))

    def call_main_dynamic_update(self, command: str, args: dict):
        try:
            self._main_window_dynamic_update.emit(command, args)
        except Exception as e:
            print(e)

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
                    try:
                        strategy = self._choose_strategy.get_strategy(msg["msg_type"], self)
                        strategy.execute(msg)
                    except TypeError as e:
                        print(e)
                    except KeyError as i:
                        print(i)
                continue
            except socket.timeout:
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
            except AttributeError: #TODO: Вот здесь прописать логику отключения сервера
                return

    @property
    def user(self):
        return self._user

    @property
    def flg(self):
        return self._flg

    def close(self) -> None:
        self._flg = False

