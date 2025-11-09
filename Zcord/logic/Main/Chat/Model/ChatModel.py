import asyncio
from logic.client.ClientConnections.ClientConnections import ClientConnections
from logic.client.voice_client import CallManager


class ChatModel:
    def __init__(self):
        super().__init__()
        self.call_manager = CallManager()
        self._block_scroll_cache = False

    def call_notification(self):
        ClientConnections.send_service_message(msg_type="CALL-NOTIFICATION")

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

    def block_user(self, user, friend_nick):
        pass
        #friendAdding = FriendAdding(user)
        #friendAdding.deleteFriendRequest(friend_nick)
        #friendAdding.BlockUser(friend_nick)
        #ClientConnections.send_service_message(f"__DELETE-REQUEST__&{friend_nick}")

    #  абстрактно здесь будет класс VOICE GUI
    def start_call(self, user, chat_id):
        """Запуск звонка - синхронный вызов"""
        success = self.call_manager.start_call(
            user=user,
            chat_obj=ClientConnections.get_chat_id(),
            host="26.181.96.20",
            port=55559,
            room=chat_id
        )
        ClientConnections.send_service_message(msg_type=f"__CALL-NOTIFICATION__", extra_data={"call_flg": "1"})

    def stop_call(self):
        """Остановка звонка - синхронный вызов"""
        success = self.call_manager.stop_call()
        ClientConnections.send_service_message(msg_type=f"__CALL-NOTIFICATION__", extra_data={"call_flg": "0"})

    def get_voice_flg(self):
        return self.call_manager.get_voice_flg()

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
