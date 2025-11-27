import json

from logic.server.Service.infrastructure.strats.IStrat import IServiceStrat, ClientStrategyKeeper


class UserInfoStrat(ClientStrategyKeeper, IServiceStrat):
    command_name = "USER-INFO"

    def __init__(self):
        super(UserInfoStrat, self).__init__()

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


class EndSessionStrategy(ClientStrategyKeeper, IServiceStrat):
    command_name = "END-SESSION"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        user_id = str(msg["user_id"])
        await self._service.user_left(client_id=user_id, status={'color': 'grey', 'user-status': 'Невидимка'})
        raise ConnectionResetError  # Чтобы задача стопалась


class UserStatusStrategy(ClientStrategyKeeper, IServiceStrat):
    command_name = "USER-STATUS"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        user_status = msg['status_name']
        color = msg['color']
        user_id: str = str(msg['user_id'])
        user_status = {'color': color, 'user-status': user_status}
        await self._service.user_status(user_id, user_status)
