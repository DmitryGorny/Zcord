import asyncio
import struct
import pyaudio
import time

RATE = 48000
CHANNELS = 1
SAMPLES_PER_FRAME = 960  # 20 ms @ 48k
FORMAT = pyaudio.paInt16
BYTES_PER_SAMPLE = 2
FRAME_BYTES = SAMPLES_PER_FRAME * BYTES_PER_SAMPLE  # 1920 bytes

# Пакет: | b'V1' (2) | type (1) | seq (uint32, 4) | payload...
PKT_HDR = b"V1"
PKT_AUDIO = b"A"
HDR_STRUCT = struct.Struct("!2s1sI")  # magic, type, seq


class VoiceHandler:
    def __init__(self):
        # sequence последовательности кадров
        self.last_seq = None
        # флаги собственного мута
        self.is_mic_mute = False
        self.is_head_mute = False
        # Потоки
        self.pa = pyaudio.PyAudio()
        self.in_stream = self.pa.open(format=FORMAT,
                                      channels=CHANNELS,
                                      rate=RATE,
                                      input=True,
                                      frames_per_buffer=SAMPLES_PER_FRAME)
        self.out_stream = self.pa.open(format=FORMAT,
                                       channels=CHANNELS,
                                       rate=RATE,
                                       output=True,
                                       frames_per_buffer=SAMPLES_PER_FRAME)

        # очень маленький «джиттер-буфер» по последовательности (опционально)
        self.play_queue = asyncio.Queue(maxsize=5)

    def audio_input_thread(self, seq):
        # читаем микрофон и шлём UDP
        try:
            data = self.in_stream.read(SAMPLES_PER_FRAME, exception_on_overflow=False)
            if self.is_mic_mute:
                data = b"\x00" * len(data)
        except Exception:
            data = b"\x00" * len(data)
        pkt = HDR_STRUCT.pack(PKT_HDR, PKT_AUDIO, seq) + data
        seq = (seq + 1) & 0xFFFFFFFF
        return pkt, seq

    # селф мьюты
    def mute_mic_self(self, flg):
        self.is_mic_mute = flg

    def mute_head_self(self, flg):
        self.is_head_mute = flg

    @property
    def get_last_seq(self):
        return self.last_seq

    @get_last_seq.setter
    def get_last_seq(self, last_seq):
        self.last_seq = last_seq

    async def audio_output_loop(self, flg):
        # минимальная «сортировка» по seq: берём всегда самое свежее, старьё выбрасываем
        self.last_seq = None
        while flg:
            try:
                seq, payload = await asyncio.wait_for(self.play_queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue
            except TypeError:  # сюда выходит потому что в методе close voice клиента в play_queue сую None,
                # но хотелось бы более понятный флажок
                break
            # если пришёл «старый» — пропускаем
            if self.last_seq is not None:
                # учтём переполнение uint32
                diff = (seq - self.last_seq) & 0xFFFFFFFF
                if diff > 0x80000000:
                    # это «очень старый» пакет — дроп
                    continue
                if diff == 0:
                    continue
            self.last_seq = seq
            print(self.last_seq)
            try:
                if not self.is_head_mute:
                    self.out_stream.write(payload)
                else:
                    continue
            except Exception:
                pass

        print("audio_output_loop завершился")

    async def play_enqueue(self, seq, payload):
        # если очередь забита — не ждём (минимальная задержка важнее)
        if self.play_queue.full():
            try:
                _ = self.play_queue.get_nowait()
            except Exception:
                pass
        await self.play_queue.put((seq, payload))

    def close(self):
        # 4. Закрываем аудио потоки
        try:
            if self.in_stream and self.in_stream.is_active():
                self.in_stream.stop_stream()
                self.in_stream.close()
        except Exception as e:
            pass

        try:
            if self.out_stream and self.out_stream.is_active():
                self.out_stream.stop_stream()
                self.out_stream.close()
        except Exception as e:
            pass

        # 7. Terminate PyAudio (только если больше нет потоков)
        try:
            self.pa.terminate()
        except Exception as e:
            pass
