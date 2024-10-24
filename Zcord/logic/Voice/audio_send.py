import socket
import pyaudio


class VoiceConnection(object):
    def __init__(self):
        pass

    def sender(self):
        data_to_send = stream_input.read(1024)
        speak.sendall(data_to_send)  # Отправляем данные на сервер


if __name__ == "__main__":
    con = VoiceConnection()

    HOST = "26.36.124.241"  # IP адрес сервера для подключения

    PORT_TO_SPEAK = 54325  # Порт, используемый сервером

    FORMAT = pyaudio.paInt16  # Формат звука
    CHANNELS = 1        # Количество каналов (1 для моно)
    RATE = 44100        # Частота дискретизации
    CHUNK = 4096

    p = pyaudio.PyAudio()

    speak = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    speak.connect((HOST, PORT_TO_SPEAK))

    stream_input = p.open(format=FORMAT,
                          channels=CHANNELS,
                          rate=RATE,
                          input=True,
                          frames_per_buffer=1024)

    print("Начата передача аудио, для завершения ctrl + c")
    con.sender()
    try:
        while True:
            con.sender()
    except KeyboardInterrupt:
        print("Передача аудио закончена или прервана")
    finally:
        p.close(stream_input)
        stream_input.close()
        speak.close()
