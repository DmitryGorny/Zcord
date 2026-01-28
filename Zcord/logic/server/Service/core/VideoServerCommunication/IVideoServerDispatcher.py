from typing import Protocol, Callable


class IVideoServerDispatcher(Protocol):
    sender_func: Callable

    def define_sender_func(self, sender_func: Callable) -> None:
        raise NotImplementedError

    async def send_video_server(self, msg_type: str, mes_data: dict) -> None:
        raise NotImplementedError

