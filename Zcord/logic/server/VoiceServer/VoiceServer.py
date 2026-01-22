import asyncio
import socket
import json
import struct
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# Протокол сообщений по TCP (NDJSON: JSON + "\n"):
# 1) Регистрация/вход в комнату:
#    {"t":"join_room","room":"room1","token":"<uuid>","user":"user1","udp_port":54321}
#
# 2) Сервер сообщает о найденном пире(ах):
#    {"t":"peer","peers":[{"ip":"1.2.3.4","udp_port":55555},{"ip":"5.6.7.8","udp_port":55556}]}
#
# 3) Клиент уходит:
#    {"t":"leave","room":"room1","token":"<uuid>"}
#
# 4) Сервисные команды (ретранслируются на пиров комнаты, кроме отправителя):
#    {"t":"mute_mic", "room":"room1","token":"<uuid>"}
#    {"t":"mute_head","room":"room1","token":"<uuid>"}
#    После того как эти сообщения пришли на сервер, сообщение формируется для клиента в виде
#    {"t": t, "client": client.to_dict()}
#
# 5) Уведомления сервера:
#    {"t":"peer_left","addr":"ip:port"}     # когда кто-то ушёл
#    {"t":"peer_joined","count":2}          # стало участников в комнате
#
# Примечание: TCP-соединение само по себе является keep-alive'ом, отдельные UDP keep-alive не нужны.

# ВНИМАНИЕ ВНИМАНИЕ ВНИМАНИЕ ВНИМАНИЕ ВНИМАНИЕ!!!!!!!!!!!!!
# В отсылку сообщений на сервисный сервер в словарь добавлена еще и g (Группа), т.к. сейчас стратегии
# разделены на группы (CLIENT, CHAT, FRIEND). Тебе, скорее всего, нужны будут только CLIENT

# Пакет: | b'V1' (2) | type (1) | seq (uint32, 4) | user_id | payload...
PKT_HDR = b"V1"
PKT_AUDIO = b"A"
HDR_STRUCT = struct.Struct("!2s1sIQ32s")  # magic, type, seq


@dataclass
class ClientInfo:
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter
    ip: str
    tcp_port: int
    user_id: Optional[str] = None
    user: Optional[str] = None
    token: Optional[str] = None
    room: Optional[str] = None
    udp_port: Optional[int] = None
    udp_ready: bool = False
    last_seen: float = field(default_factory=time.time)

    def addr_str(self) -> str:
        return f"{self.ip}:{self.tcp_port}"

    def to_dict(self) -> dict:
        return {
            "ip": self.ip,
            "tcp_port": self.tcp_port,
            "user_id": self.user_id,
            "user": self.user,
            "token": self.token,
            "room": self.room,
            "udp_port": self.udp_port,
        }


class TcpSignalServer:
    def __init__(self):
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.bind(("0.0.0.0", 55560))
        self.udp_sock.setblocking(False)
        self.client_by_token = {}
        # комнаты: room -> список клиентов
        self.rooms: Dict[str, List[ClientInfo]] = {}
        # быстрый поиск по writer
        self.client_by_writer: Dict[asyncio.StreamWriter, ClientInfo] = {}

    async def udp_loop(self):
        loop = asyncio.get_running_loop()
        while True:
            try:
                data, addr = await loop.run_in_executor(None, self.udp_sock.recvfrom, 2048)
            except BlockingIOError:
                await asyncio.sleep(0.001)
                continue
            except Exception as e:
                print("[UDP] error:", e)
                continue

            public_ip, public_port = addr

            # аудио-пакеты
            if len(data) >= HDR_STRUCT.size:
                magic, typ, seq, user_id, token = HDR_STRUCT.unpack_from(data, 0)
                if magic != PKT_HDR:
                    continue
                if typ == PKT_AUDIO:
                    client = self.client_by_token.get(token.decode("utf-8"))

                    if client:
                        await self._forward_voice_pkt(data, client)
                        continue

            token = data.decode(errors="ignore")

            client = self.client_by_token.get(token)

            # отправка трафика обратно для nat сессии
            self.udp_sock.sendto(b'', addr)

            if client:
                if not client.udp_ready:
                    client.udp_ready = True
                    client.udp_port = public_port
                    print(f"[UDP] Получен UDP порт для {public_ip}, {public_port}")
                    await self._maybe_send_peers(client)

    async def serve(self, host="0.0.0.0", port=55559):
        server = await asyncio.start_server(self.handle_client, host, port)
        addr = ", ".join(str(sock.getsockname()) for sock in server.sockets or [])
        print(f"[TCP] сервер запущен на {addr}")
        async with server:
            await server.serve_forever()

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        peername = writer.get_extra_info("peername")
        ip, tcp_port = peername[0], int(peername[1])
        client = ClientInfo(reader=reader, writer=writer, ip=ip, tcp_port=tcp_port)
        self.client_by_writer[writer] = client
        print(f"[TCP] подключился {client.addr_str()}")

        try:
            while True:
                line = await reader.readline()
                if not line:
                    break
                client.last_seen = time.time()
                msg = json.loads(line.decode("utf-8"))
                await self.handle_message(client, msg)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"[TCP] ошибка {client.addr_str()}: {e}")
        finally:  # Управление переходит сюда при любом отключении клиента (грязный/чистый)
            await self._leave_room(client)
            try:
                writer.close()
                await writer.wait_closed()
            except Exception as e:
                print(f"[TCP] ошибка {client.addr_str()}: {e}")
            self.client_by_writer.pop(writer, None)

    async def handle_message(self, client: ClientInfo, msg: dict):
        typ = msg.get("t")
        if typ == "join_room":
            await self._join_room(client, msg)
        elif typ == "leave":  # btw информационное сообщение, что с ним делать, управление всё равно отдаётся finally
            print("Клиент сообщил о выходе с сервера")
        elif "mute" in typ:
            await self._mute_msg(typ, client, msg)
        else:
            print(f"Неизвестный тип сообщения: {typ}")

    async def _mute_msg(self, t, client: ClientInfo, msg: dict):
        room = msg.get("room") or "default_room"
        token = msg.get("token")
        if client.token == token:
            await self._broadcast_room(room, {"t": t, "client": client.to_dict(), }, skip=client)

    async def _forward_voice_pkt(self, voice_pkt, client):
        lst = self.rooms.get(client.room, [])

        # Пересылаем пакеты всем другим в комнате
        for c in list(lst):
            if c == client:
                continue
            try:
                self.udp_sock.sendto(voice_pkt, (c.ip, c.udp_port))
            except Exception as e:
                print(f"[UDP] ошибка отправки {c.addr_str()}: {e}")

    async def _maybe_send_peers(self, client):
        lst = self.rooms.get(client.room, [])
        if len(lst) < 2:
            return

        # Проверяем, что у всех есть public UDP
        for c in lst:
            if not c.udp_port:
                return

        # Новому клиенту отправляем список уже присутствующих пиров
        peers_dicts = [c.to_dict() for c in lst if c != client]
        await self._send(client, {"t": "peer", "client": peers_dicts})

        # И существующим участникам разошлём адрес нового
        await self._broadcast_room(client.room, {"t": "peer", "client": [client.to_dict()]}, skip=client)

    async def _join_room(self, client: ClientInfo, msg: dict):
        room = msg.get("room") or "default_room"
        user_id = msg.get("user_id")
        token = msg.get("token")
        user = msg.get("user")

        client.user_id = user_id
        client.room = room
        client.token = token
        client.user = user
        client.udp_ready = False

        self.client_by_token[token] = client

        lst = self.rooms.setdefault(room, [])

        if client not in lst:
            lst.append(client)

        print(f"[TCP] {client.addr_str()} присоединился к комнате '{room}', участников={len(lst)}")

        await self._send_service_msg(
            obj={"g": "CLIENT", "t": "__ICON-CALL__", "user_id": client.user_id,
                 "chat_id": room, "username": client.user})

    async def _leave_room(self, client: ClientInfo):
        if not client.room:
            print("Клиент уже вышел")
            return
        room = client.room
        lst = self.rooms.get(room, [])
        if client in lst:
            lst.remove(client)
            print(f"[TCP] {client.addr_str()} вышел из комнаты '{room}', участников={len(lst)}")

            await self._send_service_msg(obj={"g": "CLIENT", "t": "__LEFT-ICON-CALL__",
                                              "user_id": client.user_id, "chat_id": room})
            await self._broadcast_room(room, {"t": "peer_left", "client": client.to_dict()}, skip=client)
        token = client.token
        self.client_by_token.pop(token, None)

        # чистка комнаты если пустая
        if not lst:
            self.rooms.pop(room, None)
        client.room = None

    async def _broadcast_room(self, room: str, obj: dict, skip: Optional[ClientInfo] = None):
        lst = self.rooms.get(room, [])
        data = (json.dumps(obj) + "\n").encode("utf-8")

        #  Отправляем всем кроме типа который = skip
        for c in list(lst):
            if skip and c is skip:
                continue
            try:
                c.writer.write(data)
                await c.writer.drain()
            except Exception as e:
                print(f"[TCP] ошибка отправки {c.addr_str()}: {e}")

    async def _send(self, client: ClientInfo, obj: dict):
        try:
            client.writer.write((json.dumps(obj) + "\n").encode("utf-8"))
            await client.writer.drain()
        except Exception as e:
            print(f"[TCP] ошибка send {client.addr_str()}: {e}")

    async def _send_service_msg(self, obj: dict):
        try:
            self.service_writer.write((json.dumps(obj) + "\n").encode("utf-8"))
            await self.service_writer.drain()
        except Exception as e:
            print(f"[TCP] ошибка _send_service_msg {self.service_writer}: {e}")

    async def connect_service_server(self, host, port):
        """Асинхронное подключение к внешнему сервисному серверу"""
        try:
            reader, writer = await asyncio.open_connection(host, port)
            self.service_reader = reader
            self.service_writer = writer
            print(f"[SERVICE] Подключен к сервисному серверу {host}:{port}")

            # Фоновая задача на прослушивание входящих сообщений
            asyncio.create_task(self._listen_service())
        except Exception as e:
            print(f"[SERVICE] Ошибка подключения: {e}")

    async def _listen_service(self):
        try:
            while True:
                line = await self.service_reader.read(1024)
                if not line:
                    break
                msg = line.decode('utf-8')

                if msg == "DISCOVER":
                    obj = {'t': 'VOICE-SERVER'}
                    await self._send_service_msg(obj)
                    continue
                try:
                    data = json.loads(msg)
                    print("[SERVICE] Получено:", data)
                    # Тут можно добавить вызов нужных стратегий обработки
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            print(f"[SERVICE] Ошибка: {e}")


async def main():
    HOST = "26.36.124.241"
    srv = TcpSignalServer()
    await asyncio.gather(
        srv.serve(HOST, 55559),
        srv.connect_service_server(HOST, 55571),
        srv.udp_loop(),
    )


if __name__ == "__main__":
    asyncio.run(main())
