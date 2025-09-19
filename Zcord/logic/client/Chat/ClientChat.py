from typing import List, Dict, Union


class Chat:
    def __init__(self, chat_id: int, friend_nick: str, socket_controller, scroll_index: int):
        self._chat_id = chat_id
        self._friend_nick = friend_nick
        self.socket_controller = socket_controller

        self._scroll_index: int = -1
        self._scroll_db_index: int = 0
        self._max_scroll_index: int = scroll_index

    @property
    def friend_nick(self) -> str:
        return self._friend_nick

    @property
    def chat_id(self) -> int:
        return self._chat_id

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


class ChatInterface:
    def __init__(self):
        self._chat: Chat = None
        self._current_chat_id = 0
        self._chats: List[Chat] = []

    def change_chat(self, chat_id: str) -> Chat:
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
    def chat(self) -> Chat:
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

        self._chat = chat

    def chats(self, attrs: Dict[str, str]):
        # 60 - Т.к. нынешнее количетсво сообщений на сервере - 15 * 4
        chat = Chat(int(attrs["chat_id"]), attrs["nickname"], attrs["socket_controller"], 60)
        self._chats.append(chat)

    chats = property(fset=chats)
