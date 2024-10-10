import socket
import pyaudio
import wave
import sys
import time


def callback(in_data, frame_count, time_info, status):
    return (in_data, pyaudio.paContinue)


HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65128  # Port to listen on (non-privileged ports are > 1023)

p = pyaudio.PyAudio()
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((HOST, PORT))
server.listen()
print("Server starts")

conn, addr = server.accept()

print("connection: ", conn)
print("client address: ", addr)


with wave.open("output.wav", "wb") as f:  # Открываем файл для записи в бинарном режиме
    f.setnchannels(CHANNELS)
    f.setsampwidth(2)  # 2 байта для paInt16
    f.setframerate(RATE)

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    output=True,
                    stream_callback=callback)

    while True:
        data = conn.recv(1024)
        if not data:
            break
        callback(data, RATE, 5, "on")
        f.writeframes(data)
    print("Получены данные")

conn.close()

print("Server ends")
server.close()
