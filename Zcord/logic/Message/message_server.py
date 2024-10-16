import socket
import threading
from datetime import datetime
import json


class MessageRoom(object):
    def __init__(self, server_msg):
        self.server_msg = server_msg
        self.cache_chat = {"chat_id": {
            1: [],
            2: []
            }
        }
        self.nicknames_in_chats = {
            1: [],
            2: []
        }
        self.f = open('cache_chat.json', 'w')

    def broadcast(self, msg):
        chat_code = msg[0]
        nickname = msg[1]
        message = msg[2]
        for client in self.nicknames_in_chats[chat_code]:
            clients[client].send(f"{nickname}: {message}".encode('utf-8'))

    def handle(self, client, nickname):
        while True:
            try:
                # Broadcasting Messages
                msg = client.recv(1024)
                msg = msg.decode('utf-8').split(", ")
                chat_code = int(msg[0])
                nickname = msg[1]
                message = msg[2]
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

                self.cache_chat["chat_id"][chat_code].append(message)

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
                #self.broadcast(f"Пользователь {nickname} вышел!".encode('utf-8'))
                print(f"{nickname} left!")
                #if len(nicknames) == 0:
                    #for i in self.cache_chat:
                      #  json.dump(self.cache_chat, self.f)
                   # self.f.close()
                #break

    def receive(self):
        while True:
            # Accept Connection
            client, address = server_msg.accept()
            print(f"Connected to {address}")

            # Request And Store Nickname
            client.send('NICK'.encode('utf-8'))
            nickname = client.recv(1024).decode('utf-8')
            clients[nickname] = client

            # Print And Broadcast Nickname
            print(f"Nickname is {nickname}")
            #self.broadcast(f"Пользователь {nickname} подключился!".encode('utf-8'))
            client.send('Подключено к серверу'.encode('utf-8'))

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

    msg_obj = MessageRoom(server_msg)

    msg_obj.receive()
