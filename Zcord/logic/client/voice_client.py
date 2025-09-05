import asyncio
import json
import socket
import struct
import threading
import time
import uuid
from logic.client.IConnection.IConnection import IConnection, BaseConnection
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
HDR_STRUCT = struct.Struct("!2s1sI")  # magic, type, seq


class VoiceConnection(IConnection, BaseConnection):
    def __init__(self, user, server_host="127.0.0.1", server_port=55559, room="default_room"):
        self.server = (server_host, server_port)
        self.room = room
        self.token = uuid.uuid4().hex
        self._user = user
        self._flg = True

        # TCP
        self.reader: asyncio.StreamReader | None = None
        self.writer: asyncio.StreamWriter | None = None
        self._tcp_task: asyncio.Task | None = None

        # UDP
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp.bind(("0.0.0.0", 0))
        self.udp.setblocking(False)
        self.local_udp_port = self.udp.getsockname()[1]
        self.peer = None  # (ip, port) после сигналинга
        self.seq = 0

        # Аудио
        self.pa = pyaudio.PyAudio()
        self.in_stream = None
        self.out_stream = None

        # очень маленький «джиттер-буфер» по последовательности (опционально)
        self.play_queue = asyncio.Queue(maxsize=5)

    async def register(self):
        msg = {"t": "join_room", "room": self.room, "token": self.token, "user": self.user,
               "udp_port": self.local_udp_port}
        print("Отправлено сообщение о входе на сервер")
        await self.send_message(msg, current_chat_id=0)

    async def recv_server(self):
        """Читает уведомления сервера: peers, сервисные команды и т.п."""
        assert self.reader is not None
        try:
            while self._flg:
                line = await self.reader.readline()
                if not line:
                    print("[Client] TCP соединение потеряно (EOF)")
                    print("Сейчас клиент не сможет увидеть все сервисные сообщения (например мута)")
                    await CallManager().stop_call()  # TODO Наверное временная мера
                    break
                msg = json.loads(line.decode("utf-8"))
                t = msg.get("t")

                if t == "peer":
                    # сервер может прислать список пиров
                    peers = msg.get("peers", [])
                    if peers:
                        # для простоты — берём первого (или последовательно всех)
                        p = peers[0]
                        self.peer = (p["ip"], int(p["udp_port"]))
                        self.last_seq = None
                        print(f"[Client] peer: {self.peer}")

                elif t == "peer_left":
                    print(f"[Client] peer_left: {msg.get('addr')}")
                    self.peer = None

                elif t == "peer_joined":
                    # просто информационное событие
                    pass

                elif t == "svc":  # Реализация мутов
                    # сервисная команда от другого клиента
                    pass
                else:
                    # прочие сообщения сервера
                    print(f"Неизвестное сообщение с сервера: {t}")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"[Client] TCP loop error: {e}")

    async def recv_udp(self):
        loop = asyncio.get_running_loop()

        while self._flg:
            try:
                data, addr = await loop.run_in_executor(None, self.udp.recvfrom, 65536)
            except BlockingIOError:
                await asyncio.sleep(0.001)
                continue
            except Exception:
                break

            # аудио-пакеты
            if len(data) >= HDR_STRUCT.size:
                magic, typ, seq = HDR_STRUCT.unpack_from(data, 0)
                if magic != PKT_HDR:
                    continue
                if typ == PKT_AUDIO:
                    payload = data[HDR_STRUCT.size:]
                    # чуть-чуть упорядочим (без жёсткого ожидания)
                    await self._play_enqueue(seq, payload)

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
        while self._flg:
            try:
                data = self.in_stream.read(SAMPLES_PER_FRAME, exception_on_overflow=False)
            except Exception:
                data = b"\x00" * FRAME_BYTES
            pkt = HDR_STRUCT.pack(PKT_HDR, PKT_AUDIO, self.seq) + data
            self.seq = (self.seq + 1) & 0xFFFFFFFF
            try:
                self._udp_send(pkt, msg_type="audio")
            except Exception:
                pass

    async def _audio_output_loop(self):
        # минимальная «сортировка» по seq: берём всегда самое свежее, старьё выбрасываем
        self.last_seq = None
        while self._flg:
            try:
                seq, payload = await asyncio.wait_for(self.play_queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue
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
            try:
                self.out_stream.write(payload)
            except Exception:
                pass

    @property
    def user(self):
        return self._user

    @property
    def flg(self):
        return self._flg

    async def close(self) -> None:
        self._flg = False  # Это остановит поток микрофона и UDP прием

        # 1. Сначала отменяем все asyncio задачи
        tasks_to_cancel = []
        if hasattr(self, 'tcp_recv_task') and self.tcp_recv_task:
            tasks_to_cancel.append(self.tcp_recv_task)
        if hasattr(self, 'udp_recv_task') and self.udp_recv_task:
            tasks_to_cancel.append(self.udp_recv_task)
        if hasattr(self, 'out_task') and self.out_task:
            tasks_to_cancel.append(self.out_task)

        for task in tasks_to_cancel:
            if not task.done():
                task.cancel()

        # 2. Ждем завершения всех задач
        if tasks_to_cancel:
            try:
                await asyncio.gather(*tasks_to_cancel, return_exceptions=True)
            except asyncio.CancelledError:
                pass

        # 3. Отправляем сообщение о выходе (если TCP еще жив)
        try:
            if self.writer and not self.writer.is_closing():
                msg = {"t": "leave", "room": self.room, "token": self.token}
                await self.send_message(msg, current_chat_id=0)
        except Exception as e:
            print(f"[VoiceConnection] Ошибка при disconnect: {e}")

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

        # 5. Закрываем TCP соединение
        try:
            if self.writer:
                self.writer.close()
                await self.writer.wait_closed()
        except Exception as e:
            pass

        # 6. Закрываем UDP сокет
        try:
            self.udp.close()
        except Exception as e:
            pass

        # 7. Terminate PyAudio (только если больше нет потоков)
        try:
            self.pa.terminate()
        except Exception as e:
            pass

        print("[VoiceConnection] Соединение полностью закрыто")

    def _udp_send(self, payload: bytes, msg_type: str = "audio") -> None:
        """
        Универсальная отправка сообщений по UDP.
        msg_type:
          - "audio"  → отправляем аудио кадры на peer (только если есть)
        """
        try:
            if msg_type == "audio":
                if self.peer:
                    self.udp.sendto(payload, self.peer)
            else:
                print(f"[VoiceConnection] неизвестный тип отправки: {msg_type}")
        except Exception as e:
            print(f"[VoiceConnection] ошибка send_message: {e}")

    async def send_message(self, obj: dict, current_chat_id: int):
        if not self.writer:
            return
        data = (json.dumps(obj) + "\n").encode("utf-8")
        self.writer.write(data)
        await self.writer.drain()

    async def run(self):
        # TCP connect
        self.reader, self.writer = await asyncio.open_connection(self.server[0], self.server[1])

        self.tcp_recv_task = asyncio.create_task(self.recv_server())

        await self.register()

        # создаём аудио потоки
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

        # ждём, пока узнаем peer
        while self.peer is None:
            await asyncio.sleep(0.05)

        # стартуем прием/воспроизведение
        self.out_task = asyncio.create_task(self._audio_output_loop())
        self.udp_recv_task = asyncio.create_task(self.recv_udp())

        # стартуем поток отправки микрофона
        microphone_thread = threading.Thread(target=self._audio_input_thread, daemon=True)
        microphone_thread.start()

        try:
            await asyncio.gather(self.tcp_recv_task, self.udp_recv_task, self.out_task)
        except asyncio.CancelledError:
            pass


class CallManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CallManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self.client = None
            self._task = None
            self._loop = None
            self._thread = None
            self._initialized = True

    def start_call(self, user, host="26.36.207.48", port=55559, room="room1"):
        if self.client is not None:
            print("Клиент уже запущен")
            return

        self._thread = threading.Thread(
            target=self._run_call,
            args=(user, host, port, room),
            daemon=True
        )
        self._thread.start()
        print("Звонок запущен")

    def _run_call(self, user, host, port, room):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._loop = loop

        try:
            self.client = VoiceConnection(user=user, server_host=host, server_port=port, room=room)
            self._task = loop.create_task(self.client.run())
            loop.run_until_complete(self._task)
        except asyncio.CancelledError:
            print("Звонок отменен")
        except Exception as e:
            print(f"Ошибка: {e}")
        finally:
            self.client = None
            self._task = None

    def stop_call(self):
        if self.client is not None and self._loop is not None:
            # Создаем задачу для асинхронного закрытия
            async def _close_async():
                try:
                    await self.client.close()
                except Exception as e:
                    print(f"Ошибка при закрытии: {e}")
                finally:
                    # НЕ останавливаем loop здесь - он остановится сам
                    pass

            # Запускаем закрытие и ждем завершения
            future = asyncio.run_coroutine_threadsafe(_close_async(), self._loop)
            try:
                future.result(timeout=5)  # Ждем до 5 секунд
                print("Звонок остановлен")
            except TimeoutError:
                print("Таймаут при остановке звонка")
            except Exception as e:
                print(f"Ошибка: {e}")
        else:
            print("Нет активного звонка")


async def main():
    runner = CallManager()
    await runner.start_call(user=None)


if __name__ == "__main__":
    asyncio.run(main())
