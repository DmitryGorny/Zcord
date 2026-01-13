import socket
import threading
from typing import Dict, Any
import queue

from logic.client.Chat.ClientChat import ChatInterface
from logic.client.message_client import MessageConnection
from logic.client.service_client import ServiceConnection
# from logic.client.voice_client import VoiceConnection
from logic.client.voice_client import CallManager


class ClientConnections:
    """Статик класс для взаимодействия с клиентской частью приложения"""

    # Объекты классов подключений
    _service_connection: ServiceConnection = None
    _message_connection: MessageConnection = None
    # _voice_connection: VoiceConnection = None

    # Объект ChatInterface
    _chat_interface: ChatInterface = ChatInterface()

    # Данные сервеа
    _SERVER_IP = "26.181.96.20"  # IP
    _SERVER_PORT = 55558  # Порт, используемый сервером с сервисными сообщениями
    _MESSAGE_SERVER_PORT = 55557  # Порт, используемый сервером чата
    _VOICE_SERVER_PORT = 55559  # Порт, используемый сервером войса

    @staticmethod
    def start_client(user, chats: queue.Queue, main_window_dynamic_update_cb):
        sockets = ClientConnections._create_sockets()
        ClientConnections._message_connection = ClientConnections._init_message_connection(user, sockets["message_tcp"],
                                                                                           main_window_dynamic_update_cb)
        ClientConnections._service_connection = ClientConnections._init_service_connection(user, sockets["service_tcp"],
                                                                                           sockets["message_tcp"],
                                                                                           main_window_dynamic_update_cb)
        ClientConnections._init_chats(chats)
        ClientConnections._create_threads()

    @staticmethod
    def _create_sockets() -> Dict[str, socket.socket]:
        """Создает сокеты для каждого из соединений"""

        service_tcp: socket.socket = None
        message_tcp: socket.socket = None

        try:
            service_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            service_tcp.settimeout(1.0)
            service_tcp.connect((ClientConnections._SERVER_IP, ClientConnections._SERVER_PORT))
        except ConnectionRefusedError:
            print("Не удалось подключится")
            exit(0)

        try:
            message_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            message_tcp.settimeout(1.0)
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
    def _init_message_connection(user, socket_pointer: socket.socket, callback) -> MessageConnection:
        return MessageConnection(socket_pointer, user, callback)

    @staticmethod
    def _init_service_connection(user, socket_pointer: socket.socket, msg_socket: socket.socket,
                                 callback) -> ServiceConnection:
        return ServiceConnection(socket_pointer,
                                 msg_socket,
                                 {"IP": ClientConnections._SERVER_IP, "PORT": ClientConnections._MESSAGE_SERVER_PORT},
                                 user, callback)

    # TODO: преобразовать правильно
    # @staticmethod
    # def _init_voice_connection(user, socket_pointer: socket.socket) -> VoiceConnection:
    # return VoiceConnection(socket_pointer, user)

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
    def add_chat(attrs: Dict[str, Any]) -> None:
        ClientConnections._chat_interface.chats = attrs

    @staticmethod
    def change_chat(chat_id: str) -> None:
        chat = ClientConnections._chat_interface.change_chat(chat_id)
        chat.socket_controller.clear_unseen_messages_in_view(chat_id)
        ClientConnections.send_service_message(group='CHAT', msg_type="__change_chat__")
        ClientConnections._message_connection.chat = chat
        ClientConnections._service_connection.chat = chat

    @staticmethod
    def send_service_message(group: str, msg_type: str, message: str = None, extra_data: Dict[str, str] = None) -> None:
        """Для сервисных сообщений на Server"""
        current_chat = ClientConnections._chat_interface.current_chat_id
        ClientConnections._service_connection.send_message(group, msg_type, message, current_chat, extra_data)

    @staticmethod
    def send_chat_message(message: str = None) -> None:
        """Для тесктовых сообщений на MessageServer"""
        current_chat = ClientConnections._chat_interface.current_chat_id
        ClientConnections._message_connection.send_message(current_chat, message=message)

    @staticmethod
    def ask_for_scroll_cache(msg_type: str):
        current_chat = ClientConnections._chat_interface.current_chat_id
        index = ClientConnections._chat_interface.chat.scroll_index
        db_index = ClientConnections._chat_interface.chat.scroll_db_index
        ClientConnections._message_connection.send_message_server_service(current_chat, msg_type=msg_type,
                                                                          data={"index": index,
                                                                                "db_index": db_index})

    @staticmethod
    def get_chat_id() -> object:
        return ClientConnections._chat_interface.chat

    @staticmethod
    def close() -> None:
        ClientConnections.send_service_message(group='CLIENT', msg_type="END-SESSION")
        ClientConnections._service_connection.close()
        ClientConnections._message_connection.close()
        # ClientConnections._voice_connection.close()
        CallManager().stop_call()
