import socket
import threading
from typing import Dict
import queue

from logic.client.Chat.ClientChat import ChatInterface
from logic.client.message_client import MessageConnection
from logic.client.service_client import ServiceConnection
from logic.client.voice_client import VoiceConnection


class ClientConnections:
    """Статик класс для взаимодействия с клиентской частью приложения"""

    # Объекты классов подключений
    _service_connection: ServiceConnection = None
    _message_connection: MessageConnection = None
    _voice_connection: VoiceConnection = None

    # Объект ChatInterface
    _chat_interface: ChatInterface = ChatInterface()

    # Данные сервеа
    _SERVER_IP = "26.36.207.48"  # IP
    _SERVER_PORT = 55558  # Порт, используемый сервером с сервисными сообщениями
    _MESSAGE_SERVER_PORT = 55557  # Порт, используемый сервером чата
    _VOICE_SERVER_PORT = 55559  # Порт, используемый сервером войса

    @staticmethod
    def start_client(user, chats: queue.Queue):
        sockets = ClientConnections._create_sockets()
        ClientConnections._message_connection = ClientConnections._init_message_connection(user, sockets["message_tcp"])
        ClientConnections._service_connection = ClientConnections._init_service_connection(user, sockets["service_tcp"], sockets["message_tcp"])
        ClientConnections._init_chats(chats)
        ClientConnections._create_threads()

    @staticmethod
    def _create_sockets() -> Dict[str, socket.socket]:
        """Создает сокеты для каждого из соединений"""

        service_tcp: socket.socket = None
        message_tcp: socket.socket = None

        try:
            service_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            service_tcp.connect((ClientConnections._SERVER_IP, ClientConnections._SERVER_PORT))
        except ConnectionRefusedError:
            print("Не удалось подключится")
            exit(0)

        try:
            message_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except ConnectionRefusedError:
            print("Не удалось подключится")
            exit(0)

        return {"service_tcp": service_tcp, "message_tcp": message_tcp}

    @staticmethod
    def _create_threads() -> None:
        if ClientConnections._service_connection is None and ClientConnections._message_connection is None:
            raise ValueError("Объекты классов соединений не инициализированы")

        # Слушаем сервисный порт
        receive_service_thread = threading.Thread(target=ClientConnections._service_connection.recv_server)
        receive_service_thread.start()

        # Слушаем чат
        recieve_message_thread = threading.Thread(target=ClientConnections._message_connection.recv_server)
        recieve_message_thread.start()

    @staticmethod
    def _init_message_connection(user, socket_pointer: socket.socket) -> MessageConnection:
        return MessageConnection(socket_pointer, user)

    @staticmethod
    def _init_service_connection(user, socket_pointer: socket.socket, msg_socket: socket.socket) -> ServiceConnection:
        return ServiceConnection(socket_pointer,
                                 msg_socket,
                                 {"IP": ClientConnections._SERVER_IP, "PORT": ClientConnections._MESSAGE_SERVER_PORT},
                                 user)

    # TODO: преобразовать правильно
    @staticmethod
    def _init_voice_connection(user, socket_pointer: socket.socket) -> VoiceConnection:
        return VoiceConnection(socket_pointer, user)

    @staticmethod
    def _init_chats(chats_queue: queue.Queue):
        if ClientConnections._service_connection is None:
            raise ValueError("_init_chats должен быть вызван после инициализации объекта сервисных сообщений")
        while not chats_queue.empty():
            attrs = chats_queue.get()
            ClientConnections._service_connection.cache_chat = attrs["chat_id"]
            ClientConnections._chat_interface.chats = attrs
            chats_queue.task_done()

    @staticmethod
    def change_chat(chat_id: str) -> None:
        chat = ClientConnections._chat_interface.change_chat(chat_id)
        ClientConnections.send_service_message("__change_chat__")
        ClientConnections._message_connection.chat = chat

    @staticmethod
    def send_service_message(message: str) -> None:
        current_chat = ClientConnections._chat_interface.current_chat_id
        ClientConnections._service_connection.send_message(message, current_chat)

    @staticmethod
    def send_chat_message(message: str) -> None:
        print(11)
        current_chat = ClientConnections._chat_interface.current_chat_id
        ClientConnections._message_connection.send_message(message, current_chat)

    @staticmethod
    def close() -> None:
        ClientConnections.send_service_message("END-SESSION")
        ClientConnections._service_connection.close()
        ClientConnections._message_connection.close()
