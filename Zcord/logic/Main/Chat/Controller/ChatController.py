from typing import List, Dict
from logic.Main.Chat.Model.ChatModel import ChatModel
from logic.Main.Chat.View.IView.IView import BaseChatView


class ChatController:
    def __init__(self):
        self._views: Dict[str, BaseChatView] = {}
        self._model: ChatModel = ChatModel()

    def delete_chat(self, chat_id: str):
        try:
            del self._views[chat_id]
        except KeyError as e:
            print(e)
            return

    def set_views(self, views: List[BaseChatView]):
        for chat in views:
            self._views[str(chat.chat_id)] = chat

    def add_view(self, chat_id: str, chat) -> None:
        self._views[str(chat_id)] = chat

    def ask_for_cached_message(self) -> None:
        self._model.ask_for_cached_messages()

    def send_message(self, text: str) -> None:
        self._model.send_message(text)

    def get_socket_controller(self) -> 'ChatController.SocketController':
        return self.SocketController(self._views, self._model)

    class SocketController:
        def __init__(self, views: Dict[str, BaseChatView], model: ChatModel):
            self._views = views
            self._model = model

        def clear_layout(self, chat_id: str):
            self._views[chat_id].clear_chat_layout()

        def recieve_message(self, chat_id: str, sender, text, date, messageIndex=1, wasSeen: bool = False):
            self._views[chat_id].messageReceived.emit(sender, text, date, messageIndex, wasSeen)

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
