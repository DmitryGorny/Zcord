import asyncio
import json
import socket
import struct
import threading
import time
import uuid

import pyaudio

# Параметры аудио: 48kHz mono, 20ms кадры
RATE = 48000
CHANNELS = 1
SAMPLES_PER_FRAME = 960  # 20 ms @ 48k
FORMAT = pyaudio.paInt16
BYTES_PER_SAMPLE = 2
FRAME_BYTES = SAMPLES_PER_FRAME * BYTES_PER_SAMPLE  # 1920 bytes

# Пакет: | b'V1' (2) | type (1) | seq (uint32, 4) | payload...
PKT_HDR = b"V1"
PKT_AUDIO = b"A"
PKT_PUNCH = b"P"
HDR_STRUCT = struct.Struct("!2s1sI")  # magic, type, seq

class VoiceClient:
    def __init__(self, server_host="127.0.0.1", server_port=55559, room="default_room"):
        self.server = (server_host, server_port)
        self.room = room
        self.token = uuid.uuid4().hex

        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp.bind(("0.0.0.0", 0))
        self.udp.setblocking(False)

        self.peer = None  # (ip, port) после сигналинга
        self.seq = 0
        self.running = True

        self.pa = pyaudio.PyAudio()
        self.in_stream = None
        self.out_stream = None

        # очень маленький «джиттер-буфер» по последовательности (опционально)
        self.play_queue = asyncio.Queue(maxsize=5)

    async def register(self):
        msg = json.dumps({"t": "register", "room": self.room, "token": self.token}).encode("utf-8")
        # отправляем периодически, пока не придёт ответ peer
        for _ in range(50):
            self.udp.sendto(msg, self.server)
            await asyncio.sleep(0.2)

    async def recv_loop(self):
        loop = asyncio.get_running_loop()
        while self.running:
            try:
                data, addr = await loop.run_in_executor(None, self.udp.recvfrom, 65536)
            except BlockingIOError:
                await asyncio.sleep(0.001)
                continue
            except Exception:
                break

            # сообщения сигналинга (JSON)
            if data[:1] in (b"{", b"["):
                try:
                    j = json.loads(data.decode("utf-8"))
                    if j.get("t") == "peer":
                        ip, port = j["addr"][0], int(j["addr"][1])
                        self.peer = (ip, port)
                        print(f"PEER: {self.peer}")
                        # начнём «панчить» адрес напарника
                        asyncio.create_task(self.punch_loop())
                except Exception:
                    pass
                continue

            # аудио-пакеты
            if len(data) >= HDR_STRUCT.size:
                magic, typ, seq = HDR_STRUCT.unpack_from(data, 0)
                if magic != PKT_HDR:
                    continue
                if typ == PKT_AUDIO:
                    payload = data[HDR_STRUCT.size:]
                    # чуть-чуть упорядочим (без жёсткого ожидания)
                    await self._play_enqueue(seq, payload)

    async def punch_loop(self):
        # отправляем "punch" пакеты напарнику и параллельно аудио как только есть поток
        if not self.peer:
            return
        for _ in range(15):  # 1.5 сек
            pkt = HDR_STRUCT.pack(PKT_HDR, PKT_PUNCH, self.seq)
            self.udp.sendto(pkt, self.peer)
            await asyncio.sleep(0.1)

    async def _play_enqueue(self, seq, payload):
        # если очередь забита — не ждём (минимальная задержка важнее)
        if self.play_queue.full():
            try:
                _ = self.play_queue.get_nowait()
            except Exception:
                pass
        await self.play_queue.put((seq, payload))

    def _audio_input_thread(self):
        # читаем микрофон и шлём UDP
        while self.running and self.peer:
            try:
                data = self.in_stream.read(SAMPLES_PER_FRAME, exception_on_overflow=False)
            except Exception:
                data = b"\x00" * FRAME_BYTES
            pkt = HDR_STRUCT.pack(PKT_HDR, PKT_AUDIO, self.seq) + data
            self.seq = (self.seq + 1) & 0xFFFFFFFF
            try:
                self.udp.sendto(pkt, self.peer)
            except Exception:
                pass

    async def _audio_output_loop(self):
        # минимальная «сортировка» по seq: берём всегда самое свежее, старьё выбрасываем
        last_seq = None
        while self.running:
            try:
                seq, payload = await asyncio.wait_for(self.play_queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue
            # если пришёл «старый» — пропускаем
            if last_seq is not None:
                # учтём переполнение uint32
                diff = (seq - last_seq) & 0xFFFFFFFF
                if diff > 0x80000000:
                    # это «очень старый» пакет — дроп
                    continue
                if diff == 0:
                    continue
            last_seq = seq
            try:
                self.out_stream.write(payload)
            except Exception:
                pass

    async def run(self):
        # читаем ответ сервера и аудио
        recv_task = asyncio.create_task(self.recv_loop())
        reg_task = asyncio.create_task(self.register())

        # создаём аудио потоки
        self.in_stream = self.pa.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                                      input=True, frames_per_buffer=SAMPLES_PER_FRAME)
        self.out_stream = self.pa.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                                       output=True, frames_per_buffer=SAMPLES_PER_FRAME)

        # ждём, пока узнаем peer
        while self.peer is None:
            await asyncio.sleep(0.05)

        # стартуем прием/воспроизведение
        out_task = asyncio.create_task(self._audio_output_loop())

        # стартуем поток отправки микрофона
        tx_thread = threading.Thread(target=self._audio_input_thread, daemon=True)
        tx_thread.start()

        try:
            await asyncio.gather(recv_task, reg_task, out_task)
        except asyncio.CancelledError:
            pass
        finally:
            self.running = False
            try:
                self.in_stream.stop_stream(); self.in_stream.close()
            except Exception: pass
            try:
                self.out_stream.stop_stream(); self.out_stream.close()
            except Exception: pass
            self.pa.terminate()
            self.udp.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", default="26.36.207.48:55559", help="host:port of UDP signal server")
    parser.add_argument("--room", default="room1")
    args = parser.parse_args()

    host, port = args.server.split(":")
    client = VoiceClient(server_host=host, server_port=int(port), room=args.room)
    asyncio.run(client.run())
