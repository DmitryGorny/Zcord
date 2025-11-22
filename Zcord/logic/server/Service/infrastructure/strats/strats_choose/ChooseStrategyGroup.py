from logic.server.Service.infrastructure.strats.IStrat import StratsGroupKeeper


class ChooseStrategyGroupKeeper:
    """Возвращает keeper определенной группы"""
    def __init__(self):
        self.__current_group = None

    def get_group(self, group_name: str) -> StratsGroupKeeper | None:
        if self.__current_group is not None:
            if self.__current_group.group_name == group_name:
                return self.__current_group

        if group_name not in StratsGroupKeeper.groups.keys():
            return None

        self.__current_group = StratsGroupKeeper.groups[group_name]()
        return self.__current_group
