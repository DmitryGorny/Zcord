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


class CallNotificationStrategy(ClientStrategyKeeper, IServiceStrat):
    command_name = "__CALL-NOTIFICATION__"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        user_id = msg["user_id"]
        chat_id = msg["chat_id"]
        call_flag = msg["call_flg"]
        await self._service.call_notification(user_id, chat_id, call_flag)


class CallConnectionIconStrategy(ClientStrategyKeeper):
    """Добавление иконки пользователей которые находятся в звонке"""

    command_name = "__ICON-CALL__"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        user_id = str(msg["user_id"])
        chat_id = str(msg["chat_id"])
        username = msg["username"]
        await self._service.icon_call_add(user_id=user_id, chat_id=chat_id, username=username)


class CallConnectionIconLeftStrategy(ClientStrategyKeeper):
    """Удаление иконки пользователей которые находятся в звонке"""

    command_name = "__LEFT-ICON-CALL__"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        user_id = str(msg["user_id"])
        chat_id = str(msg["chat_id"])
        await self._service.icon_call_left(user_id=user_id, chat_id=chat_id)
