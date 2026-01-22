from typing import Callable, Protocol, List, Dict
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import pyqtSignal

from logic.Main.Groups.GroupsRequests.View.RequestWidget.RequestWidget import RequestWidget
from logic.Main.Groups.GroupsRequests.View.RequestsQt import Ui_Groups_Requests


class IRequestsView(Protocol):
    request_accepted_model: pyqtSignal
    request_declined_model: pyqtSignal

    def add_request(self, group_id: str, group_name: str, request_id: str) -> None:
        pass

    def remove_request(self, group_id: str):
        pass

    def connect_request_accepted(self, cb: Callable) -> None:
        pass

    def connect_decline_accepted(self, cb: Callable) -> None:
        pass

    def get_widget(self) -> QtWidgets.QFrame:
        pass

    def clear_page(self) -> None:
        pass

    def has_request(self) -> bool:
        pass


class RequestsView(QtWidgets.QWidget):
    request_accepted_model = pyqtSignal(str, str)
    request_declined_model = pyqtSignal(str, str)

    def __init__(self):
        super(RequestsView, self).__init__()

        self._ui = Ui_Groups_Requests()
        self._ui.setupUi(self)

        self._requests_widgets: Dict[str, RequestWidget] = {}

    def add_request(self, group_id: str, group_name: str, request_id: str) -> None:
        request = RequestWidget(group_name=group_name, group_id=group_id)
        request.connect_accept_requests(lambda: self.request_accepted_model.emit(str(group_id), str(request_id)))
        request.connect_decline_requests(lambda: self.request_declined_model.emit(str(group_id), str(request_id)))

        item = QtWidgets.QListWidgetItem()
        item.setSizeHint(request.get_widget().sizeHint())
        self._ui.group_request.addItem(item)
        self._ui.group_request.setItemWidget(item, request.get_widget())
        request.widget = item

        if group_id not in self._requests_widgets.keys():
            self._requests_widgets[group_id] = request

    def remove_request(self, group_id: str) -> None:
        if group_id not in self._requests_widgets.keys():
            return

        widget = self._requests_widgets[group_id]

        item = widget.widget
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

    def clear_page(self) -> None:
        self._ui.group_request.clear()

    def has_request(self) -> bool:
        if len(self._requests_widgets) > 0:
            return True
        return False
