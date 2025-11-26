from typing import Protocol


class IFriendService(Protocol):
    async def friend_request_send(self, friend_id: str, user_id: str, receiver_nick: str, sender_nick: str) -> None:
        raise NotImplementedError

    async def friend_request_recall(self, friend_id: str, sender_id: str) -> None:
        raise NotImplementedError

    async def friend_request_accepted(self, friend_id: str, sender_id: str) -> None:
        raise NotImplementedError

    async def friend_request_rejected(self, friend_id: str, sender_id: str) -> None:
        raise NotImplementedError

    async def friend_delete(self, friend_id: str, sender_id: str) -> None:
        raise NotImplementedError
