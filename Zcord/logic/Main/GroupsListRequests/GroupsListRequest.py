from typing import Dict

from PyQt6 import QtWidgets
from logic.Main.GroupsListRequests.GroupsListRequestsQt import Ui_Groups_page
from logic.Main.GroupsListRequests.GroupsRequests.GroupRequestsController import GroupRequestsController


class GroupsListRequestWidget(QtWidgets.QWidget):
    def __init__(self, user):
        super(GroupsListRequestWidget, self).__init__()

        self._ui = Ui_Groups_page()
        self._ui.setupUi(self)
        self._user = user
        self._pages: Dict[str, QtWidgets.QFrame] = {}

        self._requests_controller = self._init_requests_controller()

        self._ui.requests_button.clicked.connect(self._select_requests_page)

    def get_widget(self) -> QtWidgets.QFrame:
        return self._ui.Wrapper

    def _init_requests_controller(self) -> GroupRequestsController:
        controller = GroupRequestsController(self._user)
        self._pages['requests'] = controller.get_widget()
        self._ui.stackedWidget.addWidget(controller.get_widget())
        return controller

    def _select_requests_page(self) -> None:
        self._ui.stackedWidget.setCurrentWidget(self._pages['requests'])
