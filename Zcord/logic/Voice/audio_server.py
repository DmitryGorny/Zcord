import socket
import asyncio
import pyaudio


class Client:
    def __init__(self, address):
        self.address = address

    def return_address(self):
        return self.address


class VoiceServer:
    clients = {}  # Словарь для хранения активных клиентов

    def __init__(self, server_ip, server_port):
        # 1 - порт инициализации сервера, 2 - ip инициализации сервера
        self.server_ip = server_ip  # Адрес сервера
        self.server_port = server_port  # Port to listen on (non-privileged ports are > 1023)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.CHUNK = 1440
        self.server.bind((self.server_ip, self.server_port))
        print(f"Сервер запущен")
        self.stream_output = pyaudio.PyAudio().open(format=pyaudio.paInt16,
                                         channels=1,
                                         rate=48000,
                                         output=True)

    async def read_request(self):
        while True:
            try:
                data, address = self.server.recvfrom(4096)
                header = data[0:1]
                if header == b'2':  # обычный кадр звука с микрофона
                    data = data[1:]
                    self.broadcast(data, address)
                    #self.stream_output.write(data)  # проверка на сервере не трогать
                elif header == b'1':  # подключение юзера к серверу
                    if len(self.clients) != 0:
                        self.active_users_icon(b'222', address)
                    print(f"Пользователь с ip: {address} подключен")
                    self.clients[address] = Client(address)
                    self.broadcast(b'111', address)
                elif header == b'0':  # отключение юзера от сервера
                    print(f"{address} отключен")
                    self.broadcast(b'000', address)
                    del self.clients[address]
            except Exception as e:
                print(f"Error reading request: {e}")
                break

    def broadcast(self, data: bytes, sender_address: tuple):
        for client_address in VoiceServer.clients:
            if client_address != sender_address:  # Не отправляем данные отправителю
                try:
                    self.server.sendto(data, client_address)
                except Exception as e:
                    print(f"Error sending data to {client_address}: {e}")

    def active_users_icon(self, data: bytes, sender_address: tuple):
        try:
            self.server.sendto(data, sender_address)
        except Exception as e:
            print(f"Error sending data to {sender_address}: {e}")

    def close_server(self):
        print("Server ends")
        self.server.close()


async def main():
    server = VoiceServer("26.36.124.241", 65128)
    task1 = asyncio.create_task(server.read_request())
    task2 = asyncio.create_task(server.read_request())
    await asyncio.gather(task1, task2)


if __name__ == "__main__":
    # Позже необходимо добавить работу с классом Client, а именно из него брать все апйишники и порты
    asyncio.run(main())
