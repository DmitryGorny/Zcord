import json
from abc import ABC, abstractmethod
from typing import Dict
import msgspec


class IConnection(ABC):
    #Поля
    @property
    @abstractmethod
    def user(self):
        """Объект User"""
        pass

    @property
    @abstractmethod
    def flg(self):
        """Флаг на закрытие сокета"""
        pass

    #Методы
    @abstractmethod
    def send_message(self, message: str, current_chat_id: int) -> None:
        """Отсылает message на сервер"""
        pass

    @abstractmethod
    def recv_server(self) -> None:
        """Содержит логику взаимодействия с сервером"""
        pass

    @abstractmethod
    def close(self) -> None:
        """Закрывает сокет"""


class BaseConnection(ABC):
    """Класс содержащий методы необходимые для всех IConnection"""
    def decode_multiple_json_objects(self, data):
        """Обрабатывает пришедший от сервера JSON"""
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

    #TODO: Проверить надобность
    def deserialize(self, message):
        try:  # Фикс ошибки при многократном change_chat
            cache = msgspec.json.decode(message)
        except msgspec.DecodeError:
            return []
        return cache

    def serialize(self, x):
        ser = msgspec.json.encode(x)
        return ser
