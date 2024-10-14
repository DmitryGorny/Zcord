import socket
import threading


class MessageServer(object):
    def __init__(self, server_msg):
        self.server_msg = server_msg

    def broadcast(self, message):
        for client in clients:
            client.send(message)

    def handle(self, client):
        while True:
            try:
                # Broadcasting Messages
                message = client.recv(1024)
                self.broadcast(message)
            except ConnectionResetError:
                # Removing And Closing Clients
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                self.broadcast(f"{nickname} left!".encode('utf-8'))
                print(f"{nickname} left!")
                nicknames.remove(nickname)
                break

    def receive(self):
        while True:
            # Accept Connection
            client, address = server_msg.accept()
            print(f"Connected to {address}")

            # Request And Store Nickname
            client.send('NICK'.encode('utf-8'))
            nickname = client.recv(1024).decode('utf-8')
            nicknames.append(nickname)
            clients.append(client)

            # Print And Broadcast Nickname
            print(f"Nickname is {nickname}")
            msg_obj.broadcast(f"{nickname} joined!".encode('utf-8'))
            client.send('Connected to server!'.encode('utf-8'))

            # Start Handling Thread For Client
            thread = threading.Thread(target=msg_obj.handle, args=(client,))
            thread.start()


if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 55555
    server_msg = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_msg.bind((HOST, PORT))
    server_msg.listen()

    clients = []
    nicknames = []

    msg_obj = MessageServer(server_msg)

    msg_obj.receive()
