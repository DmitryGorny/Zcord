import socket
import threading
from datetime import datetime
import msgspec
import copy
from logic.db_handler.db_handler import db_handler


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
        db_fr = db_handler("26.181.96.20", "Dmitry", "gfggfggfg3D-", "zcord", "friendship")
        db_ms = db_handler("26.181.96.20", "Dmitry", "gfggfggfg3D-", "zcord", "messages_in_chats")
        pre_chat_ids = db_fr.getDataFromTableColumn("chat_id", f"WHERE friend_one_id = '{nickname}' OR friend_two_id = '{nickname}'")
        for pre_ch in pre_chat_ids:
            pre_cache = db_ms.getDataFromTableColumn("chat_id, message, sender_nick, date", f"WHERE chat_id = {pre_ch[0]}")
        print(pre_cache)
        for pre_ch in pre_cache:
            p = str(pre_ch[0])
            if p in MessageRoom.cache_chat:
                MessageRoom.cache_chat[p].append((pre_ch[3], pre_ch[2], pre_ch[1], p))
            else:
                MessageRoom.cache_chat[p] = [(pre_ch[3], pre_ch[2], pre_ch[1], p)]

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

                    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    MessageRoom.nicknames_in_chats[chat_id].append(nickname)
                    MessageRoom.cache_chat[chat_id].append((date_now, nickname, "__FRIEND_REQUEST__", chat_id))
                    continue

                if message == "__change_chat__":
                    print(MessageRoom.cache_chat)
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

                date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                MessageRoom.cache_chat[chat_code].append((date_now, nickname, message, chat_code))

                MessageRoom.broadcast((chat_code, message, date_now, nickname))
                if len(MessageRoom.cache_chat[chat_code]) >= 21:
                    db = db_handler("26.181.96.20", "Dmitry", "gfggfggfg3D-", "zcord", "messages_in_chats")
                    db.insertDataInTable("(chat_id, message, sender_nick, date)", f"({chat_code}, '{message}', '{nickname}', '{date_now}')")
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
    HOST = "26.36.124.241"
    PORT = 55556
    server_msg = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_msg.bind((HOST, PORT))
    server_msg.listen()
    clients = {}
    receive()
