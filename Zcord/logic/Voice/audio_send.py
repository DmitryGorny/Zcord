import socket
import sys
import threading
import pyaudio
import numpy as np
import noisereduce as nr


class KalmanFilter:
    def __init__(self, initial_state, process_variance, measurement_variance):
        """
        Инициализация фильтра Калмана.

        :param initial_state: Начальное состояние (например, первый сэмпл).
        :param process_variance: Дисперсия шума процесса (Q).
        :param measurement_variance: Дисперсия шума измерений (R).
        """
        self.state = initial_state  # Текущее состояние
        self.process_variance = process_variance  # Q
        self.measurement_variance = measurement_variance  # R
        self.estimate_error = 1.0  # Начальная ошибка оценки (P)

    def update(self, measurement):
        """
        Обновление состояния фильтра Калмана на основе нового измерения.

        :param measurement: Новое измерение (текущий сэмпл).
        :return: Отфильтрованное значение.
        """
        # Предсказание
        predicted_state = self.state
        predicted_estimate_error = self.estimate_error + self.process_variance

        # Коррекция
        kalman_gain = predicted_estimate_error / (predicted_estimate_error + self.measurement_variance)
        self.state = predicted_state + kalman_gain * (measurement - predicted_state)
        self.estimate_error = (1 - kalman_gain) * predicted_estimate_error

        return self.state


class VoiceConnection:
    volume = 1.0

    def __init__(self):
        pass

    @staticmethod
    def sender():
        while True:
            try:
                data_to_send = stream_input.read(CHUNK)
                signal = np.frombuffer(data_to_send, dtype=np.int16)

                # Применяем шумоподавление
                reduced_signal = nr.reduce_noise(y=signal, y_noise=noise_sample, sr=RATE, prop_decrease=0.9)
                stream_output.write(VoiceConnection.adjust_volume(reduced_signal, VoiceConnection.volume))
                #speak.sendall(b'1' + VoiceConnection.adjust_volume(data_to_send, VoiceConnection.volume))  # Отправляем данные на сервер
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

        filtered_samples = np.zeros_like(samples)

        for i, sample in enumerate(samples):
            filtered_samples[i] = kf.update(sample)
        filtered_samples = (filtered_samples * volume).astype(np.int16)

        # Возвращаем данные в формате bytes
        return filtered_samples.tobytes()

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

    # Генерация тестового сигнала (синусоида + шум)
    t = np.linspace(0, 1, 500)
    signal = np.sin(2 * np.pi * 5 * t)  # Полезный сигнал (синусоида)
    noise = np.random.normal(0, 0.5, signal.shape)  # Шум
    noisy_signal = signal + noise  # Зашумленный сигнал

    kf = KalmanFilter(initial_state=noisy_signal[0],
                      process_variance=0.1,  # Q
                      measurement_variance=0.1)  # R

    # Запись фонового шума для подавления
    print("Запись фонового шума. Оставайтесь в тишине...")
    noise_frames = []
    for _ in range(int(RATE / 1024 * 2)):  # Запись 2 секунд фона
        noise_data = stream_input.read(1024)
        noise_frames.append(np.frombuffer(noise_data, dtype=np.int16))
    noise_sample = np.concatenate(noise_frames)
    print("Запись фонового шума завершена.")

    print("Начата передача аудио, для завершения ctrl + c")
    con.first_packet()
    thread = threading.Thread(target=con.sender, args=())
    thread.start()

    while True:  # Воображаемая параллельная работа QT
        new_volume = input("Введите новую громкость (например, 0.5 или 2.0): ")
        con.volume_change(float(new_volume))
