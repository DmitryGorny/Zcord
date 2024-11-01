import socket
import threading
from datetime import datetime
import msgspec
import copy


class MessageRoom(object):

    nicknames_in_chats = {}
    cache_chat = {}

    @staticmethod
    def set_nicknames_in_chats(arr):
        MessageRoom.nicknames_in_chats = {**MessageRoom.nicknames_in_chats, **arr}  # Какого хуя

    @staticmethod
    def set_cache_chat(arr):
        MessageRoom.cache_chat = {**arr, **MessageRoom.cache_chat}

    def __init__(self, chat_id):
        MessageRoom.set_cache_chat(copy.deepcopy(chat_id))
        MessageRoom.set_nicknames_in_chats(copy.deepcopy(chat_id))

    @staticmethod
    def serialize(x):
        ser = msgspec.json.encode(x)
        return ser

    @staticmethod
    def deserialize(message):
        cache = msgspec.json.decode(message)
        return cache

    @staticmethod
    def broadcast(msg):
        chat_code = msg[0]
        date_now = msg[1]
        nickname = msg[2]
        message = msg[3]
        for client in MessageRoom.nicknames_in_chats['chat_id'][chat_code]:
            ret = b'0' + f"{date_now}, {nickname}, {message}".encode('utf-8')
            clients[client].send(ret)

    @staticmethod
    def handle(client, nickname):
        while True:
            try:
                # Broadcasting Messages
                msg = client.recv(1024)
                msg = msg.decode('utf-8').split(", ")
                chat_code = str(msg[0])
                nickname = msg[1]
                message = msg[2]
                if message == "__change_chat__":
                    client.send(b'1' + MessageRoom.serialize(MessageRoom.cache_chat["chat_id"][chat_code]))
                    continue
                if nickname not in MessageRoom.nicknames_in_chats['chat_id'][chat_code]:
                    MessageRoom.nicknames_in_chats['chat_id'][chat_code].append(nickname)
                    try:
                        if chat_code != old_chat_cod:
                            del MessageRoom.nicknames_in_chats['chat_id'][old_chat_cod][MessageRoom.nicknames_in_chats['chat_id'][old_chat_cod].index(nickname)]
                    except UnboundLocalError:
                        pass

                    old_chat_cod = str(chat_code)

                date_now = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                date_now = date_now

                MessageRoom.broadcast((chat_code, message, date_now, nickname))

                MessageRoom.cache_chat["chat_id"][chat_code].append(f"{date_now + nickname}: {message}")

                print(MessageRoom.nicknames_in_chats)
                if len(MessageRoom.cache_chat["chat_id"][chat_code]) >= 20:
                    del MessageRoom.cache_chat["chat_id"][chat_code][0]

            except ConnectionResetError:
                # Removing And Closing Clients
                for j in MessageRoom.nicknames_in_chats['chat_id']:
                    if nickname in MessageRoom.nicknames_in_chats['chat_id'][j]:
                        MessageRoom.nicknames_in_chats['chat_id'][j].remove(nickname)
                clients.pop(nickname)
                client.close()
                print(f"{nickname} left!")
                break


def receive():
    while True:
        # Accept Connection
        client, address = server_msg.accept()
        print(f"Connected to {address}")

        # Request And Store Nickname
        client.send(b'0' + '__NICK__'.encode('utf-8'))
        msg = client.recv(1024)
        msg = msg.decode('utf-8').split(", ")
        print(msg)
        nickname = msg[0]
        chat_id = MessageRoom.deserialize(msg[1])
        clients[nickname] = client

        print(f"Nickname is {nickname}")

        client.send(b'0' + '__CONNECT__'.encode('utf-8'))

        MessageRoom(chat_id)
        # Start Handling Thread For Client
        thread = threading.Thread(target=MessageRoom.handle, args=(client, nickname,))
        thread.start()


if __name__ == "__main__":
    HOST = "26.36.124.241"
    PORT = 55555
    server_msg = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_msg.bind((HOST, PORT))
    server_msg.listen()
    clients = {}
    receive()
