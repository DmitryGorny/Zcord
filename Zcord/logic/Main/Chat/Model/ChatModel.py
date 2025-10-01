from logic.client.ClientConnections.ClientConnections import ClientConnections


class ChatModel:
    def __init__(self):
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
