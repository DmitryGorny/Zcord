import socket
import pyaudio
import wave
import asyncio
import threading


def callback(in_data, frame_count, time_info, status):
    return (in_data, pyaudio.paContinue)


class Client(object):
    def __init__(self, address):
        self.address = address

    def return_address(self):
        return self.address


class Server(object):
    def __init__(self):
        self.HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
        self.PORT = 65128  # Port to listen on (non-privileged ports are > 1023)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("Server starts")

        #self.f = wave.open("output.wav", "wb")  # Открываем файл для записи в бинарном режиме

    def read_request(self):
        self.server.bind((self.HOST, self.PORT))
        self.data, self.address = self.server.recvfrom(4096)
        print(f"Connected to: {self.address}")
        Client(address=self.address)

        #self.f.setnchannels(CHANNELS)
        #self.f.setsampwidth(2)  # 2 байта для paInt16
        #self.f.setframerate(RATE)

        while True:
            self.data, self.address = self.server.recvfrom(4096)
            if not self.data:
                break

            #self.f.writeframes(data)

            client_thread = threading.Thread(target=self.send_request(), args=(self.data, self.address, self.server))
            client_thread.start()
            #self.send_request()

    def send_request(self):
        self.server.sendto(self.data, self.address)

    def close_server(self):
        print("Server ends")
        self.f.close()
        self.server.close()


if __name__ == "__main__":
    server_obj = Server()
    server_obj.read_request()
