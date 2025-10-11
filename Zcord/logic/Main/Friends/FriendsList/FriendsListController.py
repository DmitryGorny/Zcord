from logic.Main.Friends.FriendsList.FriendListModel import IFriendListModel, FriendListModel
from logic.Main.Friends.FriendsList.View.FriendsListView import IFriendListView, FriendListView


class FriendListController:
    def __init__(self, user):
        self._view: IFriendListView = FriendListView()
        self._model: IFriendListModel = FriendListModel(user)

        self._view.connect_remove_friend(self._model.remove_friend)
        self._view.connect_add_friends(self._model.get_friends)

        self._model.connect_add_friend(self._view.add_friend)
        self._model.connect_remove_friend(self._view.remove_friend)

    def get_widget(self):
        return self._view.get_widget()

    def update_view(self):
        self._view.clear_scroll()
        self._model.get_friends()

