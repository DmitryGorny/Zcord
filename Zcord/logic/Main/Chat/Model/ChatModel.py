import asyncio
import threading

from PyQt6.QtCore import QThread, pyqtSignal, QObject

from logic.Main.Friends.FriendAdding import FriendAdding
from logic.Message import message_client
from logic.client.ClientConnections.ClientConnections import ClientConnections
from logic.client.voice_client import CallManager


class ChatModel(QObject):
    def __init__(self):
        super().__init__()
        self.call_manager = CallManager()

    def ask_for_cached_messages(self):
        ClientConnections.send_service_message(f"__CACHED-REQUEST__")

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

    def stop_call(self):
        """Остановка звонка - синхронный вызов"""
        success = self.call_manager.stop_call()

    # Микрофон
    def mute_mic_self(self, flg):
        voice_client_cls = self.call_manager.get_voice_handler_class()
        voice_client_cls.send_mute_mic(flg)

    # Наушники
    def mute_head_self(self, flg):
        voice_client_cls = self.call_manager.get_voice_handler_class()
        voice_client_cls.send_mute_mic(flg)

