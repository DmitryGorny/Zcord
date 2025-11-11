from typing import Dict, List, Union, Tuple, NamedTuple

MAX_MESSAGES_INDEX = 4  # Кто поменяет - захуячу


class Message(NamedTuple):
    id: str
    sender: str
    chat: str
    created_at: str
    was_seen: bool
    type: str


class CacheManager:
    def __init__(self, max_cache_messages: int = 15):
        self._limit = max_cache_messages
        self._main_cache: Dict[str, List[Message]] = {}
        self._cache_to_send = self.SendCache(max_cache_messages * MAX_MESSAGES_INDEX)

    def add_value(self, chat_id: str,
                  message: Message) -> None:
        """
        Добавление сообщения в основной кэш
        При необходимости выгруза кэша в БД выбросит CacheOverloadError
        """
        if len(self._main_cache[chat_id]) >= self._limit:
            for i in range(self._cache_to_send.current_free_space(chat_id) + 1):
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

    def init_cache(self, chat_id: str) -> None:
        if chat_id in self._main_cache.keys():
            return
        self._main_cache[chat_id] = []
        self._cache_to_send.init_cache(chat_id)

    def get_cache(self, chat_id: str, user_out: bool = False) -> Dict[str, Union[List[Message], int]]:
        if chat_id not in self._main_cache.keys():
            raise KeyError

        result_dict = {"cache": None, "index": 0}

        if user_out:  # TODO: Нужна ли полная очистка кэша??????
            extra_cache = [message for message in
                           self._cache_to_send.get_cache(chat_id, self._limit * MAX_MESSAGES_INDEX)]
            un_handled_cache = [*extra_cache,
                                *self._main_cache[chat_id]]
            final_cache = [message for message in un_handled_cache if str(message["id"]) == '0']

            result_dict["cache"] = final_cache
            return result_dict

        if len(self._main_cache[chat_id]) < self._limit:  # Добавочный кэш
            extra_cache = [message for message in
                           self._cache_to_send.get_cache(chat_id, self._limit - len(self._main_cache[chat_id]))]
            if len(extra_cache) > 0:
                result_dict["cache"] = [*extra_cache, *self._main_cache[chat_id]]
                result_dict["index"] = len(extra_cache)
                return result_dict

        result_dict["cache"] = self._main_cache[chat_id]
        return result_dict

    def get_cache_by_scroll(self, chat_id: str, index: int) -> Dict[str, List[Message]] | None:
        try:
            messages, index = self._cache_to_send.get_cache_offset(chat_id, index)
        except TypeError as e:
            print(e)
            return None

        return {"cache": messages, "index": index}

    def clear_cache(self, chat_id: str) -> None:
        self._main_cache[chat_id].clear()
        self._cache_to_send.clear_cache(chat_id)

    def add_cache(self, chat_id: str, message_list: List[Message]) -> None:
        for message in message_list:  # TODO: Добавить провреку на дублерование сообщений ????
            self.add_value(chat_id, message)

    def mark_as_seen(self, chat_id: str, sender_id: str, current_index: int = 0):
        for message in self._main_cache[chat_id]:
            if not message["was_seen"] and str(message["sender"]) != sender_id:
                message["was_seen"] = True

        if current_index <= 0:
            return

        self._cache_to_send.mark_as_seen(chat_id, sender_id, current_index)

    class SendCache:
        def __init__(self, max_massages: int = 60):
            self._current_free_space: Dict[str, int] = {}
            self._cache: Dict[str, List[Message]] = {}
            self._max_messages = max_massages

        def init_cache(self, chat_id: str):
            self._cache[chat_id] = []
            self._current_free_space[chat_id] = self._max_messages

        def add_value(self, chat_id: str, message: Message):
            if self._current_free_space[chat_id] <= 0:
                raise CacheOverloadError("Кэш перегружен", return_value=self._cache[chat_id].copy())

            self._cache[chat_id].append(message)
            self._current_free_space[chat_id] -= 1

        def clear_cache(self, chat_id: str) -> None:
            self._cache[chat_id].clear()
            self._current_free_space[chat_id] = self._max_messages

        def current_free_space(self, chat_id: str) -> int:
            return self._current_free_space[chat_id]

        def get_cache(self, chat_id: str, number_of_messages: int) -> List[Message]:
            cache = []
            if number_of_messages >= len(self._cache[chat_id]):
                cache = self._cache[chat_id].copy()
                return cache

            for index in range(number_of_messages):
                try:
                    cache.insert(0, self._cache[chat_id][::-1][index])
                except IndexError:
                    break
            return cache

        def get_cache_offset(self, chat_id: str, current_index: int) -> Tuple[List[Message], int] | None:
            if current_index > self._max_messages:
                return None

            end = int(self._max_messages / MAX_MESSAGES_INDEX)
            next_index = min(current_index + end, len(self._cache[chat_id]))

            return self._cache[chat_id][::-1][int(current_index):next_index], next_index
        
        #TODO: Пересмотерть методы пометки
        def mark_as_seen(self, chat_id: str, sender_id: str, messages_number: int) -> None:
            for message in self._cache[chat_id][::-1][:messages_number]:
                if not message["was_seen"] and message["sender"] != sender_id:
                    message["was_seen"] = True


class CacheOverloadError(Exception):
    def __init__(self, message, return_value):
        super(CacheOverloadError, self).__init__(message)
        self.return_value = return_value

    def __str__(self):
        return "Кэш перегружен"
