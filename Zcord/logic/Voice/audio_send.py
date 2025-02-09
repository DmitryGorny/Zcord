import socket
import sys
import threading
import pyaudio
import numpy as np
import noisereduce as nr
import webrtcvad as wb
import time
from PyQt6.QtCore import QThread, pyqtSignal
#from cryptography.fernet import Fernet


class VoiceConnection(QThread):
    noise_profile = None
    output_volume = 1.0
    volume = 1.0
    vad = wb.Vad()
    vad.set_mode(2)
    voice_checker = False
    target_level = 2000
    speech_detected_icon1 = pyqtSignal(bool)
    speech_detected_icon2 = pyqtSignal(bool)
    icon_change = pyqtSignal(bool)
    is_running = False

    def __init__(self, host, port):
        super().__init__()
        self.noise_profile = None
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 48000
        self.CHUNK = 1440

        self.is_mic_mute = False
        self.is_head_mute = False

        self.is_speaking = False

        self.speak = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.speak.connect((host, port))

        self.p = pyaudio.PyAudio()
        self.stream_input = self.p.open(format=self.FORMAT,
                                        channels=self.CHANNELS,
                                        rate=self.RATE,
                                        input=True,
                                        frames_per_buffer=self.CHUNK)
        self.stream_output = self.p.open(format=self.FORMAT,
                                         channels=self.CHANNELS,
                                         rate=self.RATE,
                                         output=True)

    def sender(self):
        while VoiceConnection.is_running:
            if not self.is_mic_mute:
                try:
                    data_to_send = self.stream_input.read(self.CHUNK)
                    data_to_send = VoiceConnection.adjust_volume(data_to_send, VoiceConnection.volume)

                    self.speech_detected_icon1.emit(VoiceConnection.vad.is_speech(data_to_send, self.RATE))

                    if VoiceConnection.noise_profile is not None:
                        data_to_send = self.noise_down(data_to_send)

                    self.speak.sendall(b'2' + data_to_send)
                except KeyboardInterrupt:
                    print("Приём аудио завершен или прерван")
                except Exception as e:
                    print(f"Отловлена ошибка в sender: {e}")
                    print(e.args)
                    print("Передача аудио закончена или прервана")
        self.speak.sendall(b'0')

    @staticmethod
    def noise_down(data_to_send, RATE=48000):
        audio_data = np.frombuffer(data_to_send, dtype=np.int16)
        audio_float = audio_data.astype(np.float32) / 32768.0

        reduced = nr.reduce_noise(
            y=audio_float,
            y_noise=VoiceConnection.noise_profile,
            sr=RATE,
            stationary=True
        )

        processed_data = (reduced * 32768).astype(np.int16)
        data_to_send = processed_data.tobytes()
        return data_to_send

    def first_packet(self):
        data_to_send = self.stream_input.read(self.CHUNK)
        self.speak.sendall(b'1' + data_to_send)

    @staticmethod
    def adjust_volume(data, volume):
        samples = np.frombuffer(data, dtype=np.int16)
        samples = (samples * volume).astype(np.int16)
        return samples.tobytes()

    @staticmethod
    def auto_gain_control(data):  # Автоматическая регулировка усиления (нужно сделать включение в qt)
        samples = np.frombuffer(data, dtype=np.int16)
        max_amplitude = np.max(np.abs(samples))
        if max_amplitude == 0:
            return data
        gain = VoiceConnection.target_level / max_amplitude
        return (np.clip(samples * gain, -32768, 32767).astype(np.int16)).tobytes()

    def getter(self):
        while VoiceConnection.is_running:
            if not self.is_head_mute:
                try:
                    data_to_read, address = self.speak.recvfrom(4096)  # Получаем данные с сервера
                    #self.speech_detected_icon2.emit(VoiceConnection.vad.is_speech(data_to_read, self.RATE))
                    header = data_to_read[0:3]

                    if header == b'111':
                        self.icon_change.emit(True)
                    elif header == b'000':
                        self.icon_change.emit(False)
                    elif header == b'222':
                        self.icon_change.emit(True)
                    else:
                        self.stream_output.write(data_to_read)
                    # Добавить сюда adjust_volume, разобраться с ошибкой передачи в np параметра data, не поддерживаемая размерность?
                except KeyboardInterrupt:
                    print("Приём аудио завершен или прерван")
                except Exception as e:
                    print(f"Отловлена ошибка в getter: {e}")
                    print(e.args)
                    print("Приём аудио завершен или прерван")

    @staticmethod
    def change_output_volume(volume):
        VoiceConnection.output_volume = volume

    def mute_mic(self, flg_mute):
        self.is_mic_mute = flg_mute

    def mute_head(self, flg_mute):
        self.is_head_mute = flg_mute

    def close(self):
        VoiceConnection.is_running = False
        self.stream_input.stop_stream()
        self.stream_input.close()
        self.stream_output.stop_stream()
        self.stream_output.close()
        self.p.terminate()
        self.speak.close()
        print("Все аудиопотоки закрыты.")


def start_voice():
    HOST = "26.36.124.241"  #  Вроде как сюда данные сервера к которому мы подключаемся
    PORT_TO_SPEAK = 65128
    voice_conn = VoiceConnection(HOST, PORT_TO_SPEAK)
    print("Начата передача аудио")
    voice_conn.first_packet()
    VoiceConnection.is_running = True
    thread_speak = threading.Thread(target=voice_conn.sender)
    thread_listen = threading.Thread(target=voice_conn.getter)
    thread_speak.start()
    thread_listen.start()
    return voice_conn


def get_local_ip():  # можно ли как-то это использовать для общения без локалки?
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]  # Получаем локальный IP
        s.close()
        return ip
    except Exception as e:
        print(f"Не удалось определить локальный IP: {e}")
        return "127.0.0.1"


def get_free_port():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", 0))
        port = s.getsockname()[1]  # Получаем номер порта
        s.close()
        return port
    except Exception as e:
        print(f"Не удалось найти свободный порт: {e}")
        return None


def listen_noise(duration=5, RATE=48000, CHUNK=1440):
    p = pyaudio.PyAudio()
    stream_in = p.open(format=pyaudio.paInt16,
                       channels=1,
                       rate=RATE,
                       input=True,
                       frames_per_buffer=CHUNK)

    print(f"Записываем фоновый шум {duration} секунд... (не издавайте звуков)")

    frames = []
    total_chunks = int((RATE * duration) / CHUNK)

    for _ in range(total_chunks):
        data = stream_in.read(CHUNK)
        frames.append(data)

    noise_data = np.frombuffer(b''.join(frames), dtype=np.int16)
    VoiceConnection.noise_profile = noise_data.astype(np.float32) / 32768.0

    print("Профиль шума успешно записан!")
    stream_in.stop_stream()
    stream_in.close()


def volume_change(volume):
    VoiceConnection.volume = volume


def activity_detection(Slider, RATE=48000, CHUNK=1440):
    p = pyaudio.PyAudio()
    stream_in = p.open(format=pyaudio.paInt16,
                       channels=1,
                       rate=RATE,
                       input=True,
                       frames_per_buffer=CHUNK)
    stream_out = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=RATE,
                        output=True)

    last_speech_time = time.time()  # Время последнего обнаружения речи
    fade_duration = 1.0  # Время (в секундах) для плавного уменьшения до 0
    current_value = 0  # Текущее значение Slider

    while VoiceConnection.voice_checker:
        data = stream_in.read(CHUNK)
        data = VoiceConnection.adjust_volume(data, VoiceConnection.volume)
        if VoiceConnection.noise_profile is not None:
            data = VoiceConnection.noise_down(data)
            stream_out.write(data)
        else:
            stream_out.write(data)
        if VoiceConnection.vad.is_speech(data, RATE):
            samples = np.frombuffer(data, dtype=np.int16)
            rms = np.sqrt(np.mean(np.square(samples)))
            try:
                Slider.VolumeCheckWithNoiseReduceSlider.setValue(int(rms))
            except ValueError:
                pass
            last_speech_time = time.time()
        else:
            time_since_speech = time.time() - last_speech_time
            if time_since_speech > fade_duration:
                current_value = 0
            else:
                current_value = int(current_value * (1 - time_since_speech / fade_duration))
            try:
                Slider.VolumeCheckWithNoiseReduceSlider.setValue(current_value)
            except ValueError:
                pass

    stream_in.stop_stream()
    stream_in.close()
    stream_out.stop_stream()
    stream_out.close()
    Slider.VolumeCheckWithNoiseReduceSlider.setValue(0)
