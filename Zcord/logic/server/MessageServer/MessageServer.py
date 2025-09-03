import json
import socket
import threading
from datetime import datetime
from typing import Dict, List, Any, Union

import msgspec
import copy
import select

from logic.server.MessageServer.Cache.Cache import CacheManager
from logic.server.StrategiesForMessageServer.StratsForServer import ChooseStrategy

class MessageRoom(object): #TODO: Когда-нибудь переделать
    nicknames_in_chats:  Dict[str, List[str]] = {}
    cache_chat: CacheManager = CacheManager()
    unseenMessages = {}
    clients: dict[str, socket.socket] = {}
    _strat_choose = ChooseStrategy()

    @staticmethod
    def set_nicknames_in_chats(arr):
        MessageRoom.nicknames_in_chats = {**arr, **MessageRoom.nicknames_in_chats}

    def __init__(self):
        pass

    @staticmethod
    def copyCacheChat(chat_id):
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

        messaghe_to_send = {
            "type": "CHAT-MESSAGE",
            "chat": msg[0],
            "message": msg[1],
            "created_at": msg[2],
            "sender": msg[3],
            "was_seen": msg[4]
        }

        for client in MessageRoom.nicknames_in_chats[chat_code]:
            try:
                MessageRoom.clients[client].send(json.dumps(messaghe_to_send).encode('utf-8'))
            except KeyError:
                continue

    @staticmethod
    def send_cache(cache_list: list[dict[str, str]], nickname_to_recv: str):
        message = {
            "type": "RECEIVE-CACHE",
            "cache": cache_list
        }
        MessageRoom.clients[nickname_to_recv].send(MessageRoom.serialize(message))


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
                    strategy = MessageRoom._strat_choose.get_strategy(msg["type"], MessageRoom)
                    try:
                        strategy.execute(msg)
                    except AttributeError as e:
                        print(e)
            except ConnectionResetError:
                client.close()
                break
            except ConnectionAbortedError:
                client.close()
                break

    @staticmethod
    def handle_server(main_server_socket):
        while True:
            buffer = ''
            server_msg = main_server_socket.recv(1024)
            server_msg = server_msg.decode('utf-8')

            try:
                if server_msg == "DISCOVER":
                    main_server_socket.send(b'MESSAGE-SERVER')
                    continue

                buffer += server_msg
                try:
                    arr = MessageRoom.decode_multiple_json_objects(buffer)
                except json.JSONDecodeError:
                    continue

                for server_msg in arr:
                    type_msg = server_msg["type"]
                    strategy = MessageRoom._strat_choose.get_strategy(type_msg, MessageRoom)
                    try:
                        strategy.execute(server_msg)
                    except AttributeError as e:
                        print(e)
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
            client, address = server_socket.accept()
            print(f"Connected to {address}")

            m = MessageRoom()
            for key in MessageRoom.clients.keys():
                if not isinstance(MessageRoom.clients[key], str):
                    continue

                if MessageRoom.clients[key] == client.getpeername()[0]:
                    MessageRoom.clients[key] = client

            thread = threading.Thread(target=MessageRoom.handle, args=(client,))
            thread.start()



if __name__ == "__main__":
    HOST = "26.181.96.20"
    PORT = 55557
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    main_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    main_server_socket.connect((HOST, 55569))

    recieve_service_comands(main_server_socket)
    receive(server_socket)
