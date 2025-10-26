import asyncio
import json
import logging
from aiohttp import web, WSMsgType

logging.basicConfig(level=logging.INFO)

rooms = {}  # {room_id: [websocket1, websocket2, ...]}

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    room_id = request.query.get("room", "default")
    if room_id not in rooms:
        rooms[room_id] = []
    rooms[room_id].append(ws)

    logging.info(f"Client joined room: {room_id}")

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                data = json.loads(msg.data)

                # Рассылаем всем, кроме отправителя
                for peer in rooms[room_id]:
                    if peer is not ws:
                        await peer.send_json(data)
            elif msg.type == WSMsgType.ERROR:
                logging.error(f"WebSocket error: {ws.exception()}")
    finally:
        rooms[room_id].remove(ws)
        logging.info(f"Client left room: {room_id}")

        for peer in rooms.get(room_id, []):
            try:
                await peer.send_json({"type": "peer-left"})
            except Exception:
                pass

    return ws


async def index(request):
    with open("web/index.html", "r", encoding="utf-8") as f:
        return web.Response(content_type="text/html", text=f.read())


app = web.Application()
app.router.add_get("/", index)
app.router.add_get("/ws", websocket_handler)


if __name__ == "__main__":
    logging.info("Starting WebRTC signaling server on http://26.36.207.48:8080")
    web.run_app(app, host="26.36.207.48", port=8080, ssl_context="26-36.207.48.crt")
