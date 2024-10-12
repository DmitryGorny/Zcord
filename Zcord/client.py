import socket
import pyaudio


class VoiceConnection(object):
    def __init__(self):
        pass

    def sender(self):
        data_to_send = stream_input.read(1024)
        client.sendall(data_to_send)  # Отправляем данные на сервер

    def getter(self):
        data_to_read, address = client.recvfrom(CHUNK)  # Получаем данные с сервера
        stream_output.write(data_to_read)


if __name__ == "__main__":
    con = VoiceConnection()

    HOST = "26.36.124.241"  # The server's hostname or IP address
    PORT = 65128  # The port used by the server

    FORMAT = pyaudio.paInt16  # Формат звука
    CHANNELS = 1        # Количество каналов (1 для моно)
    RATE = 44100        # Частота дискретизации
    CHUNK = 4096

    p = pyaudio.PyAudio()

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    hostname = socket.gethostname()  # В документации сказано если использовать в коннект имя хоста то будет непредсказуемость

    client.connect((HOST, PORT))

    stream_input = p.open(format=FORMAT,
                          channels=CHANNELS,
                          rate=RATE,
                          input=True,
                          frames_per_buffer=1024)

    stream_output = p.open(format=FORMAT,
                           channels=CHANNELS,
                           rate=RATE,
                           output=True)

    print("Начата передача аудио..., для завершения ctrl + c")
    con.sender()
    try:
        while True:
            con.sender()
            con.getter()

    except KeyboardInterrupt:
        print("Передача завершена.")
    finally:
        stream_input.stop_stream()
        stream_input.close()
        stream_output.stop_stream()
        stream_output.close()
        p.terminate()
        client.close()

