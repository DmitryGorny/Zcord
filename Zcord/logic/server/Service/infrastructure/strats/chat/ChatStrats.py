import json

from logic.server.Service.infrastructure.strats.IStrat import IServiceStrat, ChatStrategyKeeper


class RequestCacheStrategy(ChatStrategyKeeper, IServiceStrat):
    command_name = "CACHE-REQUEST"

    def __init__(self):
        super(RequestCacheStrategy, self).__init__()

    async def execute(self, msg: dict) -> None:
        user_id = str(msg["user_id"])

        await self._service.cache_request(user_id=user_id)


class ChangeChatStrategy(ChatStrategyKeeper, IServiceStrat):
    command_name = "__change_chat__"

    def __init__(self):
        super(ChangeChatStrategy, self).__init__()

    async def execute(self, msg: dict) -> None:
        user_id = str(msg["user_id"])
        chat_code = int(msg["chat_id"])

        await self._service.change_chat(user_id=user_id, chat_code=chat_code)
