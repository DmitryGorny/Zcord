import socket
from typing import Tuple, Union, Any


class ClientManager:
    def __init__(self):
        self._clients: dict[str, str] = {}
        self._clients_with_sockets: dict[str, socket.socket | None] = {}

    def add_client(self, client_id: str, ip: str):
        self._clients[client_id] = ip
        self._clients_with_sockets[client_id] = None

    def replace_ip_with_socket(self, ip, socket_object: socket.socket):
        try:
            key = next((key for key in self._clients.keys() if self._clients[key] == ip))
            self._clients[key] = ''
        except StopIteration:
            return None

        if self._clients_with_sockets[key] is None:
            self._clients_with_sockets[key] = socket_object

    def send(self, client_identent: str, message: Any) -> None:
        try:
            self._clients_with_sockets[client_identent].send(message)
        except KeyError:
            return None

    def remove_client(self, client_identent: str) -> None:
        try:

            client = self._clients[str(client_identent)]
        except KeyError:
            return None

        del self._clients[str(client_identent)]
        self._clients_with_sockets[str(client_identent)].close()
        del self._clients_with_sockets[str(client_identent)]

    def get_client(self, client_identent: str) -> socket.socket | str | None:
        try:
            return self._clients_with_sockets[client_identent]
        except KeyError:
            return None
