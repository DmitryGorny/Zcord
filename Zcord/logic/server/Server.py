import asyncio
import json
from typing import Dict

import msgspec
import re
from logic.server.Client.Client import Client
from logic.server.StrategyForServiceServer.ServeiceStrats import ChooseStrategy, UserInfoStrat


class Server:
    clients: Dict[str, Client] = {}
    servers: Dict[str, asyncio.StreamWriter] = {
        "message-server": None,
        "voice-server": None
    }

    def deserialize(self, msg):
        cache = msgspec.json.decode(msg)
        return cache
    @staticmethod
    def serialize(data):
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

    @staticmethod
    def decode_multiple_json_objects(data):
        decoder = json.JSONDecoder()
        idx = 0
        results = []
        while idx < len(data):
            try:
                obj, idx_new = decoder.raw_decode(data[idx:])
                results.append(obj)
                idx += idx_new
            except json.JSONDecodeError:
                idx += 1
        return results

    async def handle(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        # Этот урод может не кидать исключения в процесе выполнения, только после KeyboardInterrupt
        send_to_message_server = self.send_decorator(Server.servers["message-server"])
        writer.write(json.dumps({"message_type": '__USER-INFO__'}).encode('utf-8'))
        await writer.drain()
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
                    message = msg["msg_type"]
                    strategy = ChooseStrategy().get_strategy(message, send_to_message_server, Server)
                    if isinstance(strategy, UserInfoStrat):
                        msg['writer'] = writer
                    try:
                        await strategy.execute(msg)
                    except AttributeError as e:  # Пока чисто для отладки, т.к. незнакомых команд быть не может????
                        print(e)
                    continue

            except ConnectionResetError:
                break

    async def handle_server(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Сокет обрабатывающий подключение серверов"""
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
