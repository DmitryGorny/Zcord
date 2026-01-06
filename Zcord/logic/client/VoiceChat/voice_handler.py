import asyncio
import struct
import pyaudio
import audioop
import webrtcvad as wb
from logic.client.SettingController.settings_controller import VoiceSettingsController

RATE = 48000
CHANNELS = 1
SAMPLES_PER_FRAME = 960  # 20 ms @ 48k
FORMAT = pyaudio.paInt16
BYTES_PER_SAMPLE = 2
FRAME_BYTES = SAMPLES_PER_FRAME * BYTES_PER_SAMPLE  # 1920 bytes

# Пакет: | b'V1' (2) | type (1) | seq (uint32, 4) | user_id | token payload...
PKT_HDR = b"V1"
PKT_AUDIO = b"A"
HDR_STRUCT = struct.Struct("!2s1sIQ32s")  # magic, type, seq


class VoiceHandler:
    def __init__(self, chat_obj, room, user, flg_callback=lambda: True):
        # подгрузка настроек
        self.pa = pyaudio.PyAudio()

        # флаги и блокировка для безопасной перезагрузки
        self.device_reload_required = False
        self.reload_lock = asyncio.Lock()

        # объект чата
        self.user = user
        self.room = room
        self.chat_obj = chat_obj
        self._flg_callback = flg_callback  # ссылка на VoiceConnection.flg

        # флаги собственного мута
        self.is_mic_mute = False
        self.is_head_mute = False
        # Потоки
        self.in_stream = self.pa.open(format=FORMAT,
                                      channels=CHANNELS,
                                      rate=RATE,
                                      input=True,
                                      frames_per_buffer=SAMPLES_PER_FRAME,
                                      input_device_index=VoiceSettingsController().current_input_device())

        # Словари потоков и очередей по user_id
        self.out_streams: dict[int, pyaudio.Stream] = {}
        self.play_queues: dict[int, asyncio.Queue] = {}
        self.play_tasks: dict[int, asyncio.Task] = {}
        self.last_seq_map: dict[int, int | None] = {}

        self.vad = wb.Vad()
        self.vad.set_mode(2)

    def audio_input_thread(self, seq, token):
        # читаем микрофон и шлём UDP
        try:
            data = self.in_stream.read(SAMPLES_PER_FRAME, exception_on_overflow=False)
            if self.is_mic_mute:
                data = b"\x00" * len(data)
        except Exception:
            data = b"\x00" * len(data)

        if not self.is_mic_mute:
            data = self.adjust_volume(data, VoiceSettingsController().input_volume())
            #if VoiceSettingsController().is_state_ags():
                #data = self.agc_process(data)
            if seq % 5 == 0:
                self.chat_obj.socket_controller.vad_animation(self.room, self.vad.is_speech(data, RATE), self.user.id)
        pkt = HDR_STRUCT.pack(PKT_HDR, PKT_AUDIO, seq, self.user.id, token.encode("utf-8")) + data
        seq = (seq + 1) & 0xFFFFFFFF
        return pkt, seq

    async def audio_output_loop(self, user_id: int):
        queue = self.play_queues[user_id]
        out_stream = self.out_streams[user_id]

        sad = wb.Vad()
        sad.set_mode(2)

        # минимальная «сортировка» по seq: берём всегда самое свежее, старьё выбрасываем
        while self._flg_callback():
            try:
                seq, payload = await asyncio.wait_for(queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                print("таймаут")
                continue
            except TypeError:
                break

            # если пришёл «старый» — пропускаем
            # анти-джиттер фильтр
            last_seq = self.last_seq_map.get(user_id)
            if last_seq is not None:
                diff = (seq - last_seq) & 0xFFFFFFFF
                if diff == 0 or diff > 0x80000000:
                    print("дроп")
                    continue

            # обновляем
            self.last_seq_map[user_id] = seq
            #print(seq)
            try:
                if not self.is_head_mute:
                    if seq % 5 == 0:
                        self.chat_obj.socket_controller.vad_animation(self.room, sad.is_speech(payload, RATE),
                                                                      user_id)

                    payload = self.adjust_volume(payload, VoiceSettingsController().output_volume())
                    payload = self.adjust_volume(payload, VoiceSettingsController().output_volume_friend(str(user_id)))
                    out_stream.write(payload)
                else:
                    continue
            except Exception:
                pass

        print(f"[VoiceHandler] Завершён поток user_id={user_id}")
        self.last_seq_map[user_id] = None

    async def play_enqueue(self, user_id: int, seq: int, payload: bytes):
        """Добавляем пакет конкретного пользователя в очередь"""
        if not self._flg_callback():
            return

        if user_id not in self.play_queues:
            self.play_queues[user_id] = asyncio.Queue(maxsize=5)
            self.out_streams[user_id] = self.pa.open(format=FORMAT,
                                                     channels=CHANNELS,
                                                     rate=RATE,
                                                     output=True,
                                                     frames_per_buffer=SAMPLES_PER_FRAME,
                                                     output_device_index=VoiceSettingsController().current_output_device())
            self.play_tasks[user_id] = asyncio.create_task(self.audio_output_loop(user_id))
            print(f"[VoiceHandler] Создан поток воспроизведения для user_id={user_id}")

        # если очередь забита — не ждём (минимальная задержка важнее)
        queue = self.play_queues[user_id]
        if queue.full():
            try:
                _ = queue.get_nowait()
            except Exception:
                pass
        await queue.put((seq, payload))

    def reset_last_seq(self, user_id: int | None = None):
        """Сбросить seq для конкретного пользователя или для всех."""
        if user_id is None:
            self.last_seq_map.clear()
        else:
            self.last_seq_map[user_id] = None

    def adjust_volume(self, payload, volume):
        """Функция для регулирования громкости на значение volume"""
        if volume == 1.0:
            return payload
        payload = audioop.mul(payload, 2, volume)  # Здесь 2 потому что paInt16
        return payload

    def agc_process(self, data, target_rms=3000, max_gain=10.0):
        """Функция для автоматического регулирования усиления"""
        # Текущий RMS (для 16-бит)
        rms = audioop.rms(data, 2)
        # RMS считается нормальным если он от 2000 до 4000, в некоторых случаях эта функция может клипать звук до x10
        # потому что AGS работает где-то помимо этой программы, сырые данный RMS будут недостоверными
        if rms <= 0:
            return data

        # Желаемое усиление
        desired_gain = target_rms / rms
        # Ограничиваем
        desired_gain = min(desired_gain, max_gain)
        # Применяем усиление через audioop
        amplified = audioop.mul(data, 2, desired_gain)

        return amplified

    # селф мьюты
    def mute_mic_self(self, flg):
        self.is_mic_mute = flg

    def mute_head_self(self, flg):
        self.is_head_mute = flg

    def close(self):
        # Закрываем аудио потоки
        try:
            if self.in_stream and self.in_stream.is_active():
                self.in_stream.stop_stream()
                self.in_stream.close()
        except Exception:
            pass

        # отменить все задачи воспроизведения
        for user_id, task in self.play_tasks.items():
            if not task.done():
                task.cancel()

        # очистить очереди
        for q in self.play_queues.values():
            try:
                while not q.empty():
                    q.get_nowait()
            except Exception:
                pass

        # закрываем все output stream’ы
        for user_id, stream in self.out_streams.items():
            try:
                if stream.is_active():
                    stream.stop_stream()
                stream.close()
                print(f"[VoiceHandler] Закрыт out_stream user_id={user_id}")
            except Exception:
                pass

        # Terminate PyAudio (только если больше нет потоков)
        try:
            self.pa.terminate()
        except Exception as e:
            pass
