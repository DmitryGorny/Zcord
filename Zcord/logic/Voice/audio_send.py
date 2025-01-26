import socket
import sys
import threading
import pyaudio
import numpy as np
import noisereduce as nr


class VoiceConnection:
    volume = 1.0
    noise_profile = None

    def __init__(self):
        pass

    @staticmethod
    def record_noise_profile(duration):
        print(f"Записываем фоновый шум {duration} секунд... (не издавайте звуков)")

        frames = []
        total_chunks = int((RATE * duration) / CHUNK)

        for _ in range(total_chunks):
            data = stream_input.read(CHUNK)
            frames.append(data)

        # Объединяем все фреймы и конвертируем в формат float
        noise_data = np.frombuffer(b''.join(frames), dtype=np.int16)
        VoiceConnection.noise_profile = noise_data.astype(np.float32) / 32768.0

        print("Профиль шума успешно записан!")

    @staticmethod
    def sender():
        while True:
            try:
                data_to_send = stream_input.read(CHUNK)

                if VoiceConnection.noise_profile is not None:
                    # Конвертируем в формат для обработки
                    audio_data = np.frombuffer(data_to_send, dtype=np.int16)
                    audio_float = audio_data.astype(np.float32) / 32768.0

                    # Применяем шумоподавление
                    reduced = nr.reduce_noise(
                        y=audio_float,
                        y_noise=VoiceConnection.noise_profile,
                        sr=RATE,
                        stationary=True
                    )

                    # Конвертируем обратно в исходный формат
                    processed_data = (reduced * 32768).astype(np.int16)
                    data_to_send = processed_data.tobytes()

                stream_output.write(VoiceConnection.adjust_volume(data_to_send, VoiceConnection.volume))
                speak.sendall(b'1' + data_to_send)

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

        samples = (samples * volume).astype(np.int16)
        return samples.tobytes()

    @staticmethod
    def volume_change(volume):
        VoiceConnection.volume = volume


if __name__ == "__main__":
    con = VoiceConnection()

    HOST = "26.36.124.241"
    PORT_TO_SPEAK = 54325
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
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

    # Записываем фоновый шум
    con.record_noise_profile(5)

    print("Начата передача аудио, для завершения ctrl + c")
    con.first_packet()
    thread = threading.Thread(target=con.sender, args=())
    thread.start()

    while True:
        new_volume = input("Введите новую громкость (например, 0.5 или 2.0): ")
        con.volume_change(float(new_volume))
