from logic.server.Service.core.services.chat.IChatService import IChatService
from logic.server.Service.core.services.client.IClientService import IClientService
from logic.server.Service.core.services.friend.IFriendService import IFriendService
from logic.server.Service.infrastructure.strats.strats_choose.ChooseStrategyGroup import ChooseStrategyGroupKeeper
from logic.server.Service.infrastructure.strats.IStrat import IServiceStrat, StratsGroupKeeper
from logic.server.Service.infrastructure.strats.strats_fabric.StartsFabric import StratsFabric


class ChooseStrategy:
    def __init__(self, client_service: IClientService, friend_service: IFriendService, chat_service: IChatService):
        self.__current_strategy = None
        self._choose_group: ChooseStrategyGroupKeeper = ChooseStrategyGroupKeeper()
        self._fabric = StratsFabric(client_service, friend_service, chat_service)

    def _get_group(self, group_name: str) -> StratsGroupKeeper:
        return self._choose_group.get_group(group_name)

    def get_strategy(self, group_name: str, command: str) -> IServiceStrat | None:
        if self.__current_strategy is not None:
            if self.__current_strategy.command_name == command:
                return self.__current_strategy

        group_keeper = self._get_group(group_name)
        if group_keeper is None:
            return None

        self.__current_strategy = self._fabric.create(command, group_keeper)
        return self.__current_strategy
