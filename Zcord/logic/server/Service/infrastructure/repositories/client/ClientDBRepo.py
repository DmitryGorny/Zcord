from logic.db_client.api_client import APIClient
from logic.server.Service.core.repositroies.client_repo.IClientDBRepo import IClientDBRepo


class ClientDBRepo(IClientDBRepo):
    def __init__(self):
        self._api_client: APIClient = APIClient()

    def get_users(self) -> list[dict]:
        return self._api_client.get_users()

    def get_user(self, nickname: str) -> list[dict]:
        return self._api_client.get_user(nickname)

    def get_user_by_id(self, user_id: int) -> dict:
        return self._api_client.get_user_by_id(user_id)

    def create_user(self, nickname, password, firstname=None, secondname=None, lastname=None) -> None:
        self._api_client.create_user(nickname, password, firstname, secondname, lastname)
