from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import QRect, QEasingCurve, QPropertyAnimation
from PyQt6.QtWidgets import QDialog

from logic.Main.Chat.View.group_view.GroupSettings.view.GroupInfoView.GroupInfoQt import Ui_GroupInfo


class GroupInfoView(QDialog):
    def __init__(self, date_of_creation: str):
        super(GroupInfoView, self).__init__()
        self._ui = Ui_GroupInfo()
        self._ui.setupUi(self)

        self._ui.dat_of_creation_label.setText(str(date_of_creation))
        self._ui.is_private.setEnabled(False)
        self._ui.is_inviteGromAdmin.setEnabled(False)
        self._ui.is_password.setEnabled(False)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    def show_widget(self) -> QDialog:
        return self

    def private_group(self, is_private: bool) -> None:
        self._ui.is_private.setChecked(is_private)

    def invite_from_admin_only(self, is_invite_from_admin: bool) -> None:
        self._ui.is_inviteGromAdmin.setChecked(is_invite_from_admin)

    def is_password(self, is_password: bool) -> None:
        self._ui.is_password.setChecked(is_password)

    def group_name(self, group_name: str) -> None:
        if len(group_name) > 0:
            self._ui.group_name_label.setText(group_name)

    def showEvent(self, event):
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(500)
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
        parent_center = self.parent().rect().center()
        final_x = parent_center.x() - self.width() // 2
        final_y = parent_center.y() - self.height() // 2

        return QRect(final_x, final_y, self.width(), self.height())

    def center_child_window(self):
        parent_center = self.parent().rect().center()
        offset_x = parent_center.x() - self.width() // 2
        offset_y = parent_center.y() - self.height() // 2

        self.move(offset_x, offset_y)
