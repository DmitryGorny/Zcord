from typing import List

from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSignal

from logic.Main.Chat.View.GroupInviteDialog.view.FriendWidget.FriendWidget import FriendOptionWidget
from logic.Main.Chat.View.GroupInviteDialog.view.GroupInviteDialogQt import Ui_GroupInviteDial


class GroupInviteView(QtWidgets.QDialog): # TODO: В qt designer добавить ожидание подтверждения создания группы
    create_group_model = pyqtSignal(list, str)

    def __init__(self):
        super(GroupInviteView, self).__init__()
        self._ui = Ui_GroupInviteDial()
        self._ui.setupUi(self)
        self._ui.createGroup_button.clicked.connect(self._create_group)
        self._friends_options: dict[str, FriendOptionWidget] = {}

        self._friends_ids_group: List[str] = []

    def add_friend_option(self, friend_id: str, friend_nick: str) -> None:
        friend_option = FriendOptionWidget(friend_id=friend_id, friend_name=friend_nick)
        friend_option.was_checked.connect(self._add_friend_to_group)
        friend_option.was_unchecked.connect(self._remove_friend_from_group)

        item = QtWidgets.QListWidgetItem()
        item.setSizeHint(friend_option.sizeHint())
        self._ui.friend_list.addItem(item)
        self._ui.friend_list.setItemWidget(item, friend_option.get_widget())

        self._friends_options[friend_id] = friend_option

    def _add_friend_to_group(self, friend_id: str) -> None:
        self._friends_ids_group.append(friend_id)

    def _remove_friend_from_group(self, friend_id: str) -> None:
        try:
            self._friends_ids_group.remove(friend_id)
        except ValueError as e:
            print(e)

    def _create_group(self) -> None:
        group_name = ''
        for fr_id in self._friends_ids_group:
            if len(group_name) >= 15:
                break
            group_name += self._friends_options[fr_id].friend_name

        self.create_group_model.emit(self._friends_ids_group, group_name)
