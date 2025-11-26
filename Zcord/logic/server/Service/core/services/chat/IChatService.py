from typing import Protocol


class IChatService(Protocol):
    async def cache_request(self, user_id: str) -> None:
        raise NotImplementedError

    async def change_chat(self, chat_code: int, user_id: str) -> None:
        raise NotImplementedError
