import asyncio
import json


class VoiceServer:
    def __init__(self):
        self.clients = {}  # {client_id: {"writer": writer, "pc": pc}}
        self.rooms = {}    # {room_id: [client_id1, client_id2]}

    async def handle_connection(self, reader, writer):
        client_id = writer.get_extra_info('peername')  # Уникальный ID для клиента
        self.clients[client_id] = {"writer": writer}
        print(f"Новый клиент: {client_id}")

        try:
            while True:
                data = await reader.read(4096)
                if not data:
                    break

                message = json.loads(data.decode())
                print(f"Сообщение от {client_id}: {message['type']}")

                if message["type"] == "join":
                    room_id = message["room_id"]
                    if room_id not in self.rooms:
                        self.rooms[room_id] = []
                    self.rooms[room_id].append(client_id)
                    print(f"Клиент {client_id} вошёл в комнату {room_id}")

                    # Если в комнате уже есть кто-то, начинаем соединение
                    if len(self.rooms[room_id]) == 2:
                        other_client_id = self.rooms[room_id][0]
                        await self.send_message(other_client_id, {
                            "type": "wait_peer"
                        })

                elif message["type"] == "offer":
                    room_id = message["room_id"]
                    other_client_id = self.rooms[room_id][0] if self.rooms[room_id][0] != client_id else self.rooms[room_id][1]
                    await self.send_message(other_client_id, {
                        "type": "offer",
                        "sdp": message["sdp"],
                        "room_id": room_id
                    })

                elif message["type"] == "answer":
                    room_id = message["room_id"]
                    other_client_id = self.rooms[room_id][0] if self.rooms[room_id][0] != client_id else self.rooms[room_id][1]
                    await self.send_message(other_client_id, {
                        "type": "answer",
                        "sdp": message["sdp"],
                        "room_id": room_id
                    })

                elif message["type"] == "candidate":
                    room_id = message["room_id"]
                    other_client_id = self.rooms[room_id][0] if self.rooms[room_id][0] != client_id else self.rooms[room_id][1]
                    await self.send_message(other_client_id, {
                        "type": "candidate",
                        "candidate": message["candidate"],
                        "room_id": room_id
                    })

        except Exception as e:
            print(f"Ошибка у {client_id}: {e}")
        finally:
            print(f"Клиент отключён: {client_id}")
            if client_id in self.clients:
                del self.clients[client_id]
            writer.close()
            await writer.wait_closed()

    async def send_message(self, client_id, message):
        if client_id in self.clients:
            writer = self.clients[client_id]["writer"]
            writer.write(json.dumps(message).encode())
            await writer.drain()


async def main():
    server = VoiceServer()
    voice_service = await asyncio.start_server(
        server.handle_connection,
        "0.0.0.0", 55559
    )

    async with voice_service:
        await voice_service.serve_forever()

asyncio.run(main())
