import socket
from typing import Tuple, Union, Any


class ClientManager:
    def __init__(self):
        self._clients: dict[Tuple[str, str], str] = {}
        self._clients_with_sockets: dict[Tuple[str, str], socket.socket | None] = {}

    def add_client(self, client_id: str, nickname: str, ip: str):
        self._clients[(client_id, nickname)] = ip
        self._clients_with_sockets[(client_id, nickname)] = None

    def _find_client(self, client_identent: str) -> Tuple[str, str] | None:
        try:
            client_key = next(filter(lambda x: client_identent in x, self._clients))
        except StopIteration:
            return None

        return client_key

    def replace_ip_with_socket(self, ip, socket_object: socket.socket):
        try:
            key = next((key for key in self._clients.keys() if self._clients[key] == ip))
        except StopIteration:
            return None

        if self._clients_with_sockets[key] is None:
            self._clients_with_sockets[key] = socket_object

    def send(self, client_identent: str, message: Any) -> None:
        try:
            self._clients_with_sockets[self._find_client(client_identent)].send(message)
        except KeyError:
            return None

    def remove_client(self, client_identent: str) -> None:
        try:
            client = self._find_client(client_identent)
        except KeyError:
            return None

        del self._clients[client]
        self._clients_with_sockets[client].close()
        del self._clients_with_sockets[client]

    def get_client(self, client_identent: str) -> socket.socket | str | None:
        try:
            return self._clients_with_sockets[self._find_client(client_identent)]
        except KeyError:
            return None
