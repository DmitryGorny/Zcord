import json
import logging
import uuid
from aiohttp import web, WSMsgType

logging.basicConfig(level=logging.INFO)

rooms = {}  # {room_id: {peer_id: ws, ...}, room_id2: {...}, ...}


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    peer_id = uuid.uuid4().hex
    room_id = request.query.get("room", "default")

    if room_id not in rooms:
        rooms[room_id] = {}

    rooms[room_id][peer_id] = ws

    logging.info(f"Client joined room: {room_id}")

    for pid in rooms.get(room_id, []):
        try:
            if pid != peer_id:
                await ws.send_json({
                    "type": "peer-joined",
                    "peerId": pid
                })
        except Exception as e:
            print(f"[VideoServer] Ошибка отправления: {e}")

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                data = json.loads(msg.data)

                target = data.get("target")
                if not target:
                    continue

                data["from"] = peer_id
                await rooms[room_id][target].send_json(data)
    finally:
        del rooms[room_id][peer_id]
        logging.info(f"Client left room: {room_id}")
        for peer_ws in rooms[room_id].values():
            try:
                await peer_ws.send_json({
                    "type": "peer-left",
                    "peerId": peer_id
                })
            except Exception as e:
                print(f"[VideoServer] Ошибка отправления: {e}")

    return ws


async def index(request):
    with open("web/index.html", "r", encoding="utf-8") as f:
        return web.Response(content_type="text/html", text=f.read())


app = web.Application()
app.router.add_get("/", index)
app.router.add_get("/ws", websocket_handler)


if __name__ == "__main__":
    web.run_app(app, host="localhost", port=8080)
