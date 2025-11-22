import json

from logic.server.Service.core.services.client.IClientService import IClientService
from logic.server.Service.infrastructure.strats.IStrat import IServiceStrat, ClientStrategyKeeper


class UserInfoStrat(IServiceStrat, ClientStrategyKeeper):
    command_name = "USER-INFO"

    def __init__(self, service: IClientService):
        super(UserInfoStrat, self).__init__(service)

    async def execute(self, msg: dict) -> None:
        user_id = str(msg["user_id"])
        nickname = msg["nickname"]
        writer = msg['writer']
        data = json.loads(msg["message"])
        last_online = data["last_online"]
        friends = data["friends"]

        status = data['status']
        chats = data['chats']

        await self._service.user_joined(user_id=user_id,
                                        nickname=nickname,
                                        writer=writer,
                                        last_online=last_online,
                                        friends=friends,
                                        status=status,
                                        chats=chats)


class EndSessionStrategy(IServiceStrat, ClientStrategyKeeper):
    command_name = "END-SESSION"

    def __init__(self, service: IClientService):
        super().__init__(service)

    async def execute(self, msg: dict) -> None:
        user_id = str(msg["user_id"])
        await self._service.user_left(client_id=user_id)
        raise ConnectionResetError  # Чтобы задача стопалась
