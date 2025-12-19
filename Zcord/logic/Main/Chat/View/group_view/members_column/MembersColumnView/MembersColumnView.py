from typing import Dict

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import pyqtSignal
from logic.Main.Chat.View.group_view.members_column.MembersColumnView.UserCard.UserCard import UserCard


class MembersColumnView:
    kick_member_model = pyqtSignal()

    def __init__(self, column_widget):
        self._ui = column_widget
        self._ui.setSpacing(15)
        self._ui.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self._ui.setSelectionMode(QtWidgets.QListWidget.SelectionMode.NoSelection)
        self._members: Dict[str, UserCard] = {}

    def add_member(self, user_id: str, username: str, is_admin: bool, add_kick_button: bool) -> None:
        card = UserCard(username)

        if user_id not in self._members.keys():
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

    def change_activity_status(self, member_id: str, color: str) -> None:
        member_card = self._members.get(member_id)
        if member_card is None:
            return
        member_card.change_activity(color)
