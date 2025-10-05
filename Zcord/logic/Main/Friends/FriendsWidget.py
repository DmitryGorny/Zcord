from typing import Dict

from PyQt6 import QtWidgets

from logic.Main.Friends.AddFriends.AddFriendsController import AddFriendsController
from logic.Main.Friends.FriendRequestsList.FriendRequestsListController import FriendRequestController
from logic.Main.Friends.FriendsList.FriendsListController import FriendListController
from logic.Main.Friends.FriendsQt import Ui_Friends_page


class FriendsWidget(QtWidgets.QWidget):
    """Класс описывающий виджеты, связанные с друзьями"""
    def __init__(self, user):
        super(FriendsWidget, self).__init__()
        self._ui = Ui_Friends_page()
        self._ui.setupUi(self)

        self._stacked_widgets: Dict[str, QtWidgets.QFrame] = {}

        self._user = user

        self._add_friend_controller: AddFriendsController = self._init_add_friend_widget(self._user)
        self._friend_request_controller: FriendRequestController = self._init_friend_requests_list(self._user)
        self._friend_list_controller: FriendListController = self._init_friends_list(self._user)

        self._ui.requests.clicked.connect(self._select_request_page)
        self._ui.add_friend.clicked.connect(self._select_add_friend_page)
        self._ui.friends.clicked.connect(self._select_friends_list_page)

        self._ui.stackedWidget.setCurrentWidget(self._stacked_widgets['add_friend'])

    def _init_add_friend_widget(self, user) -> AddFriendsController:
        controller = AddFriendsController(user)
        self._ui.stackedWidget.addWidget(controller.get_view_widget())

        self._stacked_widgets['add_friend'] = controller.get_view_widget()
        return controller

    def _init_friend_requests_list(self, user) -> FriendRequestController:
        controller = FriendRequestController(user)
        self._ui.stackedWidget.addWidget(controller.get_view_widget())

        self._stacked_widgets['requests_list'] = controller.get_view_widget()
        return controller

    def _init_friends_list(self, user) -> FriendListController:
        controller = FriendListController(user)
        self._ui.stackedWidget.addWidget(controller.get_widget())

        self._stacked_widgets['friends_list'] = controller.get_widget()
        return controller

    def get_widget(self) -> QtWidgets.QFrame:
        return self._ui.Wrapper

    def add_others_friend_request(self, friend_id: str, username: str) -> None:
        self._friend_request_controller.add_friend_request(friend_id=friend_id, username=username)

    def add_your_friend_request(self, friend_id: str, username: str) -> None:
        self._friend_request_controller.add_your_request(friend_id=friend_id, username=username)

    def remove_your_request(self, user_id: str) -> None:
        self._friend_request_controller.remove_your_request(user_id)

    def remove_others_request(self, user_id: str) -> None:
        self._friend_request_controller.remove_friend_request(user_id)

    def remove_add_friend_widget(self, username: str) -> None:
        self._add_friend_controller.remove_add_friend_widget(username)

    def _select_request_page(self):
        self._ui.stackedWidget.setCurrentWidget(self._stacked_widgets['requests_list'])

    def _select_add_friend_page(self):
        self._ui.stackedWidget.setCurrentWidget(self._stacked_widgets['add_friend'])

    def _select_friends_list_page(self):
        self._friend_list_controller.update_view()
        self._ui.stackedWidget.setCurrentWidget(self._stacked_widgets['friends_list'])


