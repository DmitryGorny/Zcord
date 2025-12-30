from typing import Dict

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import pyqtSignal, QObject
from logic.Main.Chat.View.group_view.members_column.MembersColumnView.UserCard.UserCard import UserCard


class MembersColumnView(QObject):
    kick_member_model = pyqtSignal(str)

    def __init__(self, column_widget):
        super(MembersColumnView, self).__init__()
        self._ui = column_widget
        self._ui.setSpacing(15)
        self._ui.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self._ui.setSelectionMode(QtWidgets.QListWidget.SelectionMode.NoSelection)
        self._members: Dict[str, UserCard] = {}

    def add_member(self, user_id: str, username: str, is_admin: bool, add_kick_button: bool) -> None:
        card = UserCard(username)

        if user_id in self._members.keys():
            return

        self._members[user_id] = card

        card.connect_kick_button(lambda: self.kick_member_model.emit(user_id))

        if is_admin:
            card.add_is_admin()

        if add_kick_button:
            card.add_kick_button()

        item = QtWidgets.QListWidgetItem()
        item.setSizeHint(card.get_widget().sizeHint())
        self._ui.addItem(item)
        self._ui.setItemWidget(item, card.get_widget())
        card.widget_id = self._ui.count() - 1

    def change_activity_status(self, member_id: str, color: str) -> None:
        member_card = self._members.get(member_id)
        if member_card is None:
            return
        member_card.change_activity(color)

    def remove_user(self, user_id: str):
        if user_id not in self._members.keys():
            return

        widget = self._members[user_id]

        item = self._ui.takeItem(widget.widget_id)
        widget = self._ui.itemWidget(item)
        self._ui.removeItemWidget(item)
        if widget:
            widget.deleteLater()
        del self._members[user_id]

    def clear_list(self):
        self._ui.clear()
        self._members.clear()
