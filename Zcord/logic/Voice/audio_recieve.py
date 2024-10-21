import socket
import pyaudio
import multiprocessing as mp


class VoiceConnection(object):
    def __init__(self):
        pass

    def getter(self):
        data_to_read, address = listen.recvfrom(CHUNK)  # Получаем данные с сервера
        stream_output.write(data_to_read)


if __name__ == "__main__":
    con = VoiceConnection()

    CLIENT = "26.181.96.20"  # IP адрес свой (клиента)
    PORT_TO_LISTEN = 22222  # Порт, используемый клиентом

    FORMAT = pyaudio.paInt16  # Формат звука
    CHANNELS = 1        # Количество каналов (1 для моно)
    RATE = 44100        # Частота дискретизации
    CHUNK = 4096

    p = pyaudio.PyAudio()

    listen = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    listen.bind((CLIENT, PORT_TO_LISTEN))

    stream_output = p.open(format=FORMAT,
                           channels=CHANNELS,
                           rate=RATE,
                           output=True)

    print("Начат приём аудио..., для завершения ctrl + c")
    data_to_read, address = listen.recvfrom(CHUNK)
    print(f"Connected to {address}")
    try:
        while True:
            con.getter()
    except KeyboardInterrupt:
        print("Приём аудио закончен или прерван")
    finally:
        p.close(stream_output)
        listen.close()
        stream_output.close()
