import threading
from typing import List, Dict
from logic.Main.Chat.Model.ChatModel import ChatModel
from logic.Main.Chat.View.ChatClass.ChatView import ChatView


class ChatController:
    def __init__(self):
        self._views: Dict[str, ChatView] = {}
        self._model: ChatModel = ChatModel()

    def set_views(self, views: List[ChatView]):
        for chat in views:
            self._views[str(chat.getChatId())] = chat

    def add_view(self, chat_id: str, chat) -> None:
        self._views[str(chat_id)] = chat

    def ask_for_cached_message(self) -> None:
        self._model.ask_for_cached_messages()

    def send_message(self, text: str) -> None:
        self._model.send_message(text)

    def get_socket_controller(self) -> 'ChatController.SocketController':
        return self.SocketController(self._views, self._model)

    # TODO: Переделать вместе с ситемой добавления друзей + ChatModel
    def send_friend_request(self, chat_id, friend_nick):
        self._model.send_friend_request(chat_id, friend_nick)

    def reject_request(self, user, friend_nick, deleteFriend):
        self._model.reject_request(user, friend_nick, deleteFriend)

    def block_user(self, user, friend_nick):
        self._model.block_user(user, friend_nick)

    def accept_request(self, user, friend_nick):
        self._model.accept_friend_request(user, friend_nick)

    class SocketController:
        def __init__(self, views: Dict[str, ChatView], model: ChatModel):
            self._views = views
            self._model = model

        def clear_layout(self, chat_id: str):
            self._views[chat_id].clearLayout()

        # TODO:Пересмотреть метод в view
        def recieve_message(self, chat_id: str, sender, text, date, messageIndex=1, wasSeen: bool = False):
            self._views[chat_id].messageReceived.emit(sender, text, date, messageIndex, wasSeen)

        def awaited_receive_message(self, chat_id: str, sender, text, date, messageIndex=1,
                                    wasSeen: bool = False, event: threading.Event = None):
            self._views[chat_id].awaitedMessageReceive.emit(sender, text, date, messageIndex, wasSeen, event)

        def enable_scroll_bar(self, chat_id: str):
            self._views[chat_id].enable_scroll_bar.emit()
            self._model.enable_scroll_cache()

        def stop_requesting_cache(self):
            self._model.stop_requesting_cache()

        def enable_model_scroll_bar_requesting(self):
            self._model.enable_scroll_cache()

        def change_unseen_status(self, chat_id: str, number_of_messages: int):
            self._views[chat_id].change_unseen_status_signal.emit(number_of_messages)

        def clear_unseen_messages_in_view(self, chat_id: str):
            self._views[str(chat_id)].clear_unseen.emit()
