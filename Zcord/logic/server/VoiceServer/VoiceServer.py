import asyncio
import json
import datetime
import time


# Простейший UDP-сервер сигнализации и обмена peer-адресами.
# Протокол сообщений (JSON, в каждом datagram):
#  - {"t":"register","room":"<room_id>","token":"<client_token>"}
#  - {"t":"peer","addr":["ip",port]} — ответ с адресом напарника


class UdpSignalServer(asyncio.DatagramProtocol):
    def __init__(self):
        self.transport = None
        self.rooms = {}  # {room_id: {addr: (ip, port), ...}}
        self.last_seen = {}  # [addr, timestamp, room_id]

        asyncio.create_task(self.cleanup_task())

    def connection_made(self, transport):
        self.transport = transport
        print("Старт UDP сигнального сервера")

    def datagram_received(self, data, addr):
        try:
            msg = json.loads(data.decode("utf-8"))
        except Exception:
            return
        typ = msg.get("t")

        self.last_seen[addr] = time.time()
        if typ == "register":
            room = msg.get("room", "default_room")
            token = msg.get("token")
            if not token:
                return

            if room not in self.rooms:
                self.rooms[room] = {}
            lst = self.rooms[room]

            # добавим
            if addr not in lst:
                lst[addr] = token
                print(f"[VoiceServer] {addr} присоединился к комнате {room}, всего участников в комнате={len(lst)}"
                      f" dt={datetime.datetime.now()}")
                print(lst)

            # как только стало двое — рассылаем адреса друг друга
            if len(lst) >= 2:
                # 1) новому клиенту отправляем список всех существующих пиров
                for peer in lst:
                    if peer != addr:
                        self.send_json(addr, {"t": "peer", "addr": peer})

                # 2) всем остальным сообщаем про нового
                for peer in lst:
                    if peer != addr:
                        self.send_json(peer, {"t": "peer", "addr": addr})

        elif typ == "disconnect":
            room = msg.get("room", "default_room")
            token = msg.get("token")

            lst = self.rooms[room]

            if not token:
                return
            if addr in lst and token == lst[addr]:
                del lst[addr]
                del self.last_seen[addr]

                print(f"[VoiceServer] {addr} вышел из комнаты {room}, всего участников в комнате={len(lst)}")
                for peer in lst:
                    self.send_json(peer, {"t": "peer_left", "addr": addr})

        elif typ == "keep_alive":
            room = msg.get("room", "default_room")
            token = msg.get("token")

            lst = self.rooms[room]
            if addr in lst and token == lst[addr]:
                self.last_seen[addr] = time.time()

            print(f"Пришел пакет keep_alive от {addr}")

    def send_json(self, addr, obj):
        try:
            self.transport.sendto(json.dumps(obj).encode("utf-8"), addr)
        except Exception as e:
            print(f"[VoiceServer] send error: {e}")

    async def cleanup_task(self):
        """Периодическая очистка неактивных клиентов"""
        while True:
            now = time.time()
            for addr, ts in list(self.last_seen.items()):
                if now - ts > 20:
                    print(f"[VoiceServer] timeout for {addr}")

            await asyncio.sleep(5)


async def main():
    loop = asyncio.get_running_loop()
    # слушаем на 0.0.0.0:55559/UDP
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UdpSignalServer(),
        local_addr=("0.0.0.0", 55559)
    )
    try:
        await asyncio.Future()
    finally:
        transport.close()

if __name__ == "__main__":
    asyncio.run(main())
