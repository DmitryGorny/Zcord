import socket
import threading
from datetime import datetime
import msgspec
import copy
from logic.db_handler.db_handler import db_handler


class MessageRoom(object):
    nicknames_in_chats = {}
    cache_chat = {}
    allFriends = None
    unseenMessages = {}


    @staticmethod
    def set_nicknames_in_chats(arr):
        MessageRoom.nicknames_in_chats = {**arr, **MessageRoom.nicknames_in_chats}

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
            try:
                clients[client].send(ret)
            except KeyError:
                continue

    @staticmethod
    def handle(client, nickname):
        db_fr = db_handler("26.181.96.20", "Dmitry", "gfggfggfg3D-", "zcord", "friendship")
        db_ms = db_handler("26.181.96.20", "Dmitry", "gfggfggfg3D-", "zcord", "messages_in_chats")
        pre_chat_ids = db_fr.getDataFromTableColumn("chat_id", f"WHERE friend_one_id = '{nickname}' OR friend_two_id = '{nickname}'")
        pre_cache = []

        db_fr = db_handler("26.181.96.20", "Dmitry", "gfggfggfg3D-", "zcord", "friendship")
        allFriends = db_fr.getDataFromTableColumn("chat_id, friend_one_id, friend_two_id", f"WHERE friend_one_id = '{nickname}' OR friend_two_id = '{nickname}'")
        for pre_ch in pre_chat_ids:
            if str(pre_ch[0]) not in MessageRoom.unseenMessages:
                MessageRoom.unseenMessages[str(pre_ch[0])] = 0 #записываются айди всех чатов пользователя
            x = db_ms.getDataFromTableColumn("id, chat_id, message, sender_nick, date, WasSeen", f"WHERE chat_id = {pre_ch[0]}")
            for k in x:
                pre_cache.append(k)
        for pre_ch in pre_cache:
            chat_id = str(pre_ch[1])
            cachedMessage = {"id": pre_ch[0], "chat_id": pre_ch[1], "message": pre_ch[2], "sender_nick": pre_ch[3], "date": pre_ch[4], "WasSeen": pre_ch[5]}
            if pre_ch[5] == 0:
                MessageRoom.unseenMessages[chat_id] += 1
            if chat_id in MessageRoom.cache_chat:
                if cachedMessage not in MessageRoom.cache_chat[chat_id]:
                    MessageRoom.cache_chat[chat_id].append(cachedMessage)
            else:
                MessageRoom.cache_chat[chat_id] = [cachedMessage]

        while True:
            try:
                # Broadcasting Messages
                flg = False
                msg = client.recv(1024)
                msg = msg.decode('utf-8').split("&+& ")
                chat_code = str(msg[0])
                nickname = msg[1]
                message = msg[2]
                date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                messageToChache = { #id 0, потом когда доабвляем в базу AI сам его назначит
                    "id": 0,
                    "chat_id": chat_code,
                    "message": message,
                    "sender_nick": nickname,
                    "date": date_now,
                    "WasSeen": 0
                }

                if "__UPDATE-MESSAGES__" in message:
                    #Плохой момент, в случае большого количества пользователей будет слишком долгий перебор на клиенет
                    client.send(b'2' + MessageRoom.serialize(MessageRoom.unseenMessages))
                    continue

                if "__FRIEND-ADDING__" in message:
                    chats_id = settleFirstInformationAboutClients(client)[0]
                    MessageRoom.copyCacheChat(chats_id)
                    chat_id = message.split("&")[1]
                    friendNick = message.split("&")[2]
                    messageToChache["message"] = "__FRIEND_REQUEST__"

                    MessageRoom.nicknames_in_chats[chat_id].append(nickname)
                    MessageRoom.nicknames_in_chats[chat_id].append(friendNick)
                    MessageRoom.cache_chat[chat_id].append(messageToChache)

                    db_fr_add = db_handler("26.181.96.20", "Dmitry", "gfggfggfg3D-", "zcord", "friends_adding")
                    db_fr_add.insertDataInTable("(chat_id, sender_nick, friend_nick, message, date)", f"({chat_id}, '{nickname}', '{friendNick}', '__FRIEND_REQUEST__', '{date_now}')")

                    #Передавать специализированные сообщения обычным броадакстом так себе идейка
                    MessageRoom.broadcast((chat_id, f"__FRIEND_REQUEST__&{friendNick}", date_now, nickname))

                    continue

                if "__ACCEPT-REQUEST__" in message:
                    if message.split("&")[2] not in MessageRoom.nicknames_in_chats[message.split("&")[1]]:
                        MessageRoom.nicknames_in_chats[message.split("&")[1]].append(message.split("&")[2])
                    #Передавать специализированные сообщения обычным броадакстом так себе идейка +
                    MessageRoom.broadcast((message.split("&")[1], message, "[]", nickname))
                    continue

                if "__REJECT-REQUEST__" in message or "__DELETE-REQUEST__" in message:
                    if message.split("&")[2] not in MessageRoom.nicknames_in_chats[message.split("&")[1]]:
                        MessageRoom.nicknames_in_chats[message.split("&")[1]].append(message.split("&")[2])
                    MessageRoom.broadcast((message.split("&")[1], message, "[]", nickname))
                    continue

                if message == "__change_chat__":
                    client.send(b'1' + MessageRoom.serialize(MessageRoom.cache_chat[chat_code]))
                    flg = True

                    for message in MessageRoom.cache_chat[chat_code]:
                        message["WasSeen"] = 1

                    MessageRoom.unseenMessages[str(chat_code)] = 0
                    clients[nickname].send(b'2' + MessageRoom.serialize({chat_code: MessageRoom.unseenMessages[chat_code]}))

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

                if len(MessageRoom.nicknames_in_chats[chat_code]) > 1:
                    messageToChache["WasSeen"] = 1

                MessageRoom.cache_chat[chat_code].append(messageToChache)

                if len(MessageRoom.nicknames_in_chats[chat_code]) == 1:
                    MessageRoom.unseenMessages[chat_code] += 1
                    for frineds in allFriends:
                        if frineds[0] == int(chat_code):
                            try:
                                if frineds[1] != nickname:
                                    clients[frineds[1]].send(b'2' + MessageRoom.serialize({chat_code: MessageRoom.unseenMessages[chat_code]}))
                                    break

                                if frineds[2] != nickname:
                                    clients[frineds[2]].send(b'2' + MessageRoom.serialize({chat_code: MessageRoom.unseenMessages[chat_code]}))
                                    break
                            except KeyError:
                                break
                MessageRoom.broadcast((chat_code, message, date_now, nickname))
                if len(MessageRoom.cache_chat[chat_code]) >= 21:
                    db = db_handler("26.181.96.20", "Dmitry", "gfggfggfg3D-", "zcord", "messages_in_chats")
                    if messageToChache["id"] == 0:
                        db.insertDataInTable("(chat_id, message, sender_nick, date, WasSeen)", f"({chat_code}, '{message}', '{nickname}', '{date_now}', '{messageToChache['WasSeen']}')")
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
    db_prefr = db_handler("26.181.96.20", "Dmitry", "gfggfggfg3D-", "zcord", "friends_adding")
    pre_fr_add = db_prefr.getDataFromTableColumn("id, chat_id, sender_nick, friend_nick, message, date")
    if len(pre_fr_add) != 0:
        for l in pre_fr_add:
            chat_id = str(l[1])
            cachedMessage = {"id": l[0], "chat_id": l[1], "message": l[4], "sender_nick": l[2], "date": l[5]}
            if chat_id in MessageRoom.cache_chat.keys():
                MessageRoom.cache_chat[chat_id].append(cachedMessage)
            else:
                MessageRoom.cache_chat[chat_id] = [cachedMessage]
    receive()
