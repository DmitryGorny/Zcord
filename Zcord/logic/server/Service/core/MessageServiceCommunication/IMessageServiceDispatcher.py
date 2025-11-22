from typing import Protocol, Callable


class IMessageServiceDispatcher(Protocol):
    sender_func: Callable

    def define_sender_func(self, sender_func: Callable) -> None:
        raise NotImplementedError

    async def send_msg_server(self, msg_type: str, mes_data: dict) -> None:
        raise NotImplementedError

