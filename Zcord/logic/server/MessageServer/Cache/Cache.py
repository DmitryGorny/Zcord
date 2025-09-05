from typing import Dict, List, Union


class CacheManager:
    def __init__(self, max_cache_messages: int = 15):
        self._limit = max_cache_messages
        self._main_cache: Dict[str, List[Dict[str, Union[str, bool]]]] = {}

        self._cache_to_send = self.SendCache(max_cache_messages * 4)

    def add_value(self, chat_id: str,
                  message: Dict[str, Union[str, bool]]) -> None:  # По идее не должен ловить CacheOverloadError, но хз
        """
        Добавление сообщения в основной кэш
        При необходимости выгруза кэша в БД выбросит CacheOverloadError
        """
        if len(self._main_cache[chat_id]) >= self._limit:
            for i in range(self._cache_to_send.current_free_space(chat_id) + 1):  # TODO: Почему нужен + 1
                try:
                    self._cache_to_send.add_value(chat_id, self._main_cache[chat_id][i])
                except IndexError:
                    del self._main_cache[chat_id][0:i]
                    break
                except CacheOverloadError as e:
                    self._cache_to_send.clear_cache(chat_id)
                    return e.return_value
        self._main_cache[chat_id].append(message)
        return None

    def init_cache(self, chat_id: str):
        self._main_cache[chat_id] = []
        self._cache_to_send.init_cache(chat_id)

    def get_cache(self, chat_id: str, user_out: bool = False) -> List[Dict[str, Union[str, bool]]]:
        if user_out: #TODO: Нужна ли полная очистка кэша??????
            un_handled_cache = [*[message for message in
                                  self._cache_to_send.get_cache(chat_id, self._limit*4)], *self._main_cache[chat_id]]
            final_cache = [message for message in un_handled_cache if str(message["id"]) == '0']
            self._cache_to_send.clear_cache(chat_id)

            return final_cache

        if len(self._main_cache[chat_id]) < self._limit:  # Добавочный кэш
            extra_cache = [message for message in
                           self._cache_to_send.get_cache(chat_id, self._limit - len(self._main_cache[chat_id]))]
            if len(extra_cache) > 0:
                return [*extra_cache, *self._main_cache[chat_id]]

        return self._main_cache[chat_id]

    def clear_cache(self, chat_id: str) -> None:
        self._main_cache[chat_id].clear()

    def add_cache(self, chat_id: str, message_list: List[Dict[str, Union[str, bool]]]) -> None:
        for message in message_list:  # TODO: Добавить провреку на дублерование сообщений ????
            self.add_value(chat_id, message)

    class SendCache:
        def __init__(self, max_massages: int = 60):
            self._current_free_space: Dict[str, int] = {}
            self._cache: Dict[str, List[Dict[str, Union[str, bool]]]] = {}
            self._max_messages = max_massages

        def init_cache(self, chat_id: str):
            self._cache[chat_id] = []
            self._current_free_space[chat_id] = self._max_messages

        def add_value(self, chat_id: str, message: Dict[str, Union[str, bool]]):
            if self._current_free_space[chat_id] <= 0:
                raise CacheOverloadError("Кэш перегружен", return_value=self._cache[chat_id].copy())
            self._cache[chat_id].append(message)
            self._current_free_space[chat_id] -= 1

        def clear_cache(self, chat_id: str) -> None:
            self._cache[chat_id].clear()
            self._current_free_space[chat_id] = self._max_messages

        def current_free_space(self, chat_id: str) -> int:
            return self._current_free_space[chat_id]

        def get_cache(self, chat_id: str, number_of_messages: int) -> List[Dict[str, Union[str, bool]]]:
            cache = []

            if number_of_messages >= len(self._cache):
                cache = self._cache[chat_id].copy()
                return cache

            for index in range(number_of_messages):
                try:
                    cache.insert(0, self._cache[chat_id][::-1][index])
                except IndexError:
                    break
            return cache


class CacheOverloadError(Exception):
    def __init__(self, message, return_value):
        super(CacheOverloadError, self).__init__(message)
        self.return_value = return_value

    def __str__(self):
        return "Кэш перегружен"
