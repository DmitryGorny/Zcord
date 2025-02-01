import socket
import asyncio


class Client:
    def __init__(self, address):
        self.address = address

    def return_address(self):
        return self.address


class VoiceServer(object):
    def __init__(self, server_ip, server_port):
        # 1 - порт инициализации сервера, 2 - ip инициализации сервера
        self.server_ip = server_ip  # Адрес сервера
        self.server_port = server_port  # Port to listen on (non-privileged ports are > 1023)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.CHUNK = 1440
        self.server.bind((self.server_ip, self.server_port))
        print(f"Сервер запущен")
        self.clients = {}  # Словарь для хранения активных клиентов

    async def read_request(self):
        while True:
            try:
                data, address = await asyncio.get_event_loop().sock_recvfrom(self.server, self.CHUNK)
                header = data[0:1]
                if header == b'2':
                    data = data[1:]
                    self.broadcast(data, address)
                elif header == b'1':
                    print(f"Пользователь с ip: {address} подключен")
                    self.clients[address] = Client(address)
                elif header == b'0':
                    print(f"{address} disconnected!")
                    del self.clients[address]
            except Exception as e:
                print(f"Error reading request: {e}")
                break

    def broadcast(self, data: bytes, sender_address: tuple):
        for client_address in self.clients:
            if client_address != sender_address:  # Не отправляем данные отправителю
                try:
                    self.server.sendto(data, client_address)
                except Exception as e:
                    print(f"Error sending data to {client_address}: {e}")

    def close_server(self):
        print("Server ends")
        self.server.close()


async def main():
    server = VoiceServer("26.36.124.241", 65128)
    await server.read_request()


if __name__ == "__main__":
    # Позже необходимо добавить работу с классом Client, а именно из него брать все апйишники и порты
    asyncio.run(main())
