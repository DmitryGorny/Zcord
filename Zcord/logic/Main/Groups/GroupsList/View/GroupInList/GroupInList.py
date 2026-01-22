from typing import Callable

from PyQt6.QtWidgets import QWidget, QFrame

from logic.Main.Groups.GroupsList.View.GroupInList.GroupsInListQt import Ui_GroupInList


class GroupInList(QWidget):
    def __init__(self, group_name: str, number_of_members: str, is_password: bool):
        super(GroupInList, self).__init__()
        self._ui = Ui_GroupInList()
        self._ui.setupUi(self)

        self._ui.GroupName.setText(group_name)
        self._ui.number_of_members.setText(number_of_members)
        self._ui.has_password.setVisible(is_password)
        self._ui.GroupIcon.setText(group_name[0])

        self.widget = None

    def connect_signal(self, cb: Callable):
        self._ui.join_group.clicked.connect(cb)

    def get_widget(self) -> QFrame:
        return self._ui.Group_wrapper

