from typing import List

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import pyqtSignal, QPropertyAnimation, QRect, QEasingCurve

from logic.Main.Chat.View.GroupInviteDialog.view.FriendWidget.FriendWidget import FriendOptionWidget
from logic.Main.Chat.View.GroupInviteDialog.view.GroupInviteDialogQt import Ui_GroupInviteDial


class GroupInviteView(QtWidgets.QDialog):  # TODO: В qt designer добавить ожидание подтверждения создания группы
    create_group_model = pyqtSignal(list)

    def __init__(self, current_friend_id: str):
        super(GroupInviteView, self).__init__()
        self._ui = Ui_GroupInviteDial()
        self._ui.setupUi(self)
        self._ui.createGroup_button.clicked.connect(self._create_group)
        self._friends_options: dict[str, FriendOptionWidget] = {}

        self._current_friend_id = current_friend_id
        self._friends_ids_group: List[str] = [current_friend_id]

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    def add_friend_option(self, friend_id: str, friend_nick: str) -> None:
        if self._current_friend_id == friend_id:
            return
        friend_option = FriendOptionWidget(friend_id=friend_id, friend_name=friend_nick)
        friend_option.was_checked.connect(self._add_friend_to_group)
        friend_option.was_unchecked.connect(self._remove_friend_from_group)

        item = QtWidgets.QListWidgetItem()
        item.setSizeHint(friend_option.sizeHint())
        self._ui.friend_list.addItem(item)
        self._ui.friend_list.setItemWidget(item, friend_option.get_widget())

        self._friends_options[friend_id] = friend_option

    def clear_friends_list(self) -> None:
        self._ui.friend_list.clear()

    def _add_friend_to_group(self, friend_id: str) -> None:
        self._friends_ids_group.append(friend_id)

    def _remove_friend_from_group(self, friend_id: str) -> None:
        try:
            self._friends_ids_group.remove(friend_id)
        except ValueError as e:
            print(e)

    def _create_group(self) -> None:
        self.create_group_model.emit(self._friends_ids_group)

    def get_widget(self) -> QtWidgets.QDialog:
        return self

    def showEvent(self, event):
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(500)  # Длительность анимации
        self.animation.setStartValue(self.calculateStartGeometry())
        self.animation.setEndValue(self.calculateFinalGeometry())
        self.animation.setEasingCurve(QEasingCurve.Type.OutBack)
        self.animation.start()

    def calculateStartGeometry(self):
        parent_center = self.parent().rect().center()

        start_x = parent_center.x() - 10
        start_y = parent_center.y() - 10

        return QRect(start_x, start_y, 350, 350)

    def calculateFinalGeometry(self):
        """Вычисляем конечную геометрию окна (центрированную на экране)."""
        parent_center = self.parent().rect().center()
        # Центрируем дочернее окно относительно центра родителя
        final_x = parent_center.x() - self.width() // 2
        final_y = parent_center.y() - self.height() // 2

        return QRect(final_x, final_y, self.width(), self.height())

    def center_child_window(self):
        parent_center = self.parent().rect().center()
        offset_x = parent_center.x() - self.width() // 2
        offset_y = parent_center.y() - self.height() // 2

        self.move(offset_x, offset_y)
