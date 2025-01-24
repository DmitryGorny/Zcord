import socket
import sys
import threading
import pyaudio
import numpy as np


class VoiceConnection:
    output_volume = 1.0

    def __init__(self):
        pass

    @staticmethod
    def getter():
        while True:
            try:
                data_to_read, address = listen.recvfrom(CHUNK)  # Получаем данные с сервера

                stream_output.write(VoiceConnection.control_output_volume(data_to_read, VoiceConnection.output_volume))
            except KeyboardInterrupt:
                print("Приём аудио завершен или прерван")
                sys.exit()

    @staticmethod
    # Функция для изменения громкости
    def control_output_volume(data, volume):
        # Преобразуем данные в массив numpy
        samples = np.frombuffer(data, dtype=np.int16)
        # Масштабируем сэмплы
        samples = (samples * volume).astype(np.int16)
        # Возвращаем данные в формате bytes
        return samples.tobytes()

    @staticmethod
    def change_output_volume(volume):
        VoiceConnection.output_volume = volume


if __name__ == "__main__":
    con = VoiceConnection()

    CLIENT = "26.36.124.241"  # IP адрес свой (клиента)
    PORT_TO_LISTEN = 22223  # Порт, используемый клиентом

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

    thread = threading.Thread(target=con.getter, args=())
    thread.start()

    while True:  # Воображаемая параллельная работа QT
        new_output_volume = input("Введите новую громкость (например, 0.5 или 2.0): ")
        con.change_output_volume(float(new_output_volume))
