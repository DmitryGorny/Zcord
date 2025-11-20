import json

from logic.server.Service.infrastructure.IStrat import ServiceStrategy


class UserInfoStrat(ServiceStrategy):
    command_name = "USER-INFO"

    def __init__(self):
        super(UserInfoStrat, self).__init__()

    async def execute(self, msg: dict) -> None: # TODO: Перейти к реализации END-SESSION
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
