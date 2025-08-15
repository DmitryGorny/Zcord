import asyncio
import json

class VoiceServer:
    def __init__(self):
        self.clients = {}  # {client_id: {"writer": writer, "ready": False}}
        self.rooms = {}    # {room_id: [client_id1, client_id2]}

    async def handle_connection(self, reader, writer):
        client_id = writer.get_extra_info('peername')
        self.clients[client_id] = {"writer": writer, "ready": False}
        print(f"Новый клиент: {client_id}")

        try:
            while True:
                data = await reader.read(4096)
                if not data:
                    break

                message = json.loads(data.decode())
                msg_type = message.get("type")
                print(f"Сообщение от {client_id}: {msg_type}")

                if msg_type == "join":
                    room_id = message["room_id"]
                    self.rooms.setdefault(room_id, []).append(client_id)
                    print(f"Клиент {client_id} вошёл в комнату {room_id}")

                    if len(self.rooms[room_id]) == 2:
                        other_client_id = self.rooms[room_id][0]
                        await self.send_message(other_client_id, {"type": "wait_peer"})

                elif msg_type in ("offer", "answer", "candidate"):
                    room_id = message["room_id"]
                    other_client_id = self.get_other_client(room_id, client_id)
                    await self.send_message(other_client_id, message)

                elif msg_type == "ready_for_voice":
                    self.clients[client_id]["ready"] = True
                    room_id = message["room_id"]
                    await self.check_and_start_voice(room_id)

        except Exception as e:
            print(f"Ошибка у {client_id}: {e}")
        finally:
            print(f"Клиент отключён: {client_id}")
            self.remove_client(client_id)
            writer.close()
            await writer.wait_closed()

    def get_other_client(self, room_id, client_id):
        clients = self.rooms.get(room_id, [])
        return clients[0] if clients and clients[0] != client_id else clients[1]

    def remove_client(self, client_id):
        self.clients.pop(client_id, None)
        for room_id, members in list(self.rooms.items()):
            if client_id in members:
                members.remove(client_id)
                if not members:
                    del self.rooms[room_id]

    async def send_message(self, client_id, message):
        if client_id in self.clients:
            writer = self.clients[client_id]["writer"]
            writer.write(json.dumps(message).encode())
            await writer.drain()

    async def check_and_start_voice(self, room_id):
        members = self.rooms.get(room_id, [])
        if len(members) == 2 and all(self.clients[m]["ready"] for m in members):
            print(f"Оба клиента в комнате {room_id} готовы, отправляем start_voice")
            for m in members:
                await self.send_message(m, {"type": "start_voice"})
            # Сбрасываем ready, чтобы не переслать снова
            for m in members:
                self.clients[m]["ready"] = False


async def main():
    server = VoiceServer()
    voice_service = await asyncio.start_server(
        server.handle_connection,
        "0.0.0.0", 55559
    )
    async with voice_service:
        await voice_service.serve_forever()

asyncio.run(main())
