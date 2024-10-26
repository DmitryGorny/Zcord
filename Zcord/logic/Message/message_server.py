import socket
import threading
from datetime import datetime
import msgspec


class MessageRoom(object):
    def __init__(self):
        self.cache_chat = {"chat_id": {
            1: [],
            2: []
            }
        }
        self.nicknames_in_chats = {
            1: [],
            2: []
        }

    @staticmethod
    def serialize(x):
        ser = msgspec.json.encode(x)
        return ser

    def broadcast(self, msg):
        chat_code = msg[0]
        nickname = msg[1]
        message = msg[2]
        for client in self.nicknames_in_chats[chat_code]:
            ret = b'0' + f"{nickname}: {message}".encode('utf-8')
            clients[client].send(ret)

    def handle(self, client, nickname):
        while True:
            try:
                # Broadcasting Messages
                msg = client.recv(1024)
                msg = msg.decode('utf-8').split(", ")
                chat_code = int(msg[0])
                nickname = msg[1]
                message = msg[2]
                if message == "change chat":
                    client.send(b'1' + MessageRoom.serialize(self.cache_chat["chat_id"][chat_code]))
                    continue
                if nickname not in self.nicknames_in_chats[chat_code]:  # ВОТ ЗДЕСЬ
                    self.nicknames_in_chats[chat_code].append(nickname)
                    try:
                        if chat_code != old_chat_cod:
                            del self.nicknames_in_chats[old_chat_cod][self.nicknames_in_chats[old_chat_cod].index(nickname)]
                    except UnboundLocalError:
                        pass
                else:
                    old_chat_cod = int(chat_code)
                date_now = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                date_now = date_now
                self.broadcast((chat_code, date_now + nickname, message))

                self.cache_chat["chat_id"][chat_code].append(f"{date_now + nickname}: {message}")

                if len(self.cache_chat["chat_id"][chat_code]) >= 20:
                    del self.cache_chat["chat_id"][chat_code][0]

            except ConnectionResetError:
                # Removing And Closing Clients
                for j in self.nicknames_in_chats:
                    if nickname in self.nicknames_in_chats[j]:
                        self.nicknames_in_chats[j].remove(nickname)
                        self.broadcast((j, nickname, f"Пользователь {nickname} вышел!"))
                clients.pop(nickname)
                client.close()
                print(f"{nickname} left!")
                break

    def receive(self):
        while True:
            # Accept Connection
            client, address = server_msg.accept()
            print(f"Connected to {address}")

            # Request And Store Nickname
            client.send(b'0' + 'NICK'.encode('utf-8'))
            nickname = client.recv(1024).decode('utf-8')
            clients[nickname] = client

            # Print And Broadcast Nickname
            print(f"Nickname is {nickname}")

            client.send(b'0' + 'Подключено к серверу'.encode('utf-8'))

            # Start Handling Thread For Client
            thread = threading.Thread(target=msg_obj.handle, args=(client, nickname,))
            thread.start()


if __name__ == "__main__":
    HOST = "26.36.124.241"
    PORT = 55555
    server_msg = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_msg.bind((HOST, PORT))
    server_msg.listen()

    clients = {}

    msg_obj = MessageRoom()

    msg_obj.receive()
