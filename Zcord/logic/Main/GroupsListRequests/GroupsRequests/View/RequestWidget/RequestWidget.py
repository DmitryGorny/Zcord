from typing import Callable

from PyQt6 import QtWidgets

from logic.Main.GroupsListRequests.GroupsRequests.View.RequestWidget.GroupRequestQt import Ui_GroupRequest


class RequestWidget(QtWidgets.QWidget):
    def __init__(self, group_name: str, group_id: str):
        super(RequestWidget, self).__init__()

        self._group_name = group_name
        self._group_id = group_id

        self._ui = Ui_GroupRequest()
        self._ui.setupUi(self)

        self._ui.GroupName.setText(self._group_name)
        self._ui.GroupIcon.setText(self._group_name[0])

        self.index = 0

    def get_widget(self) -> QtWidgets.QFrame:
        return self._ui.Group_wrapper

    def connect_accept_requests(self, cb: Callable) -> None:
        self._ui.accept_request.clicked.connect(cb)

    def connect_decline_requests(self, cb: Callable) -> None:
        self._ui.decline_request.clicked.connect(cb)
