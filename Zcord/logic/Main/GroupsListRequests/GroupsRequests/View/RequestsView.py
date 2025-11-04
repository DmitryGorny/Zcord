from typing import Callable, Protocol, List, Dict
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import pyqtSignal

from logic.Main.GroupsListRequests.GroupsRequests.View.RequestWidget.RequestWidget import RequestWidget
from logic.Main.GroupsListRequests.GroupsRequests.View.RequestsQt import Ui_Groups_Requests


class IRequestsView(Protocol):
    request_accepted_model: pyqtSignal
    request_declined_model: pyqtSignal

    def add_request(self, group_id: str, group_name: str) -> None:
        pass

    def remove_request(self, group_id: str):
        pass

    def connect_request_accepted(self, cb: Callable) -> None:
        pass

    def connect_decline_accepted(self, cb: Callable) -> None:
        pass

    def get_widget(self) -> QtWidgets.QFrame:
        pass


class RequestsView(QtWidgets.QWidget):
    request_accepted_model = pyqtSignal(str)
    request_declined_model = pyqtSignal(str)

    def __init__(self):
        super(RequestsView, self).__init__()

        self._ui = Ui_Groups_Requests()
        self._ui.setupUi(self)

        self._requests_widgets: Dict[str, RequestWidget] = {}

    def add_request(self, group_id: str, group_name: str) -> None:
        request = RequestWidget(group_name=group_name, group_id=group_id)
        request.connect_accept_requests(lambda: self.request_accepted_model.emit(group_id))
        request.connect_decline_requests(lambda: self.request_declined_model.emit(group_id))

        item = QtWidgets.QListWidgetItem(self._ui.group_request)
        item.setSizeHint(request.sizeHint())
        self._ui.group_request.addItem(item)
        self._ui.group_request.setItemWidget(item, request.get_widget())

        if group_id not in self._requests_widgets.keys():
            self._requests_widgets[group_id] = request
            request.index = self._ui.group_request.count() - 1

    def remove_request(self, group_id: str) -> None:
        if group_id not in self._requests_widgets.keys():
            return

        widget = self._requests_widgets[group_id]

        item = widget.get_widget()
        widget = self._ui.group_request.itemWidget(item)
        self._ui.group_request.removeItemWidget(item)
        if widget:
            widget.deleteLater()
        del self._requests_widgets[group_id]

    def get_widget(self) -> QtWidgets.QFrame:
        return self._ui.Column

    def connect_request_accepted(self, cb: Callable) -> None:
        self.request_accepted_model.connect(cb)

    def connect_decline_accepted(self, cb: Callable) -> None:
        self.request_declined_model.connect(cb)
