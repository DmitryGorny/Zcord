import asyncio
import threading

from PyQt6.QtCore import QThread, pyqtSignal, QObject

from logic.Main.Friends.FriendAdding import FriendAdding
from logic.client.ClientConnections.ClientConnections import ClientConnections
from logic.client.voice_client import CallManager


class ChatModel(QObject):
    def __init__(self):
        super().__init__()
        self.call_manager = CallManager()
        self._block_scroll_cache = False

    def call_notification(self):
        ClientConnections.send_service_message("CALL-NOTIFICATION")

    def ask_for_cached_messages(self):
        if not self._block_scroll_cache:
            ClientConnections.ask_for_scroll_cache(msg_type=f"SCROLL-CACHE-REQUEST")
            self._block_scroll_cache = True

    def stop_requesting_cache(self):
        self._block_scroll_cache = True

    def enable_scroll_cache(self):
        self._block_scroll_cache = False

    def send_message(self, text: str):
        ClientConnections.send_chat_message(text)

    def send_friend_request(self, chat_id, friend_nick):
        ClientConnections.send_service_message(f"__FRIEND-ADDING__&{friend_nick}")
        #message_client.MessageConnection.addChat(f"{chat_id}")

    def accept_friend_request(self, user, friend_nick):
        friendAdding = FriendAdding(user)

        if friendAdding.acceptRequest(friend_nick):
            ClientConnections.send_service_message(f"__ACCEPT-REQUEST__&{friend_nick}")
        else:
            print("Ошибка целостности бд: в таблице friendship не существует запроса в друзья")

    def reject_request(self, user, friend_nick, deleteFriend:bool = False):
        friendAdding = FriendAdding(user)
        friendAdding.deleteFriendRequest(friend_nick)
        if friendAdding.rejectRequest(friend_nick, deleteFriend):
            ClientConnections.send_service_message(f"__REJECT-REQUEST__&{friend_nick}")
        else:
            print("Ошибка целостности бд: в таблице friendship не существует запроса в друзья")

    def block_user(self, user, friend_nick):
        friendAdding = FriendAdding(user)
        friendAdding.deleteFriendRequest(friend_nick)
        friendAdding.BlockUser(friend_nick)
        ClientConnections.send_service_message(f"__DELETE-REQUEST__&{friend_nick}")

    #  абстрактно здесь будет класс VOICE GUI
    def start_call(self, user, chat_id):
        """Запуск звонка - синхронный вызов"""
        success = self.call_manager.start_call(
            user=None,
            host="26.36.207.48",
            port=55559,
            room=chat_id
        )
        ClientConnections.send_service_message(message=f"__CALL-NOTIFICATION__", extra_data={"call_flg": "1"})

    def stop_call(self):
        """Остановка звонка - синхронный вызов"""
        success = self.call_manager.stop_call()
        ClientConnections.send_service_message(message=f"__CALL-NOTIFICATION__", extra_data={"call_flg": "0"})

    # Микрофон
    def mute_mic_self(self, flg):
        self.call_manager.client.voice_handler.mute_mic_self(flg)
        asyncio.run_coroutine_threadsafe(
            self.call_manager.client.send_mute_mic(flg),
            self.call_manager.loop
        )

    # Наушники
    def mute_head_self(self, flg):
        self.call_manager.client.voice_handler.mute_head_self(flg)
        asyncio.run_coroutine_threadsafe(
            self.call_manager.client.send_mute_head(flg),
            self.call_manager.loop
        )
