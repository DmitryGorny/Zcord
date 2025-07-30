import asyncio
import copy
import json
import msgspec
import re
import socket
from logic.server.StrategyForService.ServeiceStrats import ChooseStrategy


class Client:
    def __init__(self, nick, writer: asyncio.StreamWriter):
        self.nick = nick
        self._writer = writer
        self.activtyStatus = None
        self.__friends = None
        self.__message_chat_id = 0 #id чата, в котором сейчас пользователь (аналог old_chat_code из message_server)

    @property
    def message_chat_id(self) -> int:
        return self.__message_chat_id
    @message_chat_id.setter
    def message_chat_id(self, val: int) -> None:
        self.__message_chat_id = val
    @property
    def friends(self) -> dict:
        return self.__friends

    @friends.setter
    def friends(self, friends: dict) -> None:
        self.__friends = friends

    @property
    def writer(self) -> asyncio.StreamWriter:
        return self._writer

    def add_friend(self, freind_name: str, chat_id: int) -> None:
        self.__friends[freind_name] = [chat_id, 1] #1 - статус друга (по дефолту стоит заявка в друзья)

    def delete_friend(self, friend_name: str) -> None:
        del self.__friends[friend_name]

    @property
    def status(self):
        return self.activtyStatus

    @status.setter
    def status(self, status):
        self.activtyStatus = status

    async def send_message(self, mes_type: str, mes_data: dict) -> None:
        message_header = {
            "message_type": mes_type,
        }
        message = message_header | mes_data
        self._writer.write(json.dumps(message).encode('utf-8'))
        await self._writer.drain()


class Server:
    clients = {}
    servers = {
            "message-server": None,
            "voice-server": None
            }

    nicknames_in_chats = {}
    cache_chat = {}

    def deserialize(self, msg):
        cache = msgspec.json.decode(msg)
        return cache

    def serialize(self, data):
        ser = msgspec.json.encode(data)
        return ser

    @staticmethod
    def copy_nicknames_in_chat(chats):
        Server.nicknames_in_chats = {**copy.deepcopy(chats), **Server.nicknames_in_chats}

    def send_decorator(self, server: asyncio.StreamWriter):
        server_obj = server
        async def send_data_to_server(msg_type, data):
            message = {
                "message": data,
                "type": msg_type
            }

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
        #Этот урод может не кидать исключения в процесе выполнения, только после KeyboardInterrupt
        first_info = await self.settle_first_info(reader, writer)
        await self.get_client_info(reader, writer)
        nickname = first_info[1]
        chats = first_info[0]
        client_obj = Server.clients[nickname]
        Server.copy_nicknames_in_chat(chats)
        await client_obj.send_message("__CONNECT__", {
            "connect": 1
        })
        await self.send_status(nickname)
        await self.get_friends_statuses(nickname)
        send_to_message_server = self.send_decorator(Server.servers["message-server"]) #Чтобы не насиловать голову и
                                                                                          # не обращаться каждый раз к Server.servers
        client_ip = writer.transport.get_extra_info('socket').getpeername()
        await send_to_message_server("USER-INFO", f"{nickname}&-&{self.serialize(first_info[0]).decode('utf-8')}&-&{self.serialize({nickname:client_ip[0]}).decode('utf-8')}")


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
                    nickname = msg["nickname"]
                    strategy = ChooseStrategy().get_strategy(message, send_to_message_server, Server)
                    try:
                        await strategy.execute(msg)
                    except AttributeError as e: #Пока чисто для отладки, т.к. незнакомых команд быть не может????
                        print(e)
                    continue

            except ConnectionResetError:
                break

    async def handle_server(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        writer.write(b'DISCOVER') #Запрос на информацию о сервере
        while True:
            try:
                msg = await reader.read(4096)
                msg = msg.decode('utf-8')
                if msg == 'MESSAGE-SERVER':
                    Server.servers["message-server"] = writer
                    continue

            except ConnectionResetError:
                writer.close()
                break

    async def settle_first_info(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        writer.write(json.dumps({"message_type": '__NICK__'}).encode('utf-8'))
        await writer.drain()
        msg = await reader.read(4096)
        msg = json.loads(msg)

        nickname = msg["nickname"]
        chat_id = self.deserialize(msg["message"])

        print(f"Nickname is {nickname}")
        return [chat_id, nickname]

    async def get_client_info(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        writer.write(json.dumps({"message_type": '__USER-INFO__'}).encode('utf-8'))
        msg = await reader.read(1024)
        msg = json.loads(msg)
        nickname = msg["nickname"]
        msg = json.loads(msg["message"])
        clientObj = Client(nickname, writer)
        clientObj.friends = msg["friends"]
        clientObj.status = msg["status"]
        Server.clients[nickname] = clientObj

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
    IP = "26.181.96.20"
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
