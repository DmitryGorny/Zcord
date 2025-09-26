import asyncio
import json
import socket
import struct
import threading
import uuid
from logic.client.IConnection.IConnection import IConnection, BaseConnection
from logic.client.VoiceChat.voice_handler import VoiceHandler
from logic.client.ClientConnections.ClientConnections import ClientConnections

# Пакет: | b'V1' (2) | type (1) | seq (uint32, 4) | payload...
PKT_HDR = b"V1"
PKT_AUDIO = b"A"
HDR_STRUCT = struct.Struct("!2s1sI")  # magic, type, seq


class VoiceConnection(IConnection, BaseConnection):
    _flg = False

    def __init__(self, user, server_host="127.0.0.1", server_port=55559, room="default_room"):
        self.server = (server_host, server_port)
        self.room = room
        self.token = uuid.uuid4().hex
        self._user = user
        self.chat_obj = ClientConnections.get_chat_id()

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
        self._voice_handler = None

    async def register(self):
        msg = {"t": "join_room", "room": self.room, "token": self.token, "user": self.user,
               "udp_port": self.local_udp_port}
        print("Отправлено сообщение о входе на сервер")
        await self.send_message(msg, current_chat_id=0)

    async def recv_server(self):
        """Читает уведомления сервера: peers, сервисные команды и т.п."""
        assert self.reader is not None
        try:
            while self.flg:
                line = await self.reader.readline()
                if not line:
                    print("[Client] TCP соединение потеряно (EOF)")
                    print("Сейчас клиент не сможет увидеть все сервисные сообщения (например мута)")

                    break
                msg = json.loads(line.decode("utf-8"))
                t = msg.get("t")

                if t == "peer":
                    # сервер может прислать список пиров
                    peers = msg.get("client", [])
                    if peers:
                        # для простоты — берём первого (или последовательно всех)
                        p = peers[0]
                        self.peer = (p["ip"], int(p["udp_port"]))
                        self.voice_handler.get_last_seq = None  # TODO Возможно не сработает нужно проверять внимательно
                        print(f"[Client] peer: {self.peer}")
                        self.chat_obj.socket_controller.receive_connect(chat_id=self.room, clients=peers)

                elif t == "peer_left":
                    client = msg.get("client")
                    print(f"[Client] peer_left: {client}")
                    self.chat_obj.socket_controller.receive_left(chat_id=self.room, client=client)
                    self.peer = None

                elif t == "peer_joined":
                    client = msg.get("client")
                    print(f"[Client] peer_joined: {client}")
                    self.chat_obj.socket_controller.receive_join(chat_id=self.room, client=client)

                elif "mute" in t:  # Реализация мутов
                    client = msg.get("client")

                    lst = t.split("_")
                    device = lst[0]
                    action = lst[1]
                    if action == "mute":
                        self.chat_obj.socket_controller.receive_mute(device, chat_id=self.room, mute_pos=True)
                    elif action == "unmute":
                        self.chat_obj.socket_controller.receive_mute(device, chat_id=self.room, mute_pos=False)

                else:
                    # прочие сообщения сервера
                    print(f"Неизвестное сообщение с сервера: {t}")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"[Client] TCP loop error: {e}")

    async def recv_udp(self):
        loop = asyncio.get_running_loop()

        while self.flg:
            try:
                data, addr = await loop.run_in_executor(None, self.udp.recvfrom, 65536)
            except BlockingIOError:
                await asyncio.sleep(0.001)
                continue
            except (OSError, Exception) as e:
                print(f"recv_udp вышел: {e}")
                break

            # аудио-пакеты
            if len(data) >= HDR_STRUCT.size:
                magic, typ, seq = HDR_STRUCT.unpack_from(data, 0)
                if magic != PKT_HDR:
                    continue
                if typ == PKT_AUDIO:
                    payload = data[HDR_STRUCT.size:]
                    # чуть-чуть упорядочим (без жёсткого ожидания)
                    await self.voice_handler.play_enqueue(seq, payload)

    def _audio_input_thread(self):
        # читаем микрофон и шлём UDP
        while self.flg:
            pkt, self.seq = self.voice_handler.audio_input_thread(self.seq)
            try:
                self._udp_send(pkt, msg_type="audio")
            except Exception:
                pass
        print("Вышел из _audio_input_thread")

    @property
    def user(self):
        return self._user

    @property
    def flg(self):
        return VoiceConnection._flg

    @flg.setter
    def flg(self, flg):
        VoiceConnection._flg = flg

    async def close(self) -> None:
        self.flg = False  # циклы сами выскочат

        # подкидываем "сигнал завершения" для очереди вывода
        try:
            if self.voice_handler and hasattr(self.voice_handler, "play_queue"):
                self.voice_handler.play_queue.put_nowait(None)
        except:
            pass

        # сообщение "leave"
        try:
            if self.writer and not self.writer.is_closing():
                msg = {"t": "leave", "room": self.room, "token": self.token}
                await self.send_message(msg, current_chat_id=0)
        except Exception as e:
            print(f"[VoiceConnection] Ошибка при disconnect: {e}")

        # освобождаем ресурсы
        try:
            if self.voice_handler:
                self.voice_handler.close()
        except:
            pass

        try:
            if self.writer:
                self.writer.close()
                await self.writer.wait_closed()
        except:
            pass

        try:
            self.udp.close()
        except:
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

    async def run(self):
        self.flg = True

        # TCP connect
        self.reader, self.writer = await asyncio.open_connection(self.server[0], self.server[1])

        self.tcp_recv_task = asyncio.create_task(self.recv_server())

        await self.register()

        # создаём аудио потоки
        self.voice_handler = VoiceHandler()

        # ждём, пока узнаем peer
        while self.peer is None:
            await asyncio.sleep(0.05)

        # стартуем прием/воспроизведение
        self.out_task = asyncio.create_task(self.voice_handler.audio_output_loop(self.flg))
        self.udp_recv_task = asyncio.create_task(self.recv_udp())

        # стартуем поток отправки микрофона
        microphone_thread = threading.Thread(target=self._audio_input_thread, daemon=True)
        microphone_thread.start()

        try:
            await asyncio.wait(
                [self.tcp_recv_task, self.udp_recv_task, self.out_task],
                return_when=asyncio.FIRST_COMPLETED
            )
        except asyncio.CancelledError:
            pass

    @property
    def voice_handler(self):
        return self._voice_handler

    @voice_handler.setter
    def voice_handler(self, cls):
        self._voice_handler = cls

    async def send_message(self, obj: dict, current_chat_id: int):
        if not self.writer:
            return
        data = (json.dumps(obj) + "\n").encode("utf-8")
        self.writer.write(data)
        await self.writer.drain()

    async def send_mute_mic(self, flg):
        if flg:
            msg = {"t": "mic_mute", "room": self.room, "token": self.token}
        else:
            msg = {"t": "mic_unmute", "room": self.room, "token": self.token}
        await self.send_message(msg, current_chat_id=0) # TODO метод send_message зачем-то просит current_chat_id
        # (мб добавить его в кадр и обрабатывать на сервере валидатором?)

    async def send_mute_head(self, flg):
        if flg:
            msg = {"t": "head_mute", "room": self.room, "token": self.token}
        else:
            msg = {"t": "head_unmute", "room": self.room, "token": self.token}
        await self.send_message(msg, current_chat_id=0) # TODO метод send_message зачем-то просит current_chat_id
        # (мб добавить его в кадр и обрабатывать на сервере валидатором?)


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
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        try:
            self.client = VoiceConnection(user=user, server_host=host, server_port=port, room=room)
            # создаем задачу, но не блокируемся на ней
            self._task = self._loop.create_task(self.client.run())
            self._loop.run_forever()
        except Exception as e:
            print(f"Ошибка: {e}")
        finally:
            # при остановке loop доходим сюда
            self.client = None
            #self._task.cancel()
            self._task = None
            self._loop.close()
            self._loop = None
            print("Звонок завершён и loop закрыт")

    def stop_call(self):
        if self.client is not None:
            async def _close_async():
                try:
                    await self.client.close()
                    # дожидаемся завершения основного run
                except Exception as e:
                    print(f"Ошибка при закрытии: {e}")
                finally:
                    # останавливаем event loop
                    self._loop.call_soon_threadsafe(self._loop.stop)

            future = asyncio.run_coroutine_threadsafe(_close_async(), self._loop)
            try:
                future.result(timeout=5)
                print("Звонок остановлен")
            except TimeoutError:
                print("Таймаут при остановке звонка")
            except Exception as e:
                print(f"Ошибка: {e}")
        else:
            print("Нет активного звонка")

    @property
    def loop(self):
        return self._loop
