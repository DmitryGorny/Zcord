from logic.server.Service.core.services.chat.IChatService import IChatService
from logic.server.Service.core.services.client.IClientService import IClientService
from logic.server.Service.core.services.friend.IFriendService import IFriendService
from logic.server.Service.infrastructure.strats import IStrat
from logic.server.Service.infrastructure.strats.IStrat import ClientStrategyKeeper, FriendStrategyKeeper, \
    ChatStrategyKeeper


class StratsFabric:
    def __init__(self, client_service: IClientService, friend_service: IFriendService, chat_service: IChatService):
        self._client_service = client_service
        self._friend_service = friend_service
        self._chat_service = chat_service

    def create(self, command: str, strats_keeper) -> IStrat:

        strategy_cls = strats_keeper.commands.get(command)
        if strategy_cls is None:
            return None

        if isinstance(strats_keeper, ClientStrategyKeeper):
            strat = strategy_cls()
            strat.set_service(self._client_service)
            return strat
        if isinstance(strats_keeper, FriendStrategyKeeper):
            strat = strategy_cls()
            strat.set_service(self._friend_service)
            return strat
        if isinstance(strats_keeper, ChatStrategyKeeper):
            strat = strategy_cls()
            strat.set_service(self._chat_service)
            return strat
