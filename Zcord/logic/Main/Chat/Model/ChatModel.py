from logic.Main.Friends.FriendAdding import FriendAdding
from logic.client.ClientConnections.ClientConnections import ClientConnections


class ChatModel:
    def __init__(self):
        pass

    def ask_for_cached_messages(self):
        ClientConnections.send_chat_message(f"SCROLL-CACHE-REQUEST")

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
