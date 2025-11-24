from typing import Protocol


class IFriendDBRepo(Protocol):
    def create_friendship_request(self, user_id: int, friend_id: int) -> dict:
        raise NotImplementedError

    def get_friendship_by_users_id(self, user1_id: int, user2_id: int) -> list[dict]:
        raise NotImplementedError

    def send_friend_request(self, sender_id: int, receiver_id: int, friendship_id: int) -> None:
        raise NotImplementedError

    def delete_friendship_request(self, sender_id: int, friend_id: int, friendship_id: int) -> None:
        raise NotImplementedError

    def patch_friendship_status(self, friendship_id: int, status: int) -> None:
        raise NotImplementedError

    def delete_friendship(self, friendship_id) -> None:
        raise NotImplementedError
