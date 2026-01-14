import math

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import pyqtSignal, Qt, QTimer, QRect, QEasingCurve, QPropertyAnimation
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import QDialog

from logic.Main.Chat.View.group_view.GroupSettings.view.GroupSettingsQt import Ui_GroupSettings


class GroupSettingsView(QtWidgets.QDialog):
    save_settings_model = pyqtSignal(dict, dict)

    def __init__(self):
        super(GroupSettingsView, self).__init__()

        self._ui = Ui_GroupSettings()
        self._ui.setupUi(self)

        self._setup_widget()

        self._args_list = {
            'is_private': True,
            'is_password': True,
            'is_invite_from_admin': True,
            'group_name': '',
            'password': ''
        }

        self._flags = {
            'name_changed': False
        }

        self._spinner = DotSpinner()
        self._spinner.hide()

        self._ui.save_changes_button.clicked.connect(self._send_settings)
        self._ui.spinner_frame.setHidden(True)
        self._ui.info_label.setHidden(True)
        self._ui.spinner_layout.addWidget(self._spinner, alignment=Qt.AlignmentFlag.AlignCenter)
        self._spinner.setFixedSize(20, 20)
        self._ui.spinner_layout.setSpacing(0)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    def show_widget(self) -> QDialog:
        return self

    def _setup_widget(self) -> None:
        self._ui.password_wrapper.setVisible(False)
        self._ui.change_password_button.clicked.connect(lambda: self._show_hide_password(True) if self._ui.is_password.isChecked() else self._show_hide_password(False))
        self._ui.is_private.toggled.connect(self._on_toggled_private)
        self._ui.is_password.toggled.connect(self._on_toggled_password)
        self._ui.is_inviteGromAdmin.toggled.connect(self._on_toggled_invite)

    def private_group(self, is_private: bool) -> None:
        self._args_list['is_private'] = is_private
        if is_private:
            self._ui.is_private.setChecked(True)
        else:
            self._ui.is_private.setChecked(False)

    def invite_from_admin_only(self, is_invite_from_admin: bool) -> None:
        self._args_list['is_invite_from_admin'] = is_invite_from_admin
        if is_invite_from_admin:
            self._ui.is_inviteGromAdmin.setChecked(True)
        else:
            self._ui.is_inviteGromAdmin.setChecked(False)

    def is_password(self, is_password: bool) -> None:
        self._args_list['is_password'] = is_password
        if is_password:
            self._ui.is_password.setChecked(True)
        else:
            self._ui.is_password.setChecked(False)

    def group_name(self, group_name: str) -> None:
        self._args_list['group_name'] = group_name
        if len(group_name) > 0:
            self._ui.GroupName.setText(group_name)

    def _show_hide_password(self, show_password: bool) -> None:
        self._ui.password_wrapper.setVisible(show_password)

    def _on_toggled_private(self, is_private: bool) -> None:
        self._args_list['is_private'] = is_private

    def _on_toggled_password(self, is_password: bool) -> None:
        if is_password and not self._args_list['is_password']:
            self._show_hide_password(is_password)
        else:
            self._show_hide_password(is_password)
        self._args_list['is_password'] = is_password

    def _on_toggled_invite(self, is_invite_from_admin: bool) -> None:
        self._args_list['is_invite_from_admin'] = is_invite_from_admin

    def _get_new_name(self) -> bool:
        group_name = self._ui.GroupName.text()
        if self._args_list['group_name'] != group_name:
            self._args_list['group_name'] = group_name
            return True
        return False

    def _send_settings(self) -> None:
        if self._args_list['is_password']:
            if self._ui.error_label.isHidden():
                self._ui.error_label.setHidden(False)

            if self._ui.spinner_frame.isHidden():
                self._ui.spinner_frame.setHidden(False)

            if len(self._ui.Password_input.text()) == 0:
                self._ui.error_label.setText('Ошибка: Поле "Пароль" не было заполнено')
                return
            if len(self._ui.RepeatPassword_input.text()) == 0:
                self._ui.error_label.setText('Ошибка: Поле "Повторить пароль" не было заполнено')
                return
            if self._ui.Password_input.text().strip() != self._ui.RepeatPassword_input.text().strip():
                self._ui.error_label.setText('Ошибка: Пароли не совпадают')
                return
        self._args_list['password'] = self._ui.Password_input.text().strip()
        if self._get_new_name():
            self._flags['name_changed'] = True
        self.save_settings_model.emit(self._args_list, self._flags)
        self._ui.error_label.setHidden(True)

    def data_sent(self) -> None:
        self._ui.save_changes_button.setEnabled(False)
        self._ui.spinner_frame.setHidden(False)
        self._ui.info_label.setHidden(False)
        self._spinner.show()

    def data_sent_success(self) -> None:
        self._ui.save_changes_button.setEnabled(True)
        self._ui.spinner_frame.setHidden(True)
        self._ui.info_label.setHidden(True)
        self._spinner.hide()

    def data_sent_error(self, error: str) -> None:
        self._ui.save_changes_button.setEnabled(True)
        self._spinner.hide()
        self._ui.spinner_frame.setHidden(True)
        self._ui.info_label.setHidden(True)
        self._ui.error_label.setText(error)

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


class DotSpinner(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_angle)
        self.timer.start(16)

        self.dot_count = 8
        self.dot_radius = 4
        self.circle_radius = 8

    def update_angle(self):
        self.angle = (self.angle + 5) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center_x = self.width() / 2
        center_y = self.height() / 2

        for i in range(self.dot_count):
            # угол для каждой точки
            a = math.radians(i * (360 / self.dot_count) + self.angle)

            x = center_x + math.cos(a) * self.circle_radius
            y = center_y + math.sin(a) * self.circle_radius

            # альфа для плавного исчезновения (градиент)
            alpha = int(255 * ((i + 1) / self.dot_count))

            painter.setBrush(QColor(255, 255, 255, alpha))
            painter.setPen(Qt.PenStyle.NoPen)

            painter.drawEllipse(
                int(x - self.dot_radius / 2),
                int(y - self.dot_radius / 2),
                self.dot_radius,
                self.dot_radius
            )
