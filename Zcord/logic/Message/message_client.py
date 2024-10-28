import socket
import threading
import msgspec
from logic.Main.Chat.ChatClass import Chat


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
    def recv_message(nickname):
        while True:
            try:
                message = MessageConnection.client_tcp.recv(1025)
                header = message[0:1]
                message = message[1:]
                if header == b'1':
                    cache = MessageConnection.deserialize(message)
                    for i in cache:
                        print(i)
                    continue
                message = message.decode("utf-8")
                if message == 'NICK':
                    MessageConnection.client_tcp.send(f"{nickname}, {MessageConnection.serialize(MessageConnection.cache_chat).decode('utf-8')}".encode('utf-8'))
                else:
                    if MainInterface.return_current_chat() != 0:
                        #if nickname != MessageConnection.user.getNickName():
                            cht = Chat.Chat(MainInterface.return_current_chat(), nickname, MessageConnection.user)
                            cht.recieveMessage(message)
                            print(message)
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


def thread_start(nickname):
    receive_thread = threading.Thread(target=MessageConnection.recv_message, args=(nickname, ))
    receive_thread.start()

def call(nickname, chat_id, user):
    SERVER_IP = "26.181.96.20"  # IP адрес сервера
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

    event = threading.Event()

    thread_start(nickname)

    return client_tcp


