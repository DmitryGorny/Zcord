from abc import ABC, abstractmethod
from typing import List, Dict, Protocol


class IChat(ABC):

    @property
    @abstractmethod
    def socket_controller(self):
        pass

    @property
    @abstractmethod
    def chat_id(self) -> int:
        pass

    @property
    @abstractmethod
    def scroll_index(self) -> int:
        pass

    @scroll_index.setter
    @abstractmethod
    def scroll_index(self, ind: int) -> None:
        pass

    @property
    @abstractmethod
    def scroll_db_index(self) -> int:
        pass

    @scroll_db_index.setter
    @abstractmethod
    def scroll_db_index(self, ind: int) -> None:
        pass


class BaseChat(IChat):
    def __init__(self, chat_id: int, socket_controller, scroll_index: int):
        self._chat_id = chat_id
        self._socket_controller = socket_controller

        self._scroll_index: int = -1
        self._scroll_db_index: int = 0
        self._max_scroll_index: int = scroll_index

    @property
    def chat_id(self) -> int:
        return self._chat_id

    @property
    def socket_controller(self):
        return self._socket_controller

    @property
    def scroll_index(self) -> int:
        return self._scroll_index

    @scroll_index.setter
    def scroll_index(self, ind: int):
        if ind < 0:
            raise ValueError("index cant be smaller than 0")
        self._scroll_index = ind

    @property
    def scroll_db_index(self) -> int:
        return self._scroll_db_index

    @scroll_db_index.setter
    def scroll_db_index(self, ind: int):
        if ind < 0:
            raise ValueError("index cant be smaller than 0")
        if ind == 0:
            self._scroll_db_index = 0
        self._scroll_db_index += ind


class Chat(BaseChat):
    def __init__(self, chat_id: int, socket_controller, scroll_index: int):
        super(Chat, self).__init__(chat_id, socket_controller, scroll_index)


class Group(BaseChat):
    def __init__(self, chat_id: int, socket_controller, scroll_index: int):
        super(Group, self).__init__(chat_id, socket_controller, scroll_index)


class ChatInterface:
    def __init__(self):
        self._chat: IChat | None = None
        self._current_chat_id = 0
        self._chats: List[IChat] = []

    def change_chat(self, chat_id: str) -> IChat:
        try:
            self._chat.socket_controller.clear_layout(str(chat_id))
        except AttributeError:
            pass

        self._current_chat_id = int(chat_id)
        self._chat_setter(int(chat_id))

        return self._chat

    @property
    def current_chat_id(self):
        return self._current_chat_id

    @property
    def chat_id(self):
        return self._chat.chat_id

    @property
    def chat(self) -> IChat:
        return self._chat

    def _chat_setter(self, chat_id: int) -> None:
        if self._current_chat_id == 0:
            raise ValueError("Ошибка в self._curent_chat_id: id не был присвоен во время chage_chat")

        if self._chat is not None:
            self._chat.scroll_index = 0
            self._chat.scroll_db_index = 0
            self._chat.socket_controller.enable_model_scroll_bar_requesting()

        chat_filter = filter(lambda x: x.chat_id == chat_id, self._chats)
        chat = next(chat_filter, None)

        if chat is None:
            raise ValueError(f"Нет такого Chat() с id {chat_id}")
        print(chat)

        self._chat = chat

    def chats(self, attrs: Dict[str, str]):
        # 60 - Т.к. нынешнее количетсво сообщений на сервере - 15 * 4
        if attrs['is_dm']:
            chat = Chat(int(attrs["chat_id"]), attrs["socket_controller"], 60)
            self._chats.append(chat)
            return
        chat = Group(int(attrs["chat_id"]), attrs["socket_controller"], 60)
        self._chats.append(chat)

    chats = property(fset=chats)
