import socket
import threading
import msgspec
from PyQt6.QtCore import pyqtSignal, QObject


class SygnalChanger(QObject):
    sygnal = pyqtSignal(str, str)
    clear = pyqtSignal()



class MainInterface:
    __current_chat = 1

    def __init__(self):
        pass

    @staticmethod
    def change_chat(current_chat, nickname, sygnalChanger):
        MainInterface.__current_chat = current_chat
        msg = f"{MainInterface.return_current_chat()}, {nickname}, {'__change_chat__'}".encode("utf-8")
        MessageConnection.client_tcp.sendall(msg)
        try:
            sygnalChanger.clear.connect(MessageConnection.chat.clearLayout) #Атрибут чат не может постоянно строка, а не объект
            sygnalChanger.clear.emit()
        except AttributeError:
            return

    @staticmethod
    def return_current_chat():
        return MainInterface.__current_chat


class MessageConnection(object):
    cache_chat = None
    client_tcp = None
    user = None
    chat = None
    messagesFromCacheInQueue = [] #Очередь из сообщений, от пользователя клиента до инициализации Chat в MessageConnection.chat

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
    def recv_message(nickname_yours, reciever, chats):
        while True:
            try:
                msg = MessageConnection.client_tcp.recv(1025)
                header = msg[0:1]
                msg = msg[1:]
                if header == b'1':
                    cache = MessageConnection.deserialize(msg)

                    for i in cache:
                        # i[0] - дата, i[1] - ник, i[2] - смска

                        #Проверяется ник отправителя и наличие объекта класса Chat
                        if i[1] == nickname_yours and MessageConnection.chat is None:
                            MessageConnection.messagesFromCacheInQueue.append(i)
                            continue

                        #Проверяем наличие объекта класса Chat и добавляем его при необходимости
                        if MessageConnection.chat is None:
                            for CertainChat in chats.get():
                                if i[1] == CertainChat.getNickName():
                                    MessageConnection.chat = CertainChat
                                    break

                        try:
                            print("- сигнал")
                            reciever.sygnal.disconnect()
                        except TypeError:
                            pass

                        reciever.sygnal.connect(MessageConnection.chat.recieveMessage)

                        if len(MessageConnection.messagesFromCacheInQueue) > 0:
                            for messageQ in MessageConnection.messagesFromCacheInQueue:
                                print(messageQ[2], messageQ[1])
                                reciever.sygnal.emit(messageQ[2], messageQ[1])

                        #print(i[2], i[1])
                        reciever.sygnal.emit(i[2], i[1])
                    continue

                msg = msg.decode("utf-8").split(", ")
                message = msg[0]
                if message == '__NICK__':
                    MessageConnection.client_tcp.send(f"{nickname_yours}, {MessageConnection.serialize(MessageConnection.cache_chat).decode('utf-8')}".encode('utf-8'))
                elif message == '__CONNECT__':
                    print("Подключено к серверу!")
                else:
                    print(msg)
 #Идет непонятная ошибка при первом заходе в чат после подключения
                    date_now = msg[1]
                    nickname = msg[2]


                    if MainInterface.return_current_chat() != 0:
                        if nickname == nickname_yours:
                            continue

                        try:
                            reciever.sygnal.disconnect()
                        except TypeError:
                            pass

                        if MessageConnection.chat is None or MessageConnection.chat.getNickName() != nickname:
                            for CertainChat in chats.get():
                                if nickname == CertainChat.getNickName():
                                    MessageConnection.chat = CertainChat
                                    break

                        reciever.sygnal.connect(MessageConnection.chat.recieveMessage)
                        reciever.sygnal.emit(message, nickname)
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
    receive_thread = threading.Thread(target=MessageConnection.recv_message, args=(nickname, reciever, chats, ))
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

    cache_chat = {}
    for k in chat_id:
        cache_chat[k] = []

    MessageConnection(client_tcp, cache_chat, user)

    print("Старт клиента сообщений")

    thread_start(nickname, chats)

    return [client_tcp]
