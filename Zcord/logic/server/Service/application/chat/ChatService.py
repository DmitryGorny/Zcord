from logic.server.Service.core.MessageServiceCommunication.IMessageServiceDispatcher import IMessageServiceDispatcher
from logic.server.Service.core.repositroies.chat_repo.IChatDBRepo import IChatDBRepo
from logic.server.Service.core.repositroies.chat_repo.IChatRepo import IChatRepo
from logic.server.Service.core.repositroies.client_repo.IClientRepo import IClientRepo
from logic.server.Service.core.services.chat.IChatService import IChatService


class ChatService(IChatService):
    def __init__(self,
                 client_repo: IClientRepo,
                 chat_repo: IChatRepo,
                 chat_db_rp: IChatDBRepo,
                 msg_communication: IMessageServiceDispatcher):
        self._chat_repo: IChatRepo = chat_repo
        self._chat_db_repo: IChatDBRepo = chat_db_rp
        self._msg_server_communication: IMessageServiceDispatcher = msg_communication
        self._client_repo: IClientRepo = client_repo

    async def cache_request(self, user_id: str) -> None:
        chats = self._chat_repo.get_chats_by_user_id(user_id)

        chats_ids = []
        for chat in chats:
            chats_ids.append(chat.chat_id)
        await self._msg_server_communication.send_msg_server("CACHE-REQUEST",
                                                             {"chats_ids": ",".join(chats_ids), 'user_id': user_id})

    async def change_chat(self, chat_code: int, user_id: str) -> None:
        current_id = self._client_repo.get_clients_current_chat(client_id=user_id)
        if current_id is None:
            return

        if current_id == 0:
            new_id = self._client_repo.set_client_current_chat(client_id=user_id, chat_id=chat_code)
            if not new_id:
                return  # TODO: Сделать повторынй change_chat

            await self._msg_server_communication.send_msg_server("__change_chat__", {"user_id": user_id,
                                                                                     "current_chat_id": 0,
                                                                                     "chat_code": chat_code})
            return

        new_id = self._client_repo.set_client_current_chat(client_id=user_id, chat_id=chat_code)
        if not new_id:
            return  # TODO: Сделать повторынй change_chat
        
        await self._msg_server_communication.send_msg_server("__change_chat__", {"user_id": user_id,
                                                                                 "current_chat_id": current_id,
                                                                                 "chat_code": chat_code})
