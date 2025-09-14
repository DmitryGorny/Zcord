import socket
import threading
import pyaudio
import random


class VoiceServer:
    clients_udp = []  # Словарь для хранения активных клиентов
    clients_tcp = []

    def __init__(self, server_ip, CLIENT_UDP_PORT, client):
        self.HOST = server_ip  # Адрес сервера
        self.CLIENT_UDP_PORT = CLIENT_UDP_PORT  # Port to listen on (non-privileged ports are > 1023)

        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.SERVER_UDP_PORT = self.find_free_port()
        self.server.bind((self.HOST, self.SERVER_UDP_PORT))
        client.send(b'SERVER_UDP' + str(self.SERVER_UDP_PORT).encode('utf-8'))

        self.client_udp_address = (client.getpeername()[0], self.CLIENT_UDP_PORT)

        VoiceServer.clients_udp.append(self.client_udp_address)
        VoiceServer.clients_tcp.append(client)
        self.is_running = True
        self.CHUNK = 1440
        print(f"Сервер запущен")
        self.stream_output = pyaudio.PyAudio().open(format=pyaudio.paInt16,
                                         channels=1,
                                         rate=48000,
                                         output=True)

    def find_free_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', 0))  # 0 означает, что ОС выберет свободный порт
            s.listen(1)
            port = s.getsockname()[1]
            return port

    def read_request(self):
        while self.is_running:
            try:
                data, address = self.server.recvfrom(4096)  # обычный кадр звука с микрофона
                self.broadcast(data, address)
                #self.stream_output.write(data)  # проверка на сервере не трогать
            except OSError as e:
                if not self.is_running:
                    print("Сокет закрыт, поток завершается.")
                    break
                else:
                    print(f"read_request: Ошибка чтения: {e}")
                    break
            except Exception as e:
                print(f"read_request: Error reading request: {e}")
                print("Если сообщение здесь про то что сокет закрыт то всё норм")
                break

    def broadcast(self, data: bytes, sender_address: tuple):
        for client_address in VoiceServer.clients_udp:
            if client_address != sender_address:  # Не отправляем данные отправителю
                try:
                    self.server.sendto(data, client_address)
                except Exception as e:
                    print(f"broadcast: Error sending data to {client_address}: {e}")
                    break

    def send_service_tcp(self, data: bytes, client=None):
        if data == b'000':
            for client_in_server_now in VoiceServer.clients_tcp:
                client_in_server_now.send(b'000')
        else:
            for client_in_server_now in VoiceServer.clients_tcp:
                if client_in_server_now != client:
                    client_in_server_now.send(data)

    def get_service_tcp(self, client):
        while self.is_running:
            try:
                data = client.recv(4096)
                if data == b'EXI':  # отключение юзера от сервера
                    print(f"{VoiceServer.clients_tcp[VoiceServer.clients_tcp.index(client)].getpeername()} отключен")
                    self.send_service_tcp(b'000')
                    client.send(b'EXI')
                    del VoiceServer.clients_udp[VoiceServer.clients_udp.index(self.client_udp_address)]
                    del VoiceServer.clients_tcp[VoiceServer.clients_tcp.index(client)]
                    self.close_server(client)
                    break
                elif data == b'MicMute':
                    self.send_service_tcp(b'MicMute', client)
                elif data == b'MicUnMute':
                    self.send_service_tcp(b'MicUnMute', client)
                elif data == b'HeadMute':
                    self.send_service_tcp(b'HeadMute', client)
                elif data == b'HeadUnMute':
                    self.send_service_tcp(b'HeadUnMute', client)
            except Exception as e:
                print(f"get_service_tcp: Error reading request: {e}")
                print(f"{VoiceServer.clients_tcp[VoiceServer.clients_tcp.index(client)].getpeername()} отключен")
                del VoiceServer.clients_udp[VoiceServer.clients_udp.index(self.client_udp_address)]
                del VoiceServer.clients_tcp[VoiceServer.clients_tcp.index(client)]
                self.close_server(client)
                break

    def close_server(self, client):
        print("Server ends")
        self.is_running = False
        self.server.shutdown(socket.SHUT_RDWR)
        self.server.close()
        client.close()


def main():
    while True:
        client, address = server_tcp.accept()
        enter = client.recv(4096)
        print(f"Пользователь с tcp ip: {address} подключен {enter}")
        client.send(b'ENT')
        CLIENT_UDP_PORT = client.recv(4096).decode('utf-8')
        server = VoiceServer("26.36.124.241", int(CLIENT_UDP_PORT), client)
        if len(VoiceServer.clients_tcp) > 1:
            for client_in_server_now in VoiceServer.clients_tcp:
                client_in_server_now.send(b'111')
        thread = threading.Thread(target=server.read_request, args=())
        thread1 = threading.Thread(target=server.get_service_tcp, args=(client, ))
        thread.start()
        thread1.start()


if __name__ == "__main__":
    HOST = "26.36.124.241"
    PORT = 65127
    server_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_tcp.bind((HOST, PORT))
    server_tcp.listen()
    main()
