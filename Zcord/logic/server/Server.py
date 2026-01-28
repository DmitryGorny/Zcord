import asyncio
import json
import os
from pathlib import Path
from typing import Dict, Callable
import msgspec
from dotenv import load_dotenv

from logic.server.Service.application.chat.ChatService import ChatService
from logic.server.Service.application.client.ClientService import ClientService
from logic.server.Service.application.friend.FriendshipService import FriendService
from logic.server.Service.core.MessageServiceCommunication.IMessageServiceDispatcher import IMessageServiceDispatcher
from logic.server.Service.core.VideoServerCommunication.IVideoServerDispatcher import IVideoServerDispatcher
from logic.server.Service.infrastructure.MessageServiceCommunication.MessageServiceDispatcher import \
    MessageServiceDispatcher
from logic.server.Service.infrastructure.VideoServerCommunication.VideoServerDispathcer import \
    VideoServerDispatcher
from logic.server.Service.infrastructure.repositories.chat.ChatDBRepo import ChatDBRepo
from logic.server.Service.infrastructure.repositories.chat.ChatRepo import ChatRepo
from logic.server.Service.infrastructure.repositories.client.ClientDBRepo import ClientDBRepo
from logic.server.Service.infrastructure.repositories.client.ClientRepo import ClientRepo
from logic.server.Service.infrastructure.repositories.friend.FriendDBRepo import FriendDBRepo
from logic.server.Service.infrastructure.repositories.friend.FriendRepo import FriendRepo
from logic.server.Service.infrastructure.strats.client.ClientStrats import UserInfoStrat
from logic.server.Service.infrastructure.strats.strats_choose.ChooseStrategy import ChooseStrategy


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class OnionHandler(metaclass=SingletonMeta):
    def __init__(self):  # TODO: Сделать фабрику
        self._message_service_dispatcher: IMessageServiceDispatcher = MessageServiceDispatcher()
        self._video_server_dispatcher: IVideoServerDispatcher = VideoServerDispatcher()
        # Все репозитории
        self._repositories = {'client_repo': ClientRepo(self._message_service_dispatcher),
                              'chat_repo': ChatRepo(),
                              'friend_repo': FriendRepo(),
                              'client_db_repo': ClientDBRepo(),
                              'chat_db_repo': ChatDBRepo(),
                              'friend_db_repo': FriendDBRepo()}

        # Все сервисы
        self._services = {'client_service': ClientService(client_repo=self._repositories['client_repo'],
                                                          chat_repo=self._repositories['chat_repo'],
                                                          friend_repo=self._repositories['friend_repo']),
                          'friend_service': FriendService(client_repo=self._repositories['client_repo'],
                                                          chat_repo=self._repositories['chat_repo'],
                                                          friend_repo=self._repositories['friend_repo'],
                                                          chat_db_rp=self._repositories['chat_db_repo'],
                                                          client_db_rp=self._repositories['client_db_repo'],
                                                          friend_db_rp=self._repositories['friend_db_repo'],
                                                          msg_communication=self._message_service_dispatcher),
                          'chat_service': ChatService(client_repo=self._repositories['client_repo'],
                                                      chat_repo=self._repositories['chat_repo'],
                                                      chat_db_rp=self._repositories['chat_db_repo'],
                                                      client_db_repo=self._repositories['client_db_repo'],
                                                      msg_communication=self._message_service_dispatcher,
                                                      video_communication=self._video_server_dispatcher)}

        self._choose_strategy = ChooseStrategy(client_service=self._services['client_service'],
                                               friend_service=self._services['friend_service'],
                                               chat_service=self._services['chat_service'])

    def define_message_communication(self, func: Callable) -> None:
        self._message_service_dispatcher.define_sender_func(func)

    def define_video_communication(self, func: Callable) -> None:
        self._video_server_dispatcher.define_sender_func(func)


    def choose_strategy(self, group_name, command):
        return self._choose_strategy.get_strategy(group_name, command)


class Server:
    servers: Dict[str, asyncio.StreamWriter] = {
        "message-server": None,
        "voice-server": None
    }

    def __init__(self):
        self._onion_handler = OnionHandler()

    def server_connected(self, server_name: str, writer: asyncio.StreamWriter):
        # TODO: Переписать с Enum
        Server.servers[server_name] = writer

        if server_name == 'message-server':
            self._onion_handler.define_message_communication(self.send_decorator(Server.servers["message-server"]))
        elif server_name == 'video-server':
            self._onion_handler.define_video_communication(self.send_decorator(Server.servers["video-server"]))
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
                "msg_type": msg_type
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
                    try:
                        msg_type = msg["msg_type"]
                        group_name = msg['group']
                        strategy = self._onion_handler.choose_strategy(group_name=group_name, command=msg_type)
                        if isinstance(strategy, UserInfoStrat):
                            msg['writer'] = writer
                        print(msg)
                        await strategy.execute(msg)
                    except KeyError as e:
                        print('[Server(client_tcp)] Ошибка: {}'.format(e))
                    continue
            except ConnectionResetError:
                break


class ServersHandler:
    def __init__(self, server_connected_signal: Callable):
        self._servers: Dict[str, asyncio.StreamWriter | None] = {'message-server': None,
                                                                 'voice-server': None,
                                                                 'video-server': None}

        self._server_connected = server_connected_signal

        self._onion_handler = OnionHandler()

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
                    print("[Server(servers_tcp)] Подключен message")
                    continue
                elif typ == 'VOICE-SERVER':
                    self._servers["voice-server"] = writer
                    print("[Server(servers_tcp)] Подключен voice")
                    self._server_connected("voice-server", writer)
                    continue
                elif typ == 'VIDEO-SERVER':
                    self._servers["video-server"] = writer
                    print("[Server(servers_tcp)] Подключен video")
                    self._server_connected("video-server", writer)
                    continue
                group_name = msg.get("g")
                strategy = self._onion_handler.choose_strategy(group_name=group_name, command=typ)
                try:
                    await strategy.execute(msg)
                except Exception as e:
                    print(print('[Server(servers_tcp)] Ошибка: {}'.format(e)))

            except ConnectionResetError:
                writer.close()
                print("[Server(servers_tcp)] Отключён")
                break


class Runner:
    def __init__(self):
        self._servers_handler = ServersHandler(server_connected_signal=self.server_connected)
        self._service_server = Server()

    def server_connected(self, server_name: str, writer: asyncio.StreamWriter):
        self._service_server.server_connected(server_name, writer)

    async def main(self):
        BASE_DIR = Path(__file__).resolve().parent
        dotenv_path = os.path.join(BASE_DIR, '.env')
        load_dotenv(dotenv_path)
        IP = os.environ.get("HOST")
        PORT_FOR_USERS = int(os.environ.get("SERVICE_PORT_FOR_USERS"))

        server_user = await asyncio.start_server(
            lambda r, w: self._service_server.handle(r, w),
            IP,
            PORT_FOR_USERS,
            reuse_address=True,
        )

        PORT_FOR_MESSAGE = int(os.environ.get("SERVICE_PORT_FOR_MESSAGE"))
        PORT_FOR_VOICE = int(os.environ.get("SERVICE_PORT_FOR_VOICE"))
        PORT_FOR_VIDEO = int(os.environ.get("SERVICE_PORT_FOR_VIDEO"))

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

        server_video_service = await asyncio.start_server(
            lambda r, w: self._servers_handler.handle_server(r, w),
            IP,
            PORT_FOR_VIDEO
        )

        async with server_message_service, server_voice_service, server_user:
            await asyncio.gather(
                server_message_service.serve_forever(),
                server_voice_service.serve_forever(),
                server_video_service.serve_forever(),
                server_user.serve_forever()
            )


asyncio.run(Runner().main())
