import socket
import pyaudio
import multiprocessing as mp


class VoiceConnection(object):
    def __init__(self):
        pass

    def sender(self):
        while True:
            print("send")
            data_to_send = stream_input.read(1024)
            speak.sendall(data_to_send)  # Отправляем данные на сервер
            print(123)


if __name__ == "__main__":
    con = VoiceConnection()

    HOST = "26.36.124.241"  # The server's hostname or IP address
    CLIENT = "26.36.124.241"

    PORT_TO_SPEAK = 65128  # The port used by the server
    PORT_TO_LISTEN = 22223

    FORMAT = pyaudio.paInt16  # Формат звука
    CHANNELS = 1        # Количество каналов (1 для моно)
    RATE = 44100        # Частота дискретизации
    CHUNK = 4096

    p = pyaudio.PyAudio()

    speak = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #listen = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    speak.connect((HOST, PORT_TO_SPEAK))
    #listen.bind((CLIENT, PORT_TO_LISTEN))

    stream_input = p.open(format=FORMAT,
                          channels=CHANNELS,
                          rate=RATE,
                          input=True,
                          frames_per_buffer=1024)

    print("Начата передача аудио..., для завершения ctrl + c")
    con.sender()
    while True:
        try:
            con.sender()
        except BaseException:
            pass



