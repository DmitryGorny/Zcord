from logic.db_client.api_client import APIClient
from logic.server.Service.core.repositroies.chat_repo.IChatDBRepo import IChatDBRepo


class ChatDBRepo(IChatDBRepo):
    def __init__(self):
        self._api_client: APIClient = APIClient()

    def get_chats(self, user_id: int, is_group: bool) -> list[dict]:
        return self._api_client.get_chats(user_id, is_group)

    def create_dm_chat(self, chat_id: int) -> list[dict]:
        return self._api_client.create_dm_chat(chat_id)

    def create_group_chat(self, group_id: int) -> None:
        self._api_client.create_group_chat(group_id)

    def delete_dm_chat(self, DM_id: int) -> None:
        self._api_client.delete_dm_chat(DM_id)

    def search_chat_by_id(self, chat_id: int, is_group: bool) -> list[dict]:
        return self._api_client.search_chat_by_id(chat_id, is_group)

