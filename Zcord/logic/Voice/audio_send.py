import socket
import pyaudio
import threading
from multiprocessing import Process


class VoiceConnection(object):
    def __init__(self, udp, tcp, stream_input):
        self.speak = udp
        self.tcp = tcp
        self.CHUNK = 4096
        self.stream_input = stream_input

    def sender(self):
        while True:
            print(1)
            data_to_send = self.stream_input.read(1024)
            print(data_to_send)
            self.speak.sendall(data_to_send)  # Отправляем данные на сервер

    def send_tcp(self, nickname):
        message = self.tcp.recv(1024)
        if message.decode('utf-8') == "NICK":
            self.tcp.sendall(f"{nickname}".encode('utf-8'))
        message = self.tcp.recv(1024)
        print(message.decode('utf-8'))
        self.tcp.close()


if __name__ == "__main__":
    HOST = "26.36.124.241"  # IP адрес сервера для подключения
    CLIENT = "26.36.124.241"

    PORT_TO_UDP = 55534  # Порт, используемый сервером UDP
    PORT_TO_TCP = 55533  # Порт, используемый сервером TCP

    FORMAT = pyaudio.paInt16  # Формат звука
    CHANNELS = 1        # Количество каналов (1 для моно)
    RATE = 44100        # Частота дискретизации

    p = pyaudio.PyAudio()

    speak = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    speak.connect((HOST, PORT_TO_UDP))

    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.connect((HOST, PORT_TO_TCP))

    stream_input = p.open(format=FORMAT,
                          channels=CHANNELS,
                          rate=RATE,
                          input=True,
                          frames_per_buffer=1024)

    con = VoiceConnection(speak, tcp, stream_input)

    nickname = input("Введите свой ник: ")
    con.send_tcp(nickname)

    print("Начата передача аудио, для завершения ctrl + c")
    try:
        con.sender()
        #process = threading.Thread(target=con.sender)
        #process.start()

        #process1 = threading.Thread(target=con.getter)
        #process1.start()
    except KeyboardInterrupt:
        print("Передача аудио закончена или прервана")
    finally:
        p.close(stream_input)
        stream_input.close()
        speak.close()
