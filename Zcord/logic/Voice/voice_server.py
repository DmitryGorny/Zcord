import asyncio
import json

# Простейший UDP-сервер сигнализации и обмена peer-адресами.
# Протокол сообщений (JSON, в каждом datagram):
#  - {"t":"register","room":"<room_id>","token":"<client_token>"}
#  - {"t":"peer","addr":["ip",port]} — ответ с адресом напарника

class UdpSignalServer(asyncio.DatagramProtocol):
    def __init__(self):
        self.transport = None
        # room_id -> list of dicts: {"token": str, "addr": (ip, port)}
        self.rooms = {}

    def connection_made(self, transport):
        self.transport = transport
        print("UDP signal server started")

    def datagram_received(self, data, addr):
        try:
            msg = json.loads(data.decode("utf-8"))
        except Exception:
            return
        typ = msg.get("t")
        if typ == "register":
            room = msg.get("room", "default_room")
            token = msg.get("token")
            if not token:
                return

            lst = self.rooms.setdefault(room, [])
            # обновим/добавим
            for e in lst:
                if e["token"] == token:
                    e["addr"] = addr
                    break
            else:
                lst.append({"token": token, "addr": addr})

            print(f"[{room}] register from {addr}, total={len(lst)}")

            # как только стало двое — рассылаем адреса друг друга
            if len(lst) >= 2:
                a, b = lst[0], lst[1]
                self.send_peer(a["addr"], b["addr"])
                self.send_peer(b["addr"], a["addr"])

        # можно расширять протокол по необходимости

    def send_peer(self, to_addr, peer_addr):
        payload = json.dumps({"t": "peer", "addr": [peer_addr[0], peer_addr[1]]}).encode("utf-8")
        self.transport.sendto(payload, to_addr)

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
