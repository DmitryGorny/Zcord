import os
import socket
import threading
from datetime import datetime
import msgspec
from PyQt6.QtCore import pyqtSignal, QObject
import json

from logic.client.Strats.Strats import ChooseStrategy


class SygnalChanger(QObject):
    sygnal = pyqtSignal(str, str, str, int, int)
    friendRequestShow = pyqtSignal(str)
    clear = pyqtSignal()
    dynamicInterfaceUpdate = pyqtSignal(str, object) #См. документацию dynamicUpdate
    dynamicInterfaceUpdateAwaited = pyqtSignal(str, object, object)#См. документацию dynamicUpdate + threading.event
    unblockChat = pyqtSignal()
    awaitedMessageRecieve = pyqtSignal(str, str, str, int, int, object)
    changeUnseenStatus = pyqtSignal(int)
    blockAndUnblockScrollBar = pyqtSignal()


class Chat:
    def __init__(self, chat_id: int, friend_nick: str, socket_controller):
        self._chat_id = chat_id
        self._friend_nick = friend_nick
        self.socket_controller = socket_controller

    @property
    def friend_nick(self):
        return self._friend_nick

    @property
    def chat_id(self):
        return self._chat_id

class MainInterface:
    __current_chat = 1
    def __init__(self):
        pass

    @staticmethod
    def change_chat(current_chat, sygnalChanger=SygnalChanger()):
        MainInterface.__current_chat = int(current_chat)
        MessageConnection.send_service_message('__change_chat__')
        try:
            #sygnalChanger.clear.connect(MessageConnection.chat.clearLayout)
            #sygnalChanger.clear.emit()
            print(MessageConnection.chat)
            MessageConnection.chat.socket_controller.clearLayout(str(current_chat))
        except AttributeError:
            return

    @staticmethod
    def return_current_chat():
        return MainInterface.__current_chat
    @staticmethod
    def setCurrentChat(chat):
        MainInterface.__current_chat = chat


class MessageConnection(QObject):
    cache_chat = None
    client_tcp = None
    service_tcp = None
    user = None
    chat = None
    chatsList = []
    queueOfCahcedMessages = []
    flg = False
    MS_IP = None
    MS_PORT = None
    reciever = None


    def __init__(self, client_tcp, service_tcp, cache_chat, user):
        super(MessageConnection, self).__init__()
        MessageConnection.set_cache_chat(cache_chat)
        MessageConnection.set_client_tcp(client_tcp)
        MessageConnection.set_service_tcp(service_tcp)
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
    def set_service_tcp(service_tcp):
        MessageConnection.service_tcp = service_tcp

    @staticmethod
    def send_message(message):
        msg = {
            "chat_id": MainInterface.return_current_chat(),
            "nickname": MessageConnection.user.getNickName(),
            "message": message}
        MessageConnection.client_tcp.sendall((json.dumps(msg)).encode('utf-8'))

    @staticmethod
    def send_service_message(message):
        msg = {
            "chat_id": MainInterface.return_current_chat(),
            "nickname": MessageConnection.user.getNickName(),
            "message": message
        }
        MessageConnection.service_tcp.send((json.dumps(msg)).encode('utf-8'))
    @staticmethod
    def recv_message(nickname_yours):
        while MessageConnection.flg:
            try:
                msg = MessageConnection.client_tcp.recv(4096)
                msg = msg.decode("utf-8").split("&+& ")
                print("prohlo sms")
                try:
                    date_now = msg[1]
                    nickname = msg[2]
                    chat_code = msg[3]
                    wasSeen = msg[4]
                except IndexError:
                    continue
                dt = datetime.strptime(date_now, "%Y-%m-%d %H:%M:%S")
                date_now = dt.strftime("%d.%m.%Y %H:%M")

                if MainInterface.return_current_chat() == 1: #Проверить необходимость инициализации чата
                    if MessageConnection.chat is None or MessageConnection.chat._friend_nick != nickname:
                        for CertainChat in MessageConnection.chatsList:
                            if int(CertainChat.chat_id) == int(chat_code):
                                print(CertainChat)
                                MessageConnection.chat = CertainChat
                                break

                    try:
                        MessageConnection.reciever.sygnal.disconnect()
                    except TypeError:
                        pass

                    message = msg[0]
                    #MessageConnection.reciever.sygnal.connect(MessageConnection.chat.recieveMessage)
                    #MessageConnection.reciever.sygnal.emit(nickname, message, date_now, 1, int(wasSeen))
                    MessageConnection.chat.socket_controller.recieve_message(MessageConnection.chat.chat_id, nickname, message, date_now, 1, int(wasSeen))
            except os.error as e:
                if not MessageConnection.flg:
                    print("Сокет закрылся корректно")
                else:
                    print(e)
            except ConnectionResetError:
                print("Ошибка, конец соединения")
                MessageConnection.client_tcp.close()
                break
    @staticmethod
    def recv_server(nickname_yours):
        while MessageConnection.flg:
            try:
                buffer = ''
                msg = MessageConnection.service_tcp.recv(4096).decode('utf-8')
                header = msg[0:1]
                buffer += msg
                try:
                    arr = MessageConnection.decode_multiple_json_objects(buffer)
                except json.JSONDecodeError:
                    continue
                for msg in arr:
                    strategy = ChooseStrategy().get_strategy(msg["message_type"], MessageConnection, nickname_yours)
                    strategy.execute(msg)
                continue

                if header == b'2':
                    number = MessageConnection.deserialize(msg)
                    for key in number:
                        try:
                            chat = list(filter(lambda x: int(x.chat_id) == int(key), MessageConnection.chatsList))[0]
                            MessageConnection.reciever.dynamicInterfaceUpdate.emit("UPDATE-MESSAGE-NUMBER", (chat.chat_id, number[key][nickname_yours]))
                        except IndexError:
                            pass
                    continue

                if header == b'1':
                    cache = MessageConnection.deserialize(msg)
                    for i in cache:
                        event = threading.Event()
                        if MessageConnection.chat is None:
                            for chat in MessageConnection.chatsList:
                                if int(chat.chat_id) == int(i["chat_id"]):
                                    MessageConnection.chat = chat
                                    break
                        else:
                            if MessageConnection.chat.chat_id != int(i["chat_id"]):
                                for chat in MessageConnection.chatsList:
                                    if int(chat.chat_id) == int(i["chat_id"]):
                                        MessageConnection.chat = chat
                                        break

                        try:
                            MessageConnection.reciever.awaitedMessageRecieve.disconnect()
                        except TypeError:
                            pass
                                                            #Это все конченное уродство
                        try:
                            MessageConnection.reciever.friendRequestShow.disconnect()
                        except TypeError:
                            pass

                        if i["message"] == "__FRIEND_REQUEST__":
                            if i["sender_nick"] != nickname_yours:
                                MessageConnection.reciever.friendRequestShow.connect(MessageConnection.chat.showFriendRequestWidget)
                                MessageConnection.reciever.friendRequestShow.emit(i["sender_nick"])
                            else:
                                MessageConnection.reciever.awaitedMessageRecieve.connect(MessageConnection.chat.recieveMessage)
                                MessageConnection.reciever.awaitedMessageRecieve.emit(i["sender_nick"], "Вы отправили приглашение в друзья", i["date"], 1, 0, event)
                                event.wait()
                        else:
                            MessageConnection.reciever.awaitedMessageRecieve.connect(MessageConnection.chat.recieveMessage)

                            global WasSeen ##############################################################
                            WasSeen = int(i["WasSeen"])
                            if i["sender_nick"] != nickname_yours:
                                WasSeen = 1

                            dt = datetime.strptime(i["date"], "%Y-%m-%d %H:%M:%S")
                            date_now = dt.strftime("%d.%m.%Y %H:%M")

                            MessageConnection.reciever.awaitedMessageRecieve.emit(i["sender_nick"], i["message"], date_now,1, WasSeen, event)
                            event.wait()
                    continue

                if header == b'3':
                    cache = MessageConnection.deserialize(msg)

                    for i in cache:
                        event = threading.Event()
                        try:
                            MessageConnection.reciever.awaitedMessageRecieve.disconnect()
                        except TypeError:
                            pass
                        dt = datetime.strptime(i["date"], "%Y-%m-%d %H:%M:%S")
                        date_now = dt.strftime("%d.%m.%Y %H:%M")
                        MessageConnection.reciever.awaitedMessageRecieve.connect(MessageConnection.chat.addMessageOnTop)

                        WasSeen = int(i["WasSeen"])
                        if i["sender_nick"] != nickname_yours:
                            WasSeen = 1

                        MessageConnection.reciever.awaitedMessageRecieve.emit(i["sender_nick"], i["message"], date_now, 0, WasSeen, event)
                        event.wait()
                    try:
                        MessageConnection.reciever.blockAndUnblockScrollBar.disconnect()
                    except TypeError:
                        pass
                    MessageConnection.reciever.blockAndUnblockScrollBar.connect(MessageConnection.chat.slotForScroll)
                    MessageConnection.reciever.blockAndUnblockScrollBar.emit()

                    MessageConnection.send_message("__CAHCE-RECIEVED__", nickname_yours)

                    continue

                msg = msg.decode("utf-8").split("&+& ")
                message = msg[0]
                if message == '__NICK__':
                    MessageConnection.send_service_message(MessageConnection.serialize(MessageConnection.cache_chat).decode('utf-8'), nickname_yours)
                elif message == "__USER-INFO__":
                    dictToSend = {
                                  "friends": MessageConnection.user.getFriends(),
                                  "status": [MessageConnection.user.status.name, MessageConnection.user.status.color]
                                  }
                    MessageConnection.send_service_message(MessageConnection.serialize(dictToSend).decode('utf-8'), nickname_yours)
                elif message == '__CONNECT__':
                    #MessageConnection.send_service_message("__UPDATE-MESSAGES__", nickname_yours)
                    MessageConnection.client_tcp.connect((MessageConnection.MS_IP, MessageConnection.MS_PORT))
                    print("Подключено к серверу!")
                elif "__FRIEND_REQUEST__" in message:
                    if message.split("&")[1] == nickname_yours:
                        event1 = threading.Event()
                        event2 = threading.Event()
                        MessageConnection.reciever.dynamicInterfaceUpdateAwaited.emit("ADD-CANDIDATE-FRIEND", (msg[2], msg[3], 1), event1)
                        event1.wait()
                        MessageConnection.reciever.dynamicInterfaceUpdateAwaited.emit("UPDATE-CHATS", (msg[3], msg[2]), event2)
                        event2.wait()
                        MessageConnection.send_message(f"__FRIEND-REQUEST_ACTIVITY__&{msg[3]}", nickname_yours)
                    continue
                elif "__ACCEPT-REQUEST__" in message:
                    if msg[2] != nickname_yours:
                         MessageConnection.reciever.dynamicInterfaceUpdate.emit("ADD-FRIEND", (msg[2]))
                         MessageConnection.chat = list(filter(lambda chat: chat.chat_id == int(message.split("&")[1]), MessageConnection.chatsList))[0]
                         MessageConnection.reciever.unblockChat.connect(MessageConnection.chat.startMessaging)
                         MessageConnection.reciever.unblockChat.emit()
                    else:
                        MessageConnection.reciever.dynamicInterfaceUpdate.emit("ADD-FRIEND", (message.split("&")[2]))
                    continue
                elif "__REJECT-REQUEST__" in message or "__DELETE-REQUEST__" in message:
                    if msg[1] != nickname_yours:
                        MessageConnection.reciever.dynamicInterfaceUpdate.emit("DELETE-CHAT", (msg[1])) #TODO:msg[1] должен быть chat_id!!!!!!!!!!!!!
                    else:
                        MessageConnection.reciever.dynamicInterfaceUpdate.emit("DELETE-CHAT", (message.split("&")[2]))#TODO:message.split("&")[2] должен быть chat_id!!!!!!!!!!!!!
                    MainInterface.setCurrentChat(None)
                    for chat in MessageConnection.chatsList:
                        if int(chat.chat_id) == int(message.split("&")[1]):
                            MessageConnection.chatsList.remove(chat)
                            MessageConnection.cache_chat.pop(message.split("&")[1], None)
                            break
                    continue
                elif "__USER-JOINED__" in message:
                    try:
                        MessageConnection.reciever.changeUnseenStatus.disconnect()
                    except TypeError:
                        pass
                    MessageConnection.reciever.changeUnseenStatus.connect(MessageConnection.chat.changeUnseenStatus)
                    MessageConnection.reciever.changeUnseenStatus.emit(int(message.split("&")[1]))
                    continue
                else:
                    pass
            except os.error as e:
                if not MessageConnection.flg:
                    print("Сокет закрылся корректно")
                else:
                    print(e)
            except ConnectionResetError:
                print("Ошибка, конец соединения")
                MessageConnection.client_tcp.close()
                break

    @staticmethod
    def decode_multiple_json_objects(data):
        decoder = json.JSONDecoder()
        idx = 0
        results = []
        while idx < len(data):
            try:
                obj, idx_new = decoder.raw_decode(data[idx:])
                results.append(obj)
                idx += idx_new
            except json.JSONDecodeError:
                idx += 1
        return results

    @staticmethod
    def get_tcp_server(self):
        return self.client_tcp

    @staticmethod
    def deserialize(message):
        try: #Фикс ошибки при многократном change_chat
            cache = msgspec.json.decode(message)
        except msgspec.DecodeError:
            return []
        return cache

    @staticmethod
    def serialize(x):
        ser = msgspec.json.encode(x)
        return ser


def thread_start(nickname, dynamicUpdateCallback):
    reciever = SygnalChanger()
    reciever.dynamicInterfaceUpdate.connect(dynamicUpdateCallback)
    reciever.dynamicInterfaceUpdateAwaited.connect(dynamicUpdateCallback)

    MessageConnection.reciever = reciever

    #Слушаем сервисный порт
    receive_service_thread = threading.Thread(target=MessageConnection.recv_server, args=(nickname, ))
    receive_service_thread.start()

    #Слушаем чат
    recieve_message_thread = threading.Thread(target=MessageConnection.recv_message, args=(nickname, ))
    recieve_message_thread.start()

def call(user, chats, callback):
    SERVER_IP = "26.181.96.20"  # IP
    SERVER_PORT = 55558  # Порт, используемый сервером с сервисными сообщениями
    MESSAGE_SERVER_PORT = 55557

    try:
        service_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        service_tcp.connect((SERVER_IP, SERVER_PORT))
    except ConnectionRefusedError:
        print("Не удалось подключится")
        exit(0)

    try:
        client_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except ConnectionRefusedError:
        print("Не удалось подключится")
        exit(0)
    MessageConnection.MS_IP = SERVER_IP
    MessageConnection.MS_PORT = MESSAGE_SERVER_PORT
    cache_chat = {}

    while not chats.empty():
        attrs = chats.get()
        chat = Chat(attrs["chat_id"], attrs["nickname"], user.get_socket_controller())
        MessageConnection.addChatToList(chat)

        cache_chat[attrs["chat_id"]] = []
        chats.task_done()

    clientClass = MessageConnection(client_tcp, service_tcp, cache_chat, user)
    print("Старт клиента сообщений")

    MessageConnection.flg = True
    thread_start(user.getNickName(), callback)

    return [client_tcp, clientClass]
