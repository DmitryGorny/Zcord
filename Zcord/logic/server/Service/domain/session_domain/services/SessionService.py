import asyncio
from typing import Protocol

from logic.server.Service.domain.session_domain.repos.SessionRepo import SessionRepo, ISessionRepo


class ISessionService(Protocol):
    _session_repository: ISessionRepo

    async def user_joined(self, user_id: str, nickname: str, writer: asyncio.StreamWriter, last_online: str,
                          friends: list[dict], status: dict[str, str], chats: list[dict]):
        raise NotImplementedError


class SessionService:
    def __init__(self, session_repo: SessionRepo):
        self._session_repository: ISessionRepo = session_repo

    async def user_joined(self, user_id: str, nickname: str, writer: asyncio.StreamWriter, last_online: str,
                          friends: list[dict], status: dict[str, str], chats: list[dict]):
        self._session_repository.add_client(client_id=user_id,
                                            client_name=nickname,
                                            writer=writer,
                                            last_online=last_online)
        self._session_repository.add_friends(client_id=user_id, friends=friends)
        self._session_repository.add_chats(client_id=user_id, chats=chats)
        await self._session_repository.connect_message_socket(user_id)
        await self._session_repository.change_activity_status(user_id, status)
        await self._session_repository.notify_message_server_add(user_id, chats, writer)
