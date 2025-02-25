import json
import socket
import threading
from datetime import datetime
import msgspec
import copy
from logic.db_handler.db_handler import db_handler
import select
import ijson


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
        wasSeen = msg[4]
        for client in MessageRoom.nicknames_in_chats[chat_code]:
            ret = b'0' + f"{date_now}&+& {nickname}&+& {message}&+& {chat_code}&+& {wasSeen}".encode('utf-8')
            try:
                clients[client].send(ret)
            except KeyError:
                continue
    @staticmethod
    def decode_multiple_json_objects(data):
        decoded_objects = []
        parser = ijson.items(data, '')
        for obj in parser:
            decoded_objects.append(obj)
        return decoded_objects
    @staticmethod
    def handle(client, nickname):
        currentMessageIndex = -20
        db_fr = db_handler("26.181.96.20", "Dmitry", "gfggfggfg3D-", "zcord", "friendship")
        db_ms = db_handler("26.181.96.20", "Dmitry", "gfggfggfg3D-", "zcord", "messages_in_chats")
        pre_chat_ids = db_fr.getDataFromTableColumn("chat_id", f"WHERE friend_one_id = '{nickname}' OR friend_two_id = '{nickname}'")
        pre_cache = []
        global allFriends
        db_fr = db_handler("26.181.96.20", "Dmitry", "gfggfggfg3D-", "zcord", "friendship")
        allFriends = db_fr.getDataFromTableColumn("chat_id, friend_one_id, friend_two_id", f"WHERE friend_one_id = '{nickname}' OR friend_two_id = '{nickname}'")
        for pre_ch in pre_chat_ids:
            if str(pre_ch[0]) not in MessageRoom.unseenMessages:
                friendArr = list(filter(lambda x: pre_ch[0] == x[0], allFriends))[0]
                MessageRoom.unseenMessages[str(pre_ch[0])] = {friendArr[1]: 0, friendArr[2]: 0}
            x = db_ms.getDataFromTableColumn("id, chat_id, message, sender_nick, date, WasSeen", f"WHERE chat_id = {pre_ch[0]}")
            for k in x:
                k[4] = k[4].strftime("%Y-%m-%d %H:%M:%S")
                pre_cache.append(k)
        if len(pre_cache) != 0 and len(MessageRoom.cache_chat[str(pre_cache[0][1])]) == 0:
            for pre_ch in pre_cache:
                chat_id = str(pre_ch[1])
                cachedMessage = {"id": pre_ch[0], "chat_id": pre_ch[1], "message": pre_ch[2], "sender_nick": pre_ch[3], "date": pre_ch[4], "WasSeen": pre_ch[5]}
                if pre_ch[5] == 0:
                    nicknameToRecive = list(filter(lambda x: x != nickname, MessageRoom.unseenMessages[chat_id].keys()))[0]
                    if pre_ch[3] == nicknameToRecive:
                        MessageRoom.unseenMessages[chat_id][nickname] += 1
                    else:
                        MessageRoom.unseenMessages[chat_id][nicknameToRecive] += 1
                if chat_id in MessageRoom.cache_chat:
                    if cachedMessage not in MessageRoom.cache_chat[chat_id]:
                        MessageRoom.cache_chat[chat_id].append(cachedMessage)
                else:
                    MessageRoom.cache_chat[chat_id] = [cachedMessage]
        userGotCahceFlag = True
        while True:
            buffer = ""
            try:
                # Broadcasting Messages
                flg = False
                msg = client.recv(4096)
                msg = msg.decode('utf-8')
                buffer += msg
                try:
                    arr = MessageRoom.decode_multiple_json_objects(buffer)
                    buffer = ""
                except ijson.common.IncompleteJSONError:
                    continue

                for msg in arr:
                    chat_code = str(msg["chat_id"])
                    nickname = msg["nickname"]
                    message = msg["message"]
                    date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    messageToChache = { #id 0, потом когда доабвляем в базу AI сам его назначит
                        "id": 0,
                        "chat_id": chat_code,
                        "message": message,
                        "sender_nick": nickname,
                        "date": date_now,
                        "WasSeen": 0
                    }
                    if "__UPDATE-MESSAGES__" in message:
                        try:
                            client.send(b'2' + MessageRoom.serialize(MessageRoom.unseenMessages))
                        except KeyError:
                            pass

                        continue

                    if "__FRIEND-REQUEST_ACTIVITY__" in message:
                        messageToChache["chat_id"] = message.split("&")[1]
                        client.send(b'2' + MessageRoom.serialize({message.split("&")[1]: MessageRoom.unseenMessages[message.split("&")[1]]}))
                        continue

                    if "__FRIEND-ADDING__" in message:
                        chats_id = settleFirstInformationAboutClients(client)[0]
                        MessageRoom.copyCacheChat(chats_id)
                        chat_id = message.split("&")[1]
                        friendNick = message.split("&")[2]
                        MessageRoom.unseenMessages[chat_id] = {nickname: 0, friendNick: 1}
                        messageToChache["chat_id"] = chat_id
                        messageToChache["message"] = "__FRIEND_REQUEST__"
                        MessageRoom.cache_chat[chat_id].append(messageToChache)
                        allFriends = db_fr.getDataFromTableColumn("chat_id, friend_one_id, friend_two_id", f"WHERE friend_one_id = '{nickname}' OR friend_two_id = '{nickname}'")
                        db_fr_add = db_handler("26.181.96.20", "Dmitry", "gfggfggfg3D-", "zcord", "friends_adding")
                        db_fr_add.insertDataInTable("(chat_id, sender_nick, friend_nick, message, date, WasSeen)", f"({chat_id}, '{nickname}', '{friendNick}', "
                                                                                                          f"'__FRIEND_REQUEST__', '{date_now}', 0)")
                        #Передавать специализированные сообщения обычным броадакстом так себе идейка
                        try:
                            messageWithRequest = f"__FRIEND_REQUEST__&{friendNick}&+& {date_now}&+& {nickname}&+& {chat_id}"
                            clients[nickname].send(b'0' + messageWithRequest.encode('utf-8'))
                            clients[friendNick].send(b'0' + messageWithRequest.encode('utf-8'))
                        except KeyError:
                            pass
                        continue

                    if "__ACCEPT-REQUEST__" in message:
                        splitedMessage = message.split("&")
                        try:
                            messageToSend = f"{message}&+& []&+& {nickname}&+& {splitedMessage[1]}"
                            clients[nickname].send(b'0' + messageToSend.encode('utf-8'))
                            clients[splitedMessage[2]].send(b'0' + messageToSend.encode('utf-8'))
                        except KeyError:
                            pass

                        MessageRoom.cache_chat[splitedMessage[1]] = []
                        continue

                    if "__REJECT-REQUEST__" in message or "__DELETE-REQUEST__" in message:
                        splitedMessage = message.split("&")
                        if splitedMessage[2] not in MessageRoom.nicknames_in_chats[splitedMessage[1]]:
                            MessageRoom.nicknames_in_chats[splitedMessage[1]].append(splitedMessage[2])
                        del MessageRoom.unseenMessages[splitedMessage[1]]
                        MessageRoom.broadcast((splitedMessage[1], message, "[]", nickname, 0))
                        del MessageRoom.nicknames_in_chats[splitedMessage[1]]
                        del MessageRoom.cache_chat[splitedMessage[1]]
                        continue

                    if "__CAHCE-RECIEVED__" in message:
                        userGotCahceFlag = True
                        continue

                    if "__CACHED-REQUEST__" in message:
                        if not userGotCahceFlag:
                            continue

                        if currentMessageIndex > 0:
                            end = currentMessageIndex
                            currentMessageIndex = max(0, currentMessageIndex - 10)
                            if currentMessageIndex == 0:
                                arrayToSend = MessageRoom.cache_chat[chat_code][:end]
                            else:
                                arrayToSend = MessageRoom.cache_chat[chat_code][currentMessageIndex:end]
                        else:
                            continue

                        arrayToSend.reverse()
                        client.send(b'3' + MessageRoom.serialize(arrayToSend))
                        userGotCahceFlag = False
                        MessageRoom.unseenMessages[chat_code][nickname] = max(0,  MessageRoom.unseenMessages[chat_code][nickname] - len(arrayToSend))
                        clients[nickname].send(b'2' + MessageRoom.serialize({chat_code: MessageRoom.unseenMessages[chat_code]}))
                        for i in range(len(arrayToSend)):
                            MessageRoom.cache_chat[chat_code][i]["WasSeen"] = 1

                        for clientNick in MessageRoom.nicknames_in_chats[chat_code]:
                            if clientNick != nickname:
                                clients[clientNick].send(b'0' + f"__USER-JOINED__&{len(arrayToSend)}".encode('utf-8'))
                        continue

                    if message == "__change_chat__":
                        numberOfMessagesToShow = 15
                        if len(MessageRoom.cache_chat[chat_code]) != 0:
                            client.send(b'1' + MessageRoom.serialize(MessageRoom.cache_chat[chat_code][-numberOfMessagesToShow:]))
                            currentMessageIndex = len(MessageRoom.cache_chat[chat_code]) - numberOfMessagesToShow
                            if MessageRoom.cache_chat[chat_code][-1]["WasSeen"] != 1:
                                MessageRoom.unseenMessages[chat_code][nickname] = max(0,  MessageRoom.unseenMessages[chat_code][nickname] - 20)
                                clients[nickname].send(b'2' + MessageRoom.serialize({chat_code: MessageRoom.unseenMessages[chat_code]}))
                                for message in MessageRoom.cache_chat[chat_code][::-1]:
                                    if MessageRoom.cache_chat[chat_code][::-1].index(message) == 20:
                                        break
                                    if nickname != message["sender_nick"]:
                                        message["WasSeen"] = 1


                            for clientNick in MessageRoom.nicknames_in_chats[chat_code]:
                                clients[clientNick].send(b'0' + "__USER-JOINED__&20".encode('utf-8'))

                        flg = True

                    if nickname not in MessageRoom.nicknames_in_chats[chat_code]:
                        MessageRoom.nicknames_in_chats[chat_code].append(nickname)

                        try:
                            if chat_code != old_chat_cod:
                                index = MessageRoom.nicknames_in_chats[old_chat_cod].index(nickname)
                                MessageRoom.nicknames_in_chats[old_chat_cod].remove(nickname)
                        except UnboundLocalError as e:
                            print(e)
                            pass
                        except KeyError as e:
                            print(e)
                            pass
                        old_chat_cod = str(chat_code)

                    if flg:
                        continue

                    if len(MessageRoom.nicknames_in_chats[chat_code]) > 1:
                        messageToChache["WasSeen"] = 1

                    MessageRoom.cache_chat[chat_code].append(messageToChache)
                    MessageRoom.broadcast((chat_code, message, date_now, nickname, messageToChache["WasSeen"]))
                    if len(MessageRoom.nicknames_in_chats[chat_code]) == 1:
                        nicknameToRecive = list(filter(lambda x: x != nickname, MessageRoom.unseenMessages[chat_code].keys()))[0]
                        if messageToChache["WasSeen"] != 1:
                            MessageRoom.unseenMessages[chat_code][nicknameToRecive] += 1
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

            except ConnectionResetError:
                # Removing And Closing Clients
                db = db_handler("26.181.96.20", "Dmitry", "gfggfggfg3D-", "zcord", "messages_in_chats")
                lastId = db.getAI_Id()[0][0]
                if lastId == 1:
                    db.insertDataInTable("(chat_id, message, sender_nick, date, WasSeen)", f"(1, '__FIRST__', '0', '{date_now}', 1)")
                    lastId = db.getAI_Id()[0][0]
                i = 1
                messagesToInsert = []
                messagesToUpdate = []
                for chat_code in MessageRoom.nicknames_in_chats.keys():
                    for message in MessageRoom.cache_chat[chat_code]:
                        if message['message'] == "__FRIEND_REQUEST__":
                            db_fr_add = db_handler("26.181.96.20", "Dmitry", "gfggfggfg3D-", "zcord", "friends_adding")
                            db_fr_add.UpdateRequest("WasSeen", message['WasSeen'], f"WHERE chat_id = {message['chat_id']}")
                            continue

                        if message["id"] == 0:
                            mesArr = f"('{message['chat_id']}', '{message['message']}', '{message['sender_nick']}', '{message['date']}', '{message['WasSeen']}')"
                            messagesToInsert.append(mesArr)
                            message["id"] = lastId + i
                            i += 1
                        else:
                            messagesToUpdate.append((message["WasSeen"], f"WHERE id = {message['id']}"))
                            pass
                    if len(MessageRoom.nicknames_in_chats[chat_code]) == 1:
                        MessageRoom.cache_chat[chat_code] = []


                if len(messagesToInsert) > 0:
                    db.insertDataInTablePacket("(chat_id, message, sender_nick, date, WasSeen)", messagesToInsert)

                if len(messagesToUpdate) > 0:
                    db.packetUpdate("WasSeen", messagesToUpdate)
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

def receive(server_socket):
    while True:
        readable, _, _ = select.select([server_socket], [], [], 2)
        # Accept Connection
        for s in readable:
            if s is server_socket:
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
    PORT = 55558
    server_msg = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_msg.bind((HOST, PORT))
    server_msg.listen()
    clients = {}
    db_prefr = db_handler("26.181.96.20", "Dmitry", "gfggfggfg3D-", "zcord", "friends_adding")
    pre_fr_add = db_prefr.getDataFromTableColumn("id, chat_id, sender_nick, friend_nick, message, date, WasSeen")
    if len(pre_fr_add) != 0:
        for l in pre_fr_add:
            chat_id = str(l[1])
            cachedMessage = {"id": l[0], "chat_id": l[1], "message": l[4], "sender_nick": l[2], "date": l[5], "WasSeen": l[6]}
            if chat_id in MessageRoom.cache_chat.keys():
                MessageRoom.cache_chat[chat_id].append(cachedMessage)
            else:
                MessageRoom.cache_chat[chat_id] = [cachedMessage]
    receive(server_msg)
