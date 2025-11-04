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

    # TODO: Переделать вместе с ситемой добавления друзей + ChatModel
    def send_friend_request(self, chat_id, friend_nick):
        self._model.send_friend_request(chat_id, friend_nick)

    def reject_request(self, user, friend_nick, deleteFriend):
        self._model.reject_request(user, friend_nick, deleteFriend)

    def block_user(self, user, friend_nick):
        self._model.block_user(user, friend_nick)

    def accept_request(self, user, friend_nick):
        self._model.accept_friend_request(user, friend_nick)

    #  абстрактно здесь будет класс VOICE GUI
    def start_call(self, user, chat_id):
        self._model.start_call(user, chat_id)

    def stop_call(self):
        self._model.stop_call()

    def get_voice_flg(self):
        return self._model.get_voice_flg()

    # Микрофон
    def mute_mic_self(self, flg):
        self._model.mute_mic_self(flg)

    # Наушники
    def mute_head_self(self, flg):
        self._model.mute_head_self(flg)

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

        # Voice
        def icon_call(self, chat_id: str, user_id: int, username: str):
            self._views[str(chat_id)].iconCall.emit(user_id, username)

        def icon_call_left(self, chat_id: str, user_id: int):
            self._views[str(chat_id)].iconCallLeft.emit(user_id)

        def receive_mute(self, device: str, chat_id: str, mute_pos: bool, client: object):
            self._views[str(chat_id)].muteDevice.emit(device, mute_pos, client)

        def receive_connect(self, chat_id: str, clients: list):
            self._views[str(chat_id)].connectReceived.emit(clients)

        def receive_disconnect(self, chat_id: str, client: object):
            self._views[str(chat_id)].disconnectReceived.emit(client)

        def receive_call(self, chat_id: str, call_flg: bool):
            self._views[str(chat_id)].callReceived.emit(call_flg)

        def vad_animation(self, chat_id: str, speech_flg: bool, user_id: int):
            self._views[str(chat_id)].speechDetector.emit(speech_flg, user_id)
