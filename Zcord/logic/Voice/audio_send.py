import socket
import sys
import threading
import pyaudio
import numpy as np


class VoiceConnection:
    volume = 1.0

    def __init__(self):
        pass

    @staticmethod
    def sender():
        while True:
            try:
                data_to_send = stream_input.read(CHUNK)
                #stream_output.write(VoiceConnection.adjust_volume(data_to_send, VoiceConnection.volume))
                speak.sendall(b'1' + VoiceConnection.adjust_volume(data_to_send, VoiceConnection.volume))  # Отправляем данные на сервер
            except KeyboardInterrupt:
                print("Передача аудио закончена или прервана")
                speak.sendall(b'0')
                sys.exit()

    @staticmethod
    def first_packet():
        data_to_send = stream_input.read(CHUNK)
        speak.sendall(b'1' + data_to_send)  # Отправляем данные на сервер

    @staticmethod
    # Функция для изменения громкости
    def adjust_volume(data, volume):
        # Преобразуем данные в массив numpy
        samples = np.frombuffer(data, dtype=np.int16)
        # Масштабируем сэмплы
        samples = (samples * volume).astype(np.int16)
        # Возвращаем данные в формате bytes
        return samples.tobytes()

    @staticmethod
    def volume_change(volume):
        VoiceConnection.volume = volume


if __name__ == "__main__":
    con = VoiceConnection()

    HOST = "26.36.124.241"  # IP адрес сервера для подключения

    PORT_TO_SPEAK = 54325  # Порт, используемый сервером

    FORMAT = pyaudio.paInt16  # Формат звука
    CHANNELS = 1        # Количество каналов (1 для моно)
    RATE = 44100        # Частота дискретизации
    CHUNK = 1024

    p = pyaudio.PyAudio()

    speak = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    speak.connect((HOST, PORT_TO_SPEAK))

    stream_input = p.open(format=FORMAT,
                          channels=CHANNELS,
                          rate=RATE,
                          input=True,
                          frames_per_buffer=CHUNK)

    stream_output = p.open(format=FORMAT,
                           channels=CHANNELS,
                           rate=RATE,
                           output=True)

    print("Начата передача аудио, для завершения ctrl + c")
    con.first_packet()
    thread = threading.Thread(target=con.sender, args=())
    thread.start()

    while True:  # Воображаемая параллельная работа QT
        new_volume = input("Введите новую громкость (например, 0.5 или 2.0): ")
        con.volume_change(float(new_volume))
