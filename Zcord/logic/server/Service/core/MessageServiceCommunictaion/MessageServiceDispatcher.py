from typing import Protocol, Callable


class IMessageServiceDispatcher(Protocol):
    sender_func: Callable

    async def send_msg_server(self, msg_type: str, mes_data: dict) -> None:
        raise NotImplementedError


class MessageServiceDispatcher(IMessageServiceDispatcher):
    def __init__(self, sender_func: Callable):
        self._sender_func = sender_func

    async def send_msg_server(self, msg_type: str, mes_data: dict) -> None:
        await self._sender_func(msg_type, mes_data)
