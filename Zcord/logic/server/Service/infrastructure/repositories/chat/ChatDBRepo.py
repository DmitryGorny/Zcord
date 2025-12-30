from logic.db_client.api_client import APIClient
from logic.server.Service.core.repositroies.chat_repo.IChatDBRepo import IChatDBRepo


class ChatDBRepo(IChatDBRepo):
    def __init__(self):
        self._api_client: APIClient = APIClient()

    def get_chats(self, user_id: int, is_group: bool) -> list[dict]:
        return self._api_client.get_chats(user_id, is_group)

    def create_dm_chat(self, chat_id: int) -> list[dict]:
        return self._api_client.create_dm_chat(chat_id)

    def create_group_chat(self, group_id: int) -> list[dict]:
        return self._api_client.create_group_chat(group_id)

    def delete_dm_chat(self, DM_id: int) -> None:
        self._api_client.delete_dm_chat(DM_id)

    def search_chat_by_inner_id(self, chat_id: int, is_group: bool) -> list[dict]:
        return self._api_client.search_chat_by_id(chat_id, is_group)

    def get_chat_by_id(self, chat_id: int) -> dict:
        return self._api_client.get_chat_by_id(chat_id)

    def add_group_member(self, user_id: int, group_id: int) -> None:
        self._api_client.add_group_member(user_id, group_id)

    def delete_group_request(self, request_id: int) -> None:
        self._api_client.delete_group_request(request_id)

    def delete_group_member_by_id(self, member_id: int) -> None:
        self._api_client.delete_group_member_by_id(member_id)

    def search_group_member(self, user_id: int, group_id: int) -> list:
        return self._api_client.search_group_member(user_id, group_id)

    def create_group(self, group_name: str, is_private: bool, is_invite_from_admin: bool, is_password: bool,
                     password: str, creator_id: str) -> dict:
        return self._api_client.create_group(group_name=group_name,
                                             is_private=is_private,
                                             is_invite_from_admin=is_invite_from_admin,
                                             is_password=is_password,
                                             password=password,
                                             admin_id=int(creator_id))

    def add_group_admin(self, user_id: int, group_id: int) -> dict:
        return self._api_client.add_group_admin(user_id, group_id)

    def send_group_request(self, group_id: int, sender_id: int, receiver_id: int) -> dict:
        return self._api_client.send_group_request(group_id, sender_id, receiver_id)

    def change_group_admin(self, group_id: int, new_admin_id: int) -> None:
        return self._api_client.patch_admin_id(new_admin_id, group_id)

