import socket
import pyaudio


def callback(in_data, frame_count, time_info, status):
    return (in_data, pyaudio.paContinue)


def sender():
    data_to_send = stream_input.read(1024)
    client.sendall(data_to_send)  # Отправляем данные на сервер


def getter():
    data_to_read = client.recvfrom(4096)  # Получаем данные с сервера
    callback(data_to_read, RATE, 5, "on")


if __name__ == "__main__":
    HOST = "127.0.0.1"  # The server's hostname or IP address
    PORT = 65128  # The port used by the server

    FORMAT = pyaudio.paInt16  # Формат звука
    CHANNELS = 1        # Количество каналов (1 для моно)
    RATE = 44100        # Частота дискретизации

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
                           input=True,
                           output=True,
                           stream_callback=callback)

    print("Начата передача аудио..., для завершения ctrl + c")
    sender()
    try:
        while True:
            sender()
            getter()

    except KeyboardInterrupt:
        print("Передача завершена.")
    finally:
        stream_input.stop_stream()
        stream_input.close()
        stream_output.stop_stream()
        stream_output.close()
        p.terminate()
        client.close()

