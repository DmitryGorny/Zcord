import asyncio
import json
import datetime
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# Протокол сообщений по TCP (NDJSON: JSON + "\n"):
# 1) Регистрация/вход в комнату:
#    {"t":"join_room","room":"room1","token":"<uuid>","user":"user1","udp_port":54321}
#
# 2) Сервер сообщает о найденном пиро(ах):
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
        # комнаты: room -> список клиентов
        self.rooms: Dict[str, List[ClientInfo]] = {}
        # быстрый поиск по writer
        self.client_by_writer: Dict[asyncio.StreamWriter, ClientInfo] = {}

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
                print(msg)
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
            except Exception:
                pass
            self.client_by_writer.pop(writer, None)

    async def handle_message(self, client: ClientInfo, msg: dict):
        typ = msg.get("t")
        print(msg)
        if typ == "join_room":
            await self._join_room(client, msg)
        elif typ == "leave":  # btw информационное сообщение, что с ним делать не ебу, управление всё равно отдаётся finally
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

    async def _join_room(self, client: ClientInfo, msg: dict):
        room = msg.get("room") or "default_room"
        user_id = msg.get("user_id")
        token = msg.get("token")
        user = msg.get("user")
        udp_port = msg.get("udp_port")

        client.user_id = user_id
        client.room = room
        client.token = token
        client.user = user
        client.udp_port = udp_port

        lst = self.rooms.setdefault(room, [])

        if client not in lst:
            lst.append(client)

        print(f"[TCP] {client.addr_str()} присоединился к комнате '{room}', участников={len(lst)}")

        # Новому клиенту отправляем список уже присутствующих пиров
        if len(lst) >= 2:
            peers_dicts = [c.to_dict() for c in lst if c != client]
            await self._send(client, {"t": "peer", "client": peers_dicts})

        # И существующим участникам разошлём адрес нового
        await self._broadcast_room(room, {"t": "peer", "client": [client.to_dict()]}, skip=client)

    async def _leave_room(self, client: ClientInfo):
        if not client.room:
            print("Клиент уже вышел")
            return
        room = client.room
        lst = self.rooms.get(room, [])
        if client in lst:
            lst.remove(client)
            print(f"[TCP] {client.addr_str()} вышел из комнаты '{room}', участников={len(lst)}")

            await self._broadcast_room(room, {"t": "peer_left", "client": client.to_dict()}, skip=client)

        # чистка комнаты если пустая TODO: Не знаю нужно ли??
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


async def main():
    srv = TcpSignalServer()
    await srv.serve("26.36.124.241", 55559)

if __name__ == "__main__":
    asyncio.run(main())
