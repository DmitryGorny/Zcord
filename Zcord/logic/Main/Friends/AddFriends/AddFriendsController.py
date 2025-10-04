from PyQt6 import QtWidgets

from logic.Main.Friends.AddFriends.AddFriendsModel import IAddFriendModel, AddFriendModel
from logic.Main.Friends.AddFriends.View.AddFriendsView import IAddFriendView, AddFriendView


class AddFriendsController:
    def __init__(self, user):
        self._view: IAddFriendView = AddFriendView()
        self._model: IAddFriendModel = AddFriendModel(user)

        self._view.connect_send_signal(self._model.send_friend_request)  # Сигнал на отправку заявки в друзья
        self._view.connect_find_user_signal(self._model.get_friend_by_nick)
        self._view.connect_recall_request_signal(self._model.recall_friend_request)

        self._model.connect_user_found(self._view.add_found_friend)
        self._model.connect_request_sent(self._view.request_sent)
        self._model.connect_recall_sent(self._view.recall_request)
        self._model.connect_already_friend(self._view.user_is_already_friend)
        self._model.connect_already_sent_request(self._view.request_already_sent)

    def get_view_widget(self) -> QtWidgets.QFrame:
        return self._view.get_widget()

    def remove_add_friend_widget(self, username: str) -> None:
        self._view.remove_request_widget(username)
