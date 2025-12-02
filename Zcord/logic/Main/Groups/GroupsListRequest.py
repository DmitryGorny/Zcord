from typing import Dict

from PyQt6 import QtWidgets

from logic.Main.Groups.GroupsCreate.GroupsCreateController import GroupsCreateController
from logic.Main.Groups.GroupsListRequestsQt import Ui_Groups_page
from logic.Main.Groups.GroupsRequests.GroupRequestsController import GroupRequestsController


class GroupsListRequestWidget(QtWidgets.QWidget):
    def __init__(self, user):
        super(GroupsListRequestWidget, self).__init__()

        self._ui = Ui_Groups_page()
        self._ui.setupUi(self)
        self._user = user
        self._pages: Dict[str, QtWidgets.QFrame] = {}

        self._requests_controller = self._init_requests_controller()
        self._create_group_controller = self._init_create_groups_controller()

        self._ui.requests_button.clicked.connect(self._select_requests_page)
        self._ui.create_group.clicked.connect(self._select_create_group_page)

    def get_widget(self) -> QtWidgets.QFrame:
        return self._ui.Wrapper

    def _init_requests_controller(self) -> GroupRequestsController:
        controller = GroupRequestsController(self._user)
        self._pages['requests'] = controller.get_widget()
        self._ui.stackedWidget.addWidget(controller.get_widget())
        self._ui.stackedWidget.setCurrentWidget(controller.get_widget())
        return controller

    def _init_create_groups_controller(self) -> GroupsCreateController:
        controller = GroupsCreateController(self._user)
        self._pages['create'] = controller.get_widget()
        self._ui.stackedWidget.addWidget(controller.get_widget())
        return controller

    def _select_create_group_page(self) -> None:
        self._create_group_controller.reload_page()
        self._ui.stackedWidget.setCurrentWidget(self._pages['create'])

    def _select_requests_page(self) -> None:
        self._requests_controller.reload_page()
        self._ui.stackedWidget.setCurrentWidget(self._pages['requests'])

    def group_was_created(self) -> None:
        self._create_group_controller.group_created()

    def request_received(self, group_id: str, group_name: str, request_id: int):
        self._requests_controller.request_received(group_id=group_id, group_name=group_name, request_id=request_id)
