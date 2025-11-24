from typing import Protocol


class IClientDBRepo(Protocol):
    def get_users(self) -> list[dict]:
        raise NotImplementedError

    def get_user(self, nickname: str) -> list[dict]:
        raise NotImplementedError

    def get_user_by_id(self, user_id: int) -> dict:
        raise NotImplementedError

    def create_user(self, nickname, password, firstname=None, secondname=None, lastname=None) -> None:
        raise NotImplementedError
