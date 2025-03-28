import json
import socket
import threading
from datetime import datetime
import msgspec
import copy
from logic.db_handler.db_handler import db_handler
import select
import re


class MessageRoom(object):
    nicknames_in_chats = {}
    cache_chat = {}
    unseenMessages = {}


    @staticmethod
    def set_nicknames_in_chats(arr):
        MessageRoom.nicknames_in_chats = {**arr, **MessageRoom.nicknames_in_chats}

    @staticmethod
    def set_cache_chat(arr):
        MessageRoom.cache_chat = {**arr, **MessageRoom.cache_chat}

    def __init__(self):
        pass

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
                clients[client].socket.send(ret)
            except KeyError:
                continue


    @staticmethod
    def decode_multiple_json_objects(data):
        json_pattern = re.compile(r"\{.*?\}")
        decoded_objects = []
        for match in json_pattern.finditer(data):
            decoded_objects.append(json.loads(match.group()))
        return decoded_objects

    @staticmethod
    def handle(client):
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
                except json.JSONDecodeError:
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

            except ConnectionResetError:
                clients.pop(nickname)
                client.close()
                print(f"{nickname} left!")
                break

    @staticmethod
    def handle_server(main_server_socket):
        while True:
            print(MessageRoom.nicknames_in_chats)
            buffer = ''
            try:
                server_msg = main_server_socket.recv(1024)
                server_msg = server_msg.decode('utf-8')

                if server_msg == "DISCOVER":
                    main_server_socket.send(b'MESSAGE-SERVER')
                    continue

                if "USER-INFO" in server_msg:
                    MessageRoom.copyCacheChat(json.loads(server_msg.split("&-&")[2]))
                    continue

                if "__change_chat__" in server_msg:
                    server_msg = server_msg.split("&-&")

                    try: #Я боюсь какого-нибудь неотловленного рассинхрона nicknames_in_chats здесь и с сервером, поэтому будем это отлавливать
                        if server_msg[2] != server_msg[3]:
                            MessageRoom.nicknames_in_chats[server_msg[2]].remove(server_msg[1])
                        MessageRoom.nicknames_in_chats[server_msg[3]].append(server_msg[1])
                    except ValueError:
                        print(1111111) #Дописать запрос на сервер для синхронизации
                    continue
            except ConnectionResetError:
                print("Сервер сдох")
                break


def recieve_service_comands(main_server_socket):
    thread = threading.Thread(target=MessageRoom.handle_server, args=(main_server_socket,))
    thread.start()


def receive(server_socket):
    while True:
        readable, _, _ = select.select([server_socket], [], [], 2)
        # Accept Connection
        for s in readable:
            client, address = server_msg.accept()
            print(f"Connected to {address}")
            if s is client:

                m = MessageRoom()
                thread = threading.Thread(target=MessageRoom.handle, args=(client,))
                thread.start()


if __name__ == "__main__":
    HOST = "26.181.96.20"
    PORT = 55557
    server_msg = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_msg.bind((HOST, PORT))
    server_msg.listen()
    clients = {}

    main_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    main_server_socket.connect((HOST, 55569))

    recieve_service_comands(main_server_socket)
    receive(main_server_socket)
