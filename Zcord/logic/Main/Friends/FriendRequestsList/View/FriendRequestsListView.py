from typing import Dict, Protocol, Callable

from PyQt6.QtCore import pyqtSignal
from PyQt6 import QtWidgets, QtCore

from logic.Main.Friends.FriendRequestsList.View.OthersRequest.OthersRequest import OtherRequest
from logic.Main.Friends.FriendRequestsList.View.RequestsQt import Ui_Form
from logic.Main.Friends.FriendRequestsList.View.YourRequest.YourRequest import YourRequest


class IFriendRequestListView(Protocol):
    accept_request_model: pyqtSignal
    decline_request: pyqtSignal
    recall_request_model: pyqtSignal
    get_my_requests_model: pyqtSignal
    get_others_request_model: pyqtSignal

    def add_your_request(self, nickname: str, friend_id: str) -> None:
        pass

    def add_others_request(self, nickname: str, friend_id: str) -> None:
        pass

    def get_widget(self) -> QtWidgets.QFrame:
        pass

    def remove_friend_request(self, user_id: str) -> None:
        pass

    def remove_your_request(self, user_id: str) -> None:
        pass

    def connect_get_my_requests(self, callback: Callable) -> None:
        pass

    def connect_accept_request_model(self, callback: Callable) -> None:
        pass

    def connect_decline_request_model(self, callback: Callable) -> None:
        pass

    def connect_recall_request_model(self, callback: Callable) -> None:
        pass

    def connect_get_others_request(self, callbavk: Callable) -> None:
        pass

    def get_request_from_db(self) -> None:
        pass


class FriendRequestListView(QtWidgets.QWidget):
    accept_request_model = pyqtSignal(str)
    decline_request_model = pyqtSignal(str)
    recall_request_model = pyqtSignal(str)
    get_my_requests_model = pyqtSignal()
    get_others_request_model = pyqtSignal()

    def __init__(self):
        super(FriendRequestListView, self).__init__()
        self._ui = Ui_Form()
        self._ui.setupUi(self)

        self._your_requests: Dict[str, QtWidgets.QWidget] = {}
        self._others_requests: Dict[str, QtWidgets.QWidget] = {}

        self._ui.my_requests.setSpacing(10)
        self._ui.my_requests.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self._ui.my_requests.setSelectionMode(QtWidgets.QListWidget.SelectionMode.NoSelection)

        self._ui.others_request.setSpacing(10)
        self._ui.others_request.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self._ui.others_request.setSelectionMode(QtWidgets.QListWidget.SelectionMode.NoSelection)

    def add_your_request(self, nickname: str, friend_id: str) -> None:
        req = YourRequest(nickname, friend_id)

        if friend_id not in self._your_requests.keys():
            self._your_requests[friend_id] = req

        req.connect_recall_request(lambda: self.recall_request_model.emit(friend_id))

        item = QtWidgets.QListWidgetItem()
        item.setSizeHint(req.get_widget().sizeHint())
        self._ui.my_requests.addItem(item)
        self._ui.my_requests.setItemWidget(item, req.get_widget())
        req.index = self._ui.my_requests.count() - 1

    def add_others_request(self, nickname: str, friend_id: str):
        req = OtherRequest(nickname, friend_id)
        if friend_id not in self._others_requests.keys():
            self._others_requests[friend_id] = req

        item = QtWidgets.QListWidgetItem()
        item.setSizeHint(req.get_widget().sizeHint())
        self._ui.others_request.addItem(item)
        self._ui.others_request.setItemWidget(item, req.get_widget())
        req.index = self._ui.others_request.count() - 1

    def remove_friend_request(self, user_id: str) -> None:
        if user_id not in self._others_requests.keys():
            return

        widget = self._others_requests[user_id]

        item = self._ui.others_request.takeItem(widget.index)
        widget = self._ui.others_request.itemWidget(item)
        self._ui.others_request.removeItemWidget(item)
        if widget:
            widget.deleteLater()
        del self._others_requests[user_id]

    def remove_your_request(self, user_id: str) -> None:
        if user_id not in self._your_requests.keys():
            return

        widget = self._your_requests[user_id]

        item = self._ui.my_requests.takeItem(widget.index)
        widget = self._ui.my_requests.itemWidget(item)
        self._ui.my_requests.removeItemWidget(item)
        if widget:
            widget.deleteLater()
        del self._your_requests[user_id]

    def get_widget(self) -> QtWidgets.QFrame:
        return self._ui.Column

    def connect_get_my_requests(self, callback: Callable) -> None:
        self.get_my_requests_model.connect(callback)

    def connect_accept_request_model(self, callback: Callable) -> None:
        self.accept_request_model.connect(callback)

    def connect_decline_request_model(self, callback: Callable) -> None:
        self.decline_request_model.connect(callback)

    def connect_recall_request_model(self, callback: Callable) -> None:
        self.recall_request_model.connect(callback)

    def connect_get_others_request(self, callback: Callable) -> None:
        self.get_others_request_model.connect(callback)

    def get_request_from_db(self) -> None:
        self.get_my_requests_model.emit()
        self.get_others_request_model.emit()
