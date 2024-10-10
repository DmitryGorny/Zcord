import socket
import pyaudio

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65128  # The port used by the server

FORMAT = pyaudio.paInt16  # Формат звука
CHANNELS = 1        # Количество каналов (1 для моно)
RATE = 44100        # Частота дискретизации

p = pyaudio.PyAudio()

client = socket.socket()
hostname = socket.gethostname()  # В документации сказано если использовать в коннект имя хоста то будет непредсказуемость

client.connect((HOST, PORT))

stream = p.open(format=FORMAT, channels=CHANNELS,
                 rate=RATE, input=True,
                 frames_per_buffer=1024)

print("Начата передача аудио...")

try:
    while True:
        data = stream.read(1024)
        client.sendall(data)  # Отправляем данные на сервер
except KeyboardInterrupt:
    print("Передача завершена.")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
    client.close()

client.close()
