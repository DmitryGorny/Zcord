from logic.db_client.api_client import APIClient
from logic.server.Service.core.repositroies.friend_repo.IFriendDBRepo import IFriendDBRepo


class FriendDBRepo(IFriendDBRepo):
    def __init__(self):
        self._api_client: APIClient = APIClient()

    def create_friendship_request(self, user_id: int, friend_id: int) -> dict:
        return self._api_client.create_friendship_request(user_id, friend_id)

    def get_friendship_by_users_id(self, user1_id: int, user2_id: int) -> list[dict]:
        return self._api_client.get_friendship_by_id(user1_id, user2_id)

    def send_friend_request(self, sender_id: int, receiver_id: int, friendship_id: int) -> None:
        self._api_client.send_friend_request(sender_id, receiver_id, friendship_id)

    def delete_friendship_request(self, sender_id: int, friend_id: int, friendship_id: int) -> list[dict] | None:
        return self._api_client.delete_friendship_request(sender_id, friend_id, friendship_id)

    def patch_friendship_status(self, friendship_id: int, status: int) -> None:
        self._api_client.patch_friendship_status(friendship_id, status)

    def delete_friendship(self, friendship_id) -> None:
        self._api_client.delete_friendship(friendship_id)
