import socket
import threading
import msgspec
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtCore import QThread

class SygnalChanger(QObject):
    sygnal = pyqtSignal()
class MainInterface:
    __current_chat = 1

    def __init__(self):
        pass

    @staticmethod
    def change_chat(current_chat, nickname):
        MainInterface.__current_chat = current_chat
        msg = f"{MainInterface.return_current_chat()}, {nickname}, {'change chat'}".encode("utf-8")
        MessageConnection.client_tcp.sendall(msg)

    @staticmethod
    def return_current_chat():
        return MainInterface.__current_chat


class MessageConnection(object):
    cache_chat = 0
    client_tcp = 0
    user = ""


    def __init__(self, client_tcp, cache_chat, user):
        super(MessageConnection, self).__init__()
        MessageConnection.set_cache_chat(cache_chat)
        MessageConnection.set_client_tcp(client_tcp)
        MessageConnection.set_user(user)



    @staticmethod
    def set_user(user):
        MessageConnection.user = user

    @staticmethod
    def set_cache_chat(cache_chat):
        MessageConnection.cache_chat = cache_chat

    @staticmethod
    def set_client_tcp(client_tcp):
        MessageConnection.client_tcp = client_tcp

    @staticmethod
    def send_message(message, nickname):
        msg = f"{MainInterface.return_current_chat()}, {nickname}, {message}".encode("utf-8")
        MessageConnection.client_tcp.sendall(msg)

    @staticmethod
    def recv_message(nickname_yours, reciever):
        while True:
            try:
                msg = MessageConnection.client_tcp.recv(1025)
                header = msg[0:1]
                msg = msg[1:]
                if header == b'1':
                    cache = MessageConnection.deserialize(msg)
                    for i in cache:
                        print(i)
                    continue
                msg = msg.decode("utf-8").split(", ")
                message = msg[0]
                if message == 'NICK':
                    MessageConnection.client_tcp.send(f"{nickname_yours}, {MessageConnection.serialize(MessageConnection.cache_chat).decode('utf-8')}".encode('utf-8'))
                elif message == 'CONNECT':
                    print("Подключено к серверу!")
                else:
                    date_now = msg[1]
                    nickname = msg[2]
                    if MainInterface.return_current_chat() != 0:
                        print(nickname)
                        if nickname != MessageConnection.user.getNickName():
                            reciever.finished.emit(nickname, message)
            except ConnectionResetError:
                print("Ошибка, конец соединения")
                MessageConnection.client_tcp.close()
                break


    @staticmethod
    def get_tcp_server(self):
        return self.client_tcp

    @staticmethod
    def deserialize(message):
        cache = msgspec.json.decode(message)
        return cache

    @staticmethod
    def serialize(x):
        ser = msgspec.json.encode(x)
        return ser


def thread_start(nickname, chats):
    reciever = SygnalChanger()
    for chat in chats.get():
        if chat.getNickName() == nickname:
            reciever.sygnal.connect(chat.recieveMessage)
    receive_thread = threading.Thread(target=MessageConnection.recv_message, args=(nickname, reciever,))
    receive_thread.start()


def call(nickname, chat_id, user, chats):
    SERVER_IP = "26.36.124.241"  # IP адрес сервера
    SERVER_PORT = 55555  # Порт, используемый сервером

    try:
        client_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_tcp.connect((SERVER_IP, SERVER_PORT))
    except ConnectionRefusedError:
        print("Не удалось подключится к серверу или сервер неактивен")
        exit(0)

    cache_chat = {"chat_id": {}}
    for k in chat_id:
        cache_chat["chat_id"][k] = []

    MessageConnection(client_tcp, cache_chat, user)

    print("Старт клиента сообщений")

    thread = thread_start(nickname, chats)

    return [client_tcp, thread]
