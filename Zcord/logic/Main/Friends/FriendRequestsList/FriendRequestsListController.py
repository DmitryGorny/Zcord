from PyQt6 import QtWidgets

from logic.Main.Friends.FriendRequestsList.FriendRequestsListModel import IFriendRequestListModel, \
    FriendRequestListModel
from logic.Main.Friends.FriendRequestsList.View.FriendRequestsListView import IFriendRequestListView, \
    FriendRequestListView


class FriendRequestController:
    def __init__(self, user):
        self._view: IFriendRequestListView = FriendRequestListView()
        self._model: IFriendRequestListModel = FriendRequestListModel(user)

        self._view.connect_get_my_requests(self._model.get_your_requests)
        self._view.connect_accept_request_model(self._model.accept_request)
        self._view.connect_decline_request_model(self._model.decline_request)
        self._view.connect_recall_request_model(self._model.recall_friend_request)
        self._view.connect_get_others_request(self._model.get_others_request)

        self._model.connect_my_requests_view(self._view.add_your_request)
        self._model.connect_remove_your_request(self._view.remove_your_request)
        self._model.connect_remove_others_request(self._view.remove_friend_request)
        self._model.connect_others_requests_view(self._view.add_others_request)

        self._view.get_request_from_db()

    def get_view_widget(self) -> QtWidgets.QFrame:
        return self._view.get_widget()

    def add_friend_request(self, friend_id: str, username: str) -> None:
        self._view.add_others_request(nickname=username, friend_id=friend_id)

    def add_your_request(self, friend_id: str, username: str) -> None:
        self._view.add_your_request(nickname=username, friend_id=friend_id)

    def remove_your_request(self, user_id: str) -> None:
        self._view.remove_your_request(user_id=user_id)

    def remove_friend_request(self, user_id: str) -> None:
        self._view.remove_friend_request(user_id=user_id)

    def has_request(self) -> bool:
        return self._view.has_request()
