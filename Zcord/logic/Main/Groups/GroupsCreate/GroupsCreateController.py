from PyQt6 import QtWidgets

from logic.Main.Groups.GroupsCreate.GroupsCreateModel import GroupsCreateModel
from logic.Main.Groups.GroupsCreate.View.GroupsCreateView import GroupsCreateView


class GroupsCreateController:
    def __init__(self, user):
        self._view = GroupsCreateView()
        self._model = GroupsCreateModel(user)

        self._view.send_form_model.connect(self._model.send_form)
        self._model.group_is_being_created_view.connect(self._view.creating_group)
        self._model.name_is_not_unique_view.connect(self._view.name_error)
        self._model.group_created_view.connect(self._view.show_success_page)

    def group_created(self) -> None:
        self._model.group_created()

    def reload_page(self) -> None:
        self._view.reload_page()

    def get_widget(self) -> QtWidgets.QFrame:
        return self._view.get_widget()
