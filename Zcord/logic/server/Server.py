import asyncio
import json
from typing import Dict, Callable
import msgspec
from logic.server.Service.application.client.ClientService import ClientService
from logic.server.Service.core.MessageServiceCommunication.IMessageServiceDispatcher import IMessageServiceDispatcher
from logic.server.Service.infrastructure.MessageServiceCommunication.MessageServiceDispatcher import \
    MessageServiceDispatcher
from logic.server.Service.infrastructure.repositories.chat.ChatRepo import ChatRepo
from logic.server.Service.infrastructure.repositories.client.ClientRepo import ClientRepo
from logic.server.Service.infrastructure.repositories.friend.FriendRepo import FriendRepo
from logic.server.Service.infrastructure.strats.strats_choose.ChooseStrategy import ChooseStrategy
from logic.server.StrategyForServiceServer.ServiceServersStrats import ChooseServerStrategy


class Server:
    servers: Dict[str, asyncio.StreamWriter] = {
        "message-server": None,
        "voice-server": None
    }

    def __init__(self):
        self._message_service_dispatcher: IMessageServiceDispatcher = MessageServiceDispatcher()
        # Все репозитории
        self._repositories = {'client_repo': ClientRepo(self._message_service_dispatcher),
                              'chat_repo': ChatRepo(),
                              'friend_repo': FriendRepo()}

        # Все сервисы
        self._services = {'client_service': ClientService(client_repo=self._repositories['client_repo'],
                                                          chat_repo=self._repositories['chat_repo'],
                                                          friend_repo=self._repositories['friend_repo'])}

        self._choose_strategy = ChooseStrategy(client_service=self._services['client_service'],
                                               friend_service=None,
                                               chat_service=None)

    def server_connected(self, server_name: str, writer: asyncio.StreamWriter):
        # TODO: Переписать с Enum
        Server.servers[server_name] = writer

        if server_name == 'message-server':
            self._message_service_dispatcher.define_sender_func(self.send_decorator(Server.servers["message-server"]))

    async def create_task(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        await self.handle(reader, writer)

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
                    type = msg["msg_type"]
                    group_name = msg['group']

                    strategy = self._choose_strategy.get_strategy(group_name=group_name, command=type)
                    try:
                        await strategy.execute(msg)
                    except AttributeError as e:
                        print(e)
                    continue

            except ConnectionResetError:
                break


class ServersHandler:
    def __init__(self, server_connected_signal: Callable):
        self._servers: Dict[str, asyncio.StreamWriter | None] = {'message-server': None,
                                                                 'voice-server': None}

        self._server_connected = server_connected_signal

    async def task_creator(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        await self.handle_server(reader, writer)

    async def handle_server(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        writer.write(b'DISCOVER')  # Запрос на информацию о сервере
        await writer.drain()
        while True:
            try:
                msg = await reader.read(4096)
                msg = json.loads(msg.decode("utf-8"))

                typ = msg.get("t")

                if typ == 'MESSAGE-SERVER':
                    self._servers["message-server"] = writer
                    self._server_connected('message-server', writer)
                    print("Подключен message")
                    continue
                elif typ == 'VOICE-SERVER':
                    self._servers["voice-server"] = writer
                    print("Подключен voice")
                    self._server_connected("voice-server", writer)
                    continue

                try:
                    strategy = ChooseServerStrategy().get_strategy(typ, Server)
                    await strategy.execute(msg)
                except Exception as e:
                    print(e)

            except ConnectionResetError:
                writer.close()
                print("Отключён")
                break


class Runner:
    def __init__(self):
        self._servers_handler = ServersHandler(server_connected_signal=self.server_connected)
        self._service_server = Server()

    def server_connected(self, server_name: str, writer: asyncio.StreamWriter):
        self._service_server.server_connected(server_name, writer)

    async def main(self):
        IP = "26.181.96.20"
        PORT_FO_USERS = 55558

        server_user = await asyncio.start_server(
            lambda r, w: self._service_server.handle(r, w),
            IP,
            PORT_FO_USERS,
            reuse_address=True,
        )

        PORT_FOR_MESSAGE = 55569
        PORT_FOR_VOICE = 55571

        server_message_service = await asyncio.start_server(
            lambda r, w: self._servers_handler.handle_server(r, w),
            IP,
            PORT_FOR_MESSAGE
        )

        server_voice_service = await asyncio.start_server(
            lambda r, w: self._servers_handler.handle_server(r, w),
            IP,
            PORT_FOR_VOICE
        )

        async with server_message_service, server_voice_service, server_user:
            await asyncio.gather(
                server_message_service.serve_forever(),
                server_voice_service.serve_forever(),
                server_user.serve_forever()
            )


asyncio.run(Runner().main())
