import asyncio
import copy
import json
from typing import Dict, List

import msgspec
import re
from logic.server.Client.Client import Client
from logic.server.StrategyForServiceServer.ServeiceStrats import ChooseStrategy


class Server:
    clients: Dict[str, Client] = {}
    servers: Dict[str, asyncio.StreamWriter] = {
        "message-server": None,
        "voice-server": None
    }

    def deserialize(self, msg):
        cache = msgspec.json.decode(msg)
        return cache

    def serialize(self, data):
        ser = msgspec.json.encode(data)
        return ser

    def send_decorator(self, server: asyncio.StreamWriter):
        server_obj = server

        async def send_data_to_server(msg_type, mes_data: Dict[str, str]):
            message_header = {
                "type": msg_type
            }
            message = message_header | mes_data

            server_obj.write(json.dumps(message).encode('utf-8'))
            await server_obj.drain()

        return send_data_to_server

    def decode_multiple_json_objects(self, data):
        json_pattern = re.compile(r"\{.*?\}")
        decoded_objects = []
        for match in json_pattern.finditer(data):
            decoded_objects.append(json.loads(match.group()))
        return decoded_objects

    async def handle(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        # Этот урод может не кидать исключения в процесе выполнения, только после KeyboardInterrupt
        first_info = await self.settle_first_info(reader, writer)
        await self.get_client_info(reader, writer)
        user_id = first_info[1]
        chats = first_info[0]
        client_obj = Server.clients[user_id]

        await client_obj.send_message("__CONNECT__", {
            "connect": 1
        })

        send_to_message_server = self.send_decorator(Server.servers["message-server"])

        client_ip = writer.transport.get_extra_info('socket').getpeername()
        await send_to_message_server("USER-INFO", {"serialize_1": self.serialize(chats).decode('utf-8'),
                                                   "serialize_2": self.serialize({'user_id': str(client_obj.id),
                                                                                  "IP": client_ip[0]}).decode('utf-8')})

        while True:
            buffer = ''
            try:
                msg = await reader.read(4096)
                msg = msg.decode('utf-8')
                buffer += msg
                try:
                    arr = self.decode_multiple_json_objects(buffer)
                except json.JSONDecodeError:
                    continue

                for msg in arr:
                    message = msg["message"]
                    strategy = ChooseStrategy().get_strategy(message, send_to_message_server, Server)
                    try:
                        await strategy.execute(msg)
                    except AttributeError as e:  # Пока чисто для отладки, т.к. незнакомых команд быть не может????
                        print(e)
                    continue

            except ConnectionResetError:
                break

    async def handle_server(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        writer.write(b'DISCOVER')  # Запрос на информацию о сервере
        while True:
            try:
                msg = await reader.read(4096)
                msg = msg.decode('utf-8')
                if msg == 'MESSAGE-SERVER':
                    Server.servers["message-server"] = writer
                    continue
                elif msg == 'VOICE-SERVER':
                    Server.servers["voice-server"] = writer
                    print("Подключен войс")
                    continue

            except ConnectionResetError:
                writer.close()
                print("Отключён")
                break

    async def settle_first_info(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        writer.write(json.dumps({"message_type": '__NICK__'}).encode('utf-8'))
        await writer.drain()
        msg = await reader.read(4096)
        msg = json.loads(msg)
        user_id = msg["user_id"]
        chat_id = self.deserialize(msg["message"])

        print(f"user_id is {user_id}")
        return [chat_id, user_id]

    async def get_client_info(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        writer.write(json.dumps({"message_type": '__USER-INFO__'}).encode('utf-8'))
        msg = await reader.read(1024)
        msg = json.loads(msg)
        nickname = msg["nickname"]
        msg = json.loads(msg["message"])
        clientObj = Client(msg["id"], nickname, msg["last_online"], writer)
        clientObj.friends = msg["friends"]
        clientObj.status = msg["status"]
        Server.clients[msg["id"]] = clientObj

    # TODO: Переделать
    async def send_status(self, nickname: str) -> None:
        for friend in Server.clients[nickname].friends.keys():
            if friend not in Server.clients:
                continue

            friend_obj = Server.clients[friend]

            await friend_obj.send_message('USER-STATUS', {
                "user-status": "__USER-ONLINE__",
                "nickname": nickname,
            })

    async def get_friends_statuses(self, nickname: str) -> None:
        for friend in Server.clients[nickname].friends.keys():
            if friend not in Server.clients:
                continue

            await Server.clients[nickname].send_message('USER-STATUS', {
                "user-status": "__USER-ONLINE__",
                "nickname": friend,
            })


async def main():
    IP = "26.36.124.241"
    PORT_FO_USERS = 55558

    server_user = await asyncio.start_server(
        lambda r, w: Server().handle(r, w),
        IP,
        PORT_FO_USERS,
        reuse_address=True,
    )

    PORT_FOR_SERVERS = 55569

    server_service = await asyncio.start_server(
        lambda r, w: Server().handle_server(r, w),
        IP,
        PORT_FOR_SERVERS
    )

    async with server_service, server_user:
        await asyncio.gather(
            server_service.serve_forever(),
            server_user.serve_forever()
        )


asyncio.run(main())
