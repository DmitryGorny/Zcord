from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSignal

from logic.Main.Chat.View.GroupInviteDialog.view.FriendWidget.FriendWidgetQt import Ui_FriendOption


class FriendOptionWidget(QtWidgets.QWidget):
    was_checked = pyqtSignal(str)
    was_unchecked = pyqtSignal(str)

    def __init__(self, friend_id: str, friend_name: str):
        super(FriendOptionWidget, self).__init__()
        self._ui = Ui_FriendOption()
        self._ui.setupUi(self)
        self._ui.FriendName.setText(friend_name)
        self._ui.FriendIcon.setText(friend_name[0])

        self._friend_id = friend_id
        self._friend_name = friend_name
        self._ui.add_to_group_box.toggled.connect(self.on_checkbox_toggled)

    def get_widget(self) -> QtWidgets.QFrame:
        return self._ui.Friend_wrapper

    @property
    def friend_name(self) -> str:
        return self._friend_name

    def on_checkbox_toggled(self, is_checked):
        if is_checked:
            self.was_checked.emit(self._friend_id)
        else:
            self.was_unchecked.emit(self._friend_id)
