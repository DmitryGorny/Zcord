from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QFrame

from logic.Main.Groups.GroupsList.View.GroupInList.GroupInList import GroupInList
from logic.Main.Groups.GroupsList.View.GroupsListQt import Ui_Groups_List
from logic.Main.Groups.GroupsList.View.PasswordDialog.PasswordDialog import PasswordDialog
from logic.Main.miniProfile.MiniProfile import Overlay


class GroupListView(QWidget):
    join_group_model = pyqtSignal(str, bool)
    send_password_model = pyqtSignal(str, str)
    find_group_model = pyqtSignal(str)

    def __init__(self):
        super(GroupListView, self).__init__()

        self._ui = Ui_Groups_List()
        self._ui.setupUi(self)

        self._groups = {}

        self._password_dialog = PasswordDialog()
        self._password_dialog.setParent(self._ui.Column)

        self._password_overlay = Overlay(self._password_dialog)
        self._password_overlay.setParent(self._ui.Column)

        self._password_dialog.close()
        self._password_overlay.close()

        self._ui.group_request.setSpacing(10)
        self._ui.group_request.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self._ui.group_request.setSelectionMode(QtWidgets.QListWidget.SelectionMode.NoSelection)

        self._ui.Search_button.clicked.connect(self.find_group)

    def find_group(self):
        text = self._ui.search_group_input.text().strip()
        if len(text) != 0:
            self.find_group_model.emit(text)

    def add_group(self, group_id: str, group_name: str, number_of_members: str, is_password: bool) -> None:
        group = GroupInList(group_name=group_name, number_of_members=number_of_members, is_password=is_password)
        group.connect_signal(lambda: self.join_group_model.emit(group_id, is_password))

        item = QtWidgets.QListWidgetItem()
        item.setSizeHint(group.get_widget().sizeHint())
        self._ui.group_request.addItem(item)
        self._ui.group_request.setItemWidget(item, group.get_widget())
        group.widget = item

        if group_id in self._groups.keys():
            self.remove_group(group_id)
        self._groups[group_id] = group

    def remove_group(self, group_id: str) -> None:
        if group_id not in self._groups:
            return

        item = self._groups[group_id].widget

        row = self._ui.group_request.row(item)
        taken_item = self._ui.group_request.takeItem(row)

        widget = self._ui.group_request.itemWidget(taken_item)
        if widget:
            widget.deleteLater()

        del taken_item
        del self._groups[group_id]

    def show_password_dialog(self, group_id: str):
        password = self._password_dialog.get_password()
        if password is not None:
            self.send_password_model.emit(group_id, password)

    def send_password(self):
        self._password_dialog.reload_dialog()
        new_rect = QtCore.QRect(
            self._ui.Column.rect().x(),
            self._ui.Column.rect().y(),
            self._ui.Column.width(),
            self._ui.Column.height()
        )
        self._password_overlay.setGeometry(new_rect)

        self._password_overlay.show()
        self._password_dialog.raise_()

        self._password_dialog.exec()

    def get_widget(self) -> QFrame:
        return self._ui.Column
