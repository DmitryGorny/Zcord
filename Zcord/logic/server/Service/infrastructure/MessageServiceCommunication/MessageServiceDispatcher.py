from typing import Callable

from logic.server.Service.core.MessageServiceCommunication.IMessageServiceDispatcher import IMessageServiceDispatcher


class MessageServiceDispatcher(IMessageServiceDispatcher):
    def __init__(self):
        self._sender_func: Callable = None

    def define_sender_func(self, sender_func: Callable) -> None:
        self._sender_func = sender_func

    async def send_msg_server(self, msg_type: str, mes_data: dict) -> None:
        if self._sender_func is None:
            return

        await self._sender_func(msg_type, mes_data)
