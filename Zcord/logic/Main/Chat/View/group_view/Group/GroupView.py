from typing import List

from PyQt6 import QtCore, QtWidgets

from logic.Main.Chat.View.IView.IView import IView, BaseChatView
from logic.Main.Chat.View.group_view.Group.GroupQt import Ui_Group


class GroupView(BaseChatView):
    def __init__(self, chatId, group_name, user, controller, members):
        super(GroupView, self).__init__(chatId, user, controller)

        self.ui = Ui_Group()
        self.ui.setupUi(self)

        self.ui.GroupName.setText(group_name)
        self.ui.GroupIcon.setText(group_name[0])

        self._group_name = group_name

        self.ui.MAIN_ChatLayout.setContentsMargins(0, 0, 0, 0)

        self.ui.Send_button.clicked.connect(self.send_message)

        self.ui.ChatScroll.setSpacing(10)
        self.ui.ChatScroll.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.ui.ChatScroll.setSelectionMode(QtWidgets.QListWidget.SelectionMode.NoSelection)

        self.ui.Chat_input_.returnPressed.connect(self.send_message)

        self.ui.ChatScroll.verticalScrollBar().valueChanged.connect(self.ask_for_cached_messages)

        self.ui.ChatScroll.setVerticalScrollMode(QtWidgets.QListWidget.ScrollMode.ScrollPerPixel)

        self._users: List[str] = members.copy()

    @property
    def group_name(self) -> str:
        return self._group_name

    @property
    def get_users(self):
        return self._users.copy()
