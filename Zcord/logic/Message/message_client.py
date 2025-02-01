import socket
import threading
import time

import msgspec
from PyQt6.QtCore import pyqtSignal, QObject, QCoreApplication, QThread


class SygnalChanger(QObject):
    sygnal = pyqtSignal(str, str)
    friendRequestShow = pyqtSignal(str)
    clear = pyqtSignal()
    dynamicInterfaceUpdate = pyqtSignal(str, object) #См. документацию dynamicUpdate
    unblockChat = pyqtSignal()
    chat = ""

class MainInterface:
    __current_chat = 1

    def __init__(self):
        pass

    @staticmethod
    def change_chat(current_chat, nickname, sygnalChanger):
        MainInterface.__current_chat = current_chat
        msg = f"{MainInterface.return_current_chat()}&+& {nickname}&+& {'__change_chat__'}".encode("utf-8")
        MessageConnection.client_tcp.sendall(msg)
        try:
            sygnalChanger.clear.connect(MessageConnection.chat.clearLayout) #Атрибут чат не может постоянно строка, а не объект
            sygnalChanger.clear.emit()
        except AttributeError:
            return

    @staticmethod
    def return_current_chat():
        return MainInterface.__current_chat


class MessageConnection(QObject):
    cache_chat = None
    client_tcp = None
    user = None
    chat = None
    chatsList = []
    queueOfCahcedMessages = []

    def __init__(self, client_tcp, cache_chat, user):
        super(MessageConnection, self).__init__()
        MessageConnection.set_cache_chat(cache_chat)
        MessageConnection.set_client_tcp(client_tcp)
        MessageConnection.set_user(user)

    @staticmethod
    def set_user(user):
        MessageConnection.user = user


    @staticmethod
    def addChatToList(chatObject):
        MessageConnection.chatsList.append(chatObject)

    @staticmethod
    def addChat(chat_id):
        MessageConnection.cache_chat[chat_id] = []

    @staticmethod
    def set_cache_chat(cache_chat):
        MessageConnection.cache_chat = cache_chat

    @staticmethod
    def set_client_tcp(client_tcp):
        MessageConnection.client_tcp = client_tcp

    @staticmethod
    def send_message(message, nickname):
        msg = f"{MainInterface.return_current_chat()}&+& {nickname}&+& {message}".encode("utf-8")
        MessageConnection.client_tcp.sendall(msg)

    @staticmethod
    def recv_message(nickname_yours, reciever):
        while True:
            try:
                msg = MessageConnection.client_tcp.recv(4096)
                header = msg[0:1]
                msg = msg[1:]
                if header == b'2':
                    number = MessageConnection.deserialize(msg)
                    for key in number:
                        try:
                            chat = list(filter(lambda x: int(x.getChatId()) == int(key), MessageConnection.chatsList[0]))[0]
                            reciever.dynamicInterfaceUpdate.emit("UPDATE-MESSAGE-NUMBER", (chat, number[key]))
                        except IndexError:
                            pass
                    continue

                if header == b'1':
                    cache = MessageConnection.deserialize(msg)
                    for i in cache:
                        if MessageConnection.chat is None:
                            for chat in MessageConnection.chatsList[0]:
                                if int(chat.getChatId()) == int(i["chat_id"]):
                                    MessageConnection.chat = chat
                                    break
                        else:
                            if MessageConnection.chat.getChatId() != int(i["chat_id"]):
                                for chat in MessageConnection.chatsList[0]:
                                    if int(chat.getChatId()) == int(i["chat_id"]):
                                        MessageConnection.chat = chat
                                        break

                        try:
                            reciever.sygnal.disconnect()
                        except TypeError:
                            pass
                                                            #Это все конченное уродство
                        try:
                            reciever.friendRequestShow.disconnect()
                        except TypeError:
                            pass

                        if i["message"] == "__FRIEND_REQUEST__":
                            if i["sender_nick"] != nickname_yours:
                                reciever.friendRequestShow.connect(MessageConnection.chat.showFriendRequestWidget)
                                reciever.friendRequestShow.emit(i["sender_nick"])
                            else:
                                reciever.sygnal.connect(MessageConnection.chat.recieveMessage)
                                reciever.sygnal.emit(i["sender_nick"], "Вы отправили приглашение в друзья")
                        else:
                            reciever.sygnal.connect(MessageConnection.chat.recieveMessage)
                            reciever.sygnal.emit(i["sender_nick"], i["message"])

                        time.sleep(0.01) #Костыль. Что-то в emit (chat.recieveMessage) работает асинхронно???

                    continue

                msg = msg.decode("utf-8").split("&+& ")
                message = msg[0]
                if message == '__NICK__':
                    MessageConnection.client_tcp.send(f"{nickname_yours}&+& {MessageConnection.serialize(MessageConnection.cache_chat).decode('utf-8')}".encode('utf-8'))
                elif message == '__CONNECT__':
                    MessageConnection.send_message("__UPDATE-MESSAGES__", nickname_yours)
                    print("Подключено к серверу!")
                elif "__FRIEND_REQUEST__" in message:
                    if message.split("&")[1] == nickname_yours:
                        reciever.dynamicInterfaceUpdate.emit("ADD-CANDIDATE-FRIEND", (msg[2], msg[3], 1))
                        reciever.dynamicInterfaceUpdate.emit("UPDATE-CHATS", (msg[3], msg[2]))
                    continue
                elif "__ACCEPT-REQUEST__" in message:
                    if msg[2] != nickname_yours:
                         reciever.dynamicInterfaceUpdate.emit("ADD-FRIEND", (msg[2]))
                         MessageConnection.chat = list(filter(lambda chat: chat.getChatId() == int(message.split("&")[1]), MessageConnection.chatsList[0]))[0]
                         reciever.unblockChat.connect(MessageConnection.chat.startMessaging)
                         reciever.unblockChat.emit()
                    else:
                        reciever.dynamicInterfaceUpdate.emit("ADD-FRIEND", (message.split("&")[2]))
                    continue
                elif "__REJECT-REQUEST__" in message or "__DELETE-REQUEST__" in message:
                    if msg[2] != nickname_yours:
                        reciever.dynamicInterfaceUpdate.emit("DELETE-CHAT", (msg[2]))
                    else:
                        reciever.dynamicInterfaceUpdate.emit("DELETE-CHAT", (message.split("&")[2]))
                    continue
                else:
                    date_now = msg[1]
                    nickname = msg[2]
                    chat_code = msg[3]

                    if MainInterface.return_current_chat() != 0:
                        if nickname == nickname_yours:
                            continue

                        if MessageConnection.chat is None or MessageConnection.chat.getNickName() != nickname:
                            for CertainChat in MessageConnection.chatsList[0]:
                                if int(CertainChat.getChatId()) == int(chat_code):
                                    MessageConnection.chat = CertainChat
                                    break

                        try:
                            reciever.sygnal.disconnect()
                        except TypeError:
                            pass

                        reciever.sygnal.connect(MessageConnection.chat.recieveMessage)
                        reciever.sygnal.emit(nickname, message)
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


def thread_start(nickname, dynamicUpdateCallback):
    reciever = SygnalChanger()
    reciever.dynamicInterfaceUpdate.connect(dynamicUpdateCallback)
    receive_thread = threading.Thread(target=MessageConnection.recv_message, args=(nickname, reciever, ))
    receive_thread.start()


def call(nickname, chat_id, user, chats, callback):
    SERVER_IP = "26.181.96.20"  # IP адрес сервера
    SERVER_PORT = 55556  # Порт, используемый сервером

    try:
        client_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_tcp.connect((SERVER_IP, SERVER_PORT))
    except ConnectionRefusedError:
        print("Не удалось подключится к серверу или сервер неактивен")
        exit(0)

    cache_chat = {}
    for k in chat_id:
        cache_chat[k] = []

    clientClass = MessageConnection(client_tcp, cache_chat, user)

    while not chats.empty():
        MessageConnection.addChatToList(chats.get()) #достаем объекты chat из очереди и пихаем их в массив


    print("Старт клиента сообщений")

    thread_start(nickname, callback)

    return [client_tcp, clientClass]
