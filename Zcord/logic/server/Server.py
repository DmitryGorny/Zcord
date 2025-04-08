import asyncio
import copy
import json
import msgspec
import re
import socket

class Client:
    def __init__(self, nick, socket):
        self.nick = nick
        self.writer = socket
        self.activtyStatus = None
        self.__friends = None
        self.__message_chat_id = 0 #id чата, в котором сейчас пользователь (аналог old_chat_code из message_server)

    @property
    def message_chat_id(self) -> int:
        return self.__message_chat_id
    @message_chat_id.setter
    def message_chat_id(self, val:int) -> None:
        self.__message_chat_id = val
    @property
    def friends(self) -> dict:
        return self.__friends
    @friends.setter
    def friends(self, friends: dict) -> None:
        self.__friends = friends

    def add_friend(self, freind_name:str, chat_id:int) -> None:
        self.__friends[freind_name] = [chat_id, 1] #1 - статус друга (по дефолту стоит заявка в друзья)

    def delete_friend(self, friend_name:str) -> None:
        del self.__friends[friend_name]

    @property
    def status(self):
        return self.activtyStatus

    @status.setter
    def status(self, status):
        self.activtyStatus = status

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
    def send_decorator(self, server:asyncio.StreamWriter):
        server_obj = server
        async def send_data_to_server(data):
            server_obj.write(data.encode('utf-8'))
            #await server_obj.drain()

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
        nickname = first_info[1]
        chats = first_info[0]
        Server.copy_nicknames_in_chat(chats)
        await self.get_client_info(reader, writer)
        writer.write(b'0' + '__CONNECT__'.encode('utf-8'))
        send_to_message_server = self.send_decorator(Server.servers["message-server"]) #Чтобы не насиловать голову и
                                                                                          # не обращаться каждый раз к Server.servers
        client_ip = writer.transport.get_extra_info('socket').getpeername()
        await send_to_message_server(f"USER-INFO&-&{nickname}&-&{self.serialize(first_info[0]).decode('utf-8')}&-&{self.serialize({nickname:client_ip[0]}).decode('utf-8')}")

        client_obj = Server.clients[nickname]

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
                    if "__change_chat__" == message:
                        chat_code = msg["chat_id"]
                        nickname = msg["nickname"]
                        if client_obj.message_chat_id == 0:
                            client_obj.message_chat_id = chat_code
                            await send_to_message_server(f"__change_chat__&-&{nickname}&-&{client_obj.message_chat_id}&-&{chat_code}")
                            continue

                        client_chatID = str(client_obj.message_chat_id)
                        if nickname not in Server.nicknames_in_chats[client_chatID]:
                            Server.nicknames_in_chats[client_chatID].append(nickname)

                        try:
                            if chat_code != client_chatID:
                                index = Server.nicknames_in_chats[client_chatID].index(nickname)
                                Server.nicknames_in_chats[client_chatID].pop(index)
                        except UnboundLocalError as e:
                            print(e)
                        except KeyError as e:
                            print(e)
                        await send_to_message_server(f"__change_chat__&-&{nickname}&-&{client_obj.message_chat_id}&-&{chat_code}")

                        client_obj.message_chat_id = chat_code

                        continue

            except ConnectionResetError:
                del Server.clients[nickname]
                writer.close()
                break

    async def handle_server(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        writer.write(b'DISCOVER') #Запрос на информацию о сервере
        while True:
            try:
                msg = await reader.read(4096)
                msg = msg.decode('utf-8')
                print(msg, "srv")
                if msg == 'MESSAGE-SERVER':
                    Server.servers["message-server"] = writer
                    continue

            except ConnectionResetError:
                writer.close()
                break

    async def settle_first_info(self, reader:asyncio.StreamReader, writer:asyncio.StreamWriter):
        writer.write(b'0' + '__NICK__'.encode('utf-8'))
        msg = await reader.read(4096)
        msg = json.loads(msg)

        nickname = msg["nickname"]
        chat_id = self.deserialize(msg["message"])

        print(f"Nickname is {nickname}")
        return [chat_id, nickname]

    async def get_client_info(self, reader:asyncio.StreamReader, writer:asyncio.StreamWriter):
        writer.write(b'0' + '__USER-INFO__'.encode('utf-8'))
        msg = await reader.read(1024)
        msg = json.loads(msg)
        nickname = msg["nickname"]
        msg = json.loads(msg["message"])
        clientObj = Client(nickname, writer)
        clientObj.friends = msg["friends"]
        clientObj.status = msg["status"]
        Server.clients[nickname] = clientObj

async def main():
    IP = "26.181.96.20"
    PORT_FO_USERS = 55558

    server_user = await asyncio.start_server(
        lambda r, w: Server().handle(r, w),
        IP,
        PORT_FO_USERS
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
