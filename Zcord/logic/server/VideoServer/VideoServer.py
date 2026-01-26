import asyncio
import json
import logging
import uuid
from aiohttp import web, WSMsgType

logging.basicConfig(level=logging.INFO)


class TcpSignalServer:
    def __init__(self, out_queue):
        self.out_queue = out_queue

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
                    obj = {'t': 'VIDEO-SERVER'}
                    await self._send_service_msg(obj)
                    continue
                try:
                    # Все остальные сообщения с сигнального сервера
                    data = json.loads(msg)
                    print("[SERVICE] Получено:", data)

                    await self.out_queue.put(msg)

                except json.JSONDecodeError:
                    pass
        except Exception as e:
            print(f"[SERVICE] Ошибка: {e}")

    async def _send_service_msg(self, obj: dict):
        try:
            self.service_writer.write((json.dumps(obj) + "\n").encode("utf-8"))
            await self.service_writer.drain()
        except Exception as e:
            print(f"[TCP] ошибка _send_service_msg {self.service_writer}: {e}")

    async def close(self):
        self.service_writer.close()
        # TODO надо ли закрывать reader?


async def on_startup(app):
    HOST = "26.36.124.241"

    app["rooms"] = {}  # room_id -> {peer_id: ws}
    app["tcp_queue"] = asyncio.Queue()
    app["tcp_srv"] = TcpSignalServer(app["tcp_queue"])
    app["pending_ws"] = set()
    app["tcp_task"] = asyncio.create_task(
        app["tcp_srv"].connect_service_server(HOST, 55572)
    )

    app["dispatcher_task"] = asyncio.create_task(
        tcp_to_ws_dispatcher(app)
    )

    logging.info("Подключен к сигнальному серверу")


async def tcp_to_ws_dispatcher(app):
    queue = app["tcp_queue"]
    rooms = app["rooms"]

    while True:
        msg = await queue.get()

        # { "peer": "abc", "room": "room42", "payload": {...} }
        room = msg.get("room")
        peer = msg.get("peer")

        if room:
            for ws in list(app["pending_ws"]):
                ws.room_id = room
                rooms.setdefault(room, {})[ws.peer_id] = ws
                app["pending_ws"].remove(ws)

                await ws.send_json({
                    "type": "assign-room",
                    "room": room
                })

                logging.info(f"Назначена комната {room} для пира {peer}: {ws.peer_id}")

        if room not in rooms:
            continue

        for ws in rooms[room].values():
            try:
                await ws.send_json({
                    "type": "tcp-message",
                    "payload": msg
                })
            except Exception as e:
                print("WS send error:", e)


async def on_shutdown(app):
    app["tcp_task"].cancel()
    app["dispatcher_task"].cancel()

    await app["tcp_srv"].close()

    for room in app["rooms"].values():
        for ws in room.values():
            await ws.close()

    logging.info("Подключение к сигнальному серверу закрыто")


async def websocket_handler(request):
    app = request.app
    rooms = app["rooms"]

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    peer_id = uuid.uuid4().hex
    room_id = request.query.get("room")

    ws.peer_id = peer_id
    ws.room_id = room_id

    if room_id:
        rooms.setdefault(room_id, {})[peer_id] = ws
        logging.info(f"Client {peer_id} joined room {room_id}")

        for pid in rooms.get(room_id, []):
            try:
                if pid != peer_id:
                    await ws.send_json({
                        "type": "peer-joined",
                        "peerId": pid
                    })
            except Exception as e:
                print(f"[VideoServer] Ошибка отправления: {e}")
    else:
        app["pending_ws"].add(ws)
        logging.info(f"Client {peer_id} ожидает назначения комнаты")

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                data = json.loads(msg.data)

                target = data.get("target")
                if not target or not ws.room_id:
                    continue

                data["from"] = peer_id
                await rooms[ws.room_id][target].send_json(data)
    finally:
        app["pending_ws"].discard(ws)

        if ws.room_id and ws.room_id in rooms:
            rooms[ws.room_id].pop(peer_id, None)
            for peer_ws in rooms[ws.room_id].values():
                try:
                    await peer_ws.send_json({
                        "type": "peer-left",
                        "peerId": peer_id
                    })
                except Exception as e:
                    print(f"[VideoServer] Ошибка отправления: {e}")
        logging.info(f"Client left room: {room_id}")

    return ws


async def index(request):
    with open("web/index.html", "r", encoding="utf-8") as f:
        return web.Response(content_type="text/html", text=f.read())


if __name__ == "__main__":
    app = web.Application()
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    app.router.add_get("/", index)
    app.router.add_get("/ws", websocket_handler)
    web.run_app(app, host="localhost", port=8080)
