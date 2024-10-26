import socket
from multiprocessing import Pool, cpu_count, Process
from multiprocessing.pool import ThreadPool


class Client(object):
    def __init__(self, address):
        self.address = address

    def return_address(self):
        return self.address


class VoiceServer(object):
    def __init__(self, server_udp, server_tcp):
        self.server_udp = server_udp
        self.server_tcp = server_tcp
        self.CHUNK = 4096
        self.clients = {}
        print(f"Listening Server starts")

    def read_request(self, client, nickname):
        while True:
            #try:
                data, address = self.server_udp.recvfrom(self.CHUNK)
                if not data:
                    break
                print(self.clients)
                with Pool(processes=cpu_count() * len(self.clients)) as pool:
                    pool.map(self.broadcast, [(i, data) for i in self.clients.values() if i != address[0]])
            #except ConnectionResetError:
                # Removing And Closing Clients
                #self.broadcast((j, nickname, f"Пользователь {nickname} вышел!"))
                #self.clients.pop(nickname)
               # client.close()
                #print(f"{nickname} left!")
                #break

    def broadcast(self, client):
        print(client)
        self.server_udp.sendto(client[1], (client[0], 55536))

    def receive(self):
        while True:
            # Accept Connection
            client, address = self.server_tcp.accept()
            print(f"Connected to {address}")

            # Request And Store Nickname
            client.send('NICK'.encode('utf-8'))
            nickname = client.recv(1024).decode('utf-8')
            self.clients[nickname] = address[0]

            print(f"Nickname is {nickname}")

            client.send('Подключено к серверу'.encode('utf-8'))

            # Start Handling Thread For Client
            process = Process(target=voice_obj.read_request, args=(client, nickname,))
            process.start()


if __name__ == "__main__":
    HOST = "26.36.124.241"
    UDP_PORT = 55534
    TCP_PORT = 55533
    server_voice_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_voice_udp.bind((HOST, UDP_PORT))

    server_voice_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_voice_tcp.bind((HOST, TCP_PORT))
    server_voice_tcp.listen()

    voice_obj = VoiceServer(server_voice_udp, server_voice_tcp)

    voice_obj.receive()
    # Позже необходимо добавить работу с классом Client, а именно из него брать все апйишники и порты
