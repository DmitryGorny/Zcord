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
        MessageRoom.nicknames_in_chats = {**MessageRoom.nicknames_in_chats, **arr}

    @staticmethod
    def set_cache_chat(arr):
        MessageRoom.cache_chat = {**arr, **MessageRoom.cache_chat}

    def __init__(self, chat_id):
        self.copyCacheChat(chat_id)

    @staticmethod
    def copyCacheChat(chat_id):
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
        for client in MessageRoom.nicknames_in_chats[chat_code]:
            ret = b'0' + f"{date_now}&+& {nickname}&+& {message}&+& {chat_code}".encode('utf-8')
            clients[client].send(ret)

    @staticmethod
    def handle(client, nickname):
        while True:
            try:
                # Broadcasting Messages
                flg = False
                msg = client.recv(1024)
                msg = msg.decode('utf-8').split("&+& ")
                chat_code = str(msg[0])
                nickname = msg[1]
                message = msg[2]

                if "__FRIEND-ADDING__" in message:
                    chats_id = settleFirstInformationAboutClients(client)[0]
                    MessageRoom.copyCacheChat(chats_id)

                    chat_id = message.split("&")[1]
                    #client.send(b'0' + f'__FRIEND_REQUEST__&{nickname}&{chat_id}'.encode('utf-8')) #Здесь

                    date_now = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                    date_now = date_now

                    continue
                if message == "__change_chat__":
                    client.send(b'1' + MessageRoom.serialize(MessageRoom.cache_chat[chat_code]))
                    flg = True

                if nickname not in MessageRoom.nicknames_in_chats[chat_code]:
                    MessageRoom.nicknames_in_chats[chat_code].append(nickname)
                    try:
                        if chat_code != old_chat_cod:
                            index = MessageRoom.nicknames_in_chats[old_chat_cod].index(nickname)
                            del MessageRoom.nicknames_in_chats[old_chat_cod][index]
                    except UnboundLocalError:
                        pass

                    old_chat_cod = str(chat_code)

                if flg:
                    continue

                date_now = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                date_now = date_now

                MessageRoom.cache_chat[chat_code].append((date_now, nickname, message, chat_code))

                MessageRoom.broadcast((chat_code, message, date_now, nickname))

                print(message)

                if len(MessageRoom.cache_chat[chat_code]) >= 21:
                    del MessageRoom.cache_chat[chat_code][0]

            except ConnectionResetError:
                # Removing And Closing Clients
                for j in MessageRoom.nicknames_in_chats:
                    if nickname in MessageRoom.nicknames_in_chats[j]:
                        MessageRoom.nicknames_in_chats[j].remove(nickname)
                clients.pop(nickname)
                client.close()
                print(f"{nickname} left!")
                break


def settleFirstInformationAboutClients(client):
        client.send(b'0' + '__NICK__'.encode('utf-8'))
        msg = client.recv(1024)
        msg = msg.decode('utf-8').split("&+& ")
        nickname = msg[0]
        chat_id = MessageRoom.deserialize(msg[1])
        clients[nickname] = client
        print(f"Nickname is {nickname}")
        return [chat_id, nickname]
def receive():
    while True:
        # Accept Connection
        client, address = server_msg.accept()
        print(f"Connected to {address}")

        # Request And Store Nickname
        nickAndId = settleFirstInformationAboutClients(client)

        client.send(b'0' + '__CONNECT__'.encode('utf-8'))

        MessageRoom(nickAndId[0])
        # Start Handling Thread For Client
        thread = threading.Thread(target=MessageRoom.handle, args=(client, nickAndId[1],))
        thread.start()


if __name__ == "__main__":
    HOST = "26.181.96.20"
    PORT = 55556
    server_msg = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_msg.bind((HOST, PORT))
    server_msg.listen()
    clients = {}
    receive()
