import math

from PyQt6 import QtCore
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtWidgets import QDialog, QWidget

from logic.Main.Groups.GroupsList.View.PasswordDialog.PasswordDialogQt import Ui_GroupPassword
from PyQt6.QtGui import QPainter, QColor


class PasswordDialog(QDialog):
    send_password_signal = pyqtSignal(str)

    def __init__(self):
        super(PasswordDialog, self).__init__()
        self._ui = Ui_GroupPassword()
        self._ui.setupUi(self)

        self.group_id = 0

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    def _get_password(self):
        if self._ui.Errors.isHidden():
            self._ui.Errors.setHidden(False)

            if self._ui.spinner_frame.isHidden():
                self._ui.spinner_frame.setHidden(False)

            if len(self._ui.GroupPassword_input.text()) == 0:
                self._ui.ErrorText.setText('Ошибка: Поле "Пароль" не было заполнено')
                return
        self._ui.Errors.setHidden(True)
        return self._ui.GroupPassword_input.text()

    def password_wrong(self):
        if self._ui.Errors.isHidden():
            self._ui.Errors.setHidden(False)

            if self._ui.spinner_frame.isHidden():
                self._ui.spinner_frame.setHidden(False)

            self._ui.ErrorText.setText('Ошибка: Пароль неверный')
            return

    def reload_dialog(self) -> None:
        self._ui.Errors.setHidden(True)
        self._ui.GroupPassword_input.setText('')

    def _send_password(self, group_id: str):
        password = self._get_password()
        if password is not None:
            self.send_password_signal.emit(group_id, password)

    def showEvent(self, event):
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(500)
        self.animation.setStartValue(self.calculateStartGeometry())
        self.animation.setEndValue(self.calculateFinalGeometry())
        self.animation.setEasingCurve(QEasingCurve.Type.OutBack)
        self.animation.start()

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



class DotSpinner(QWidget):
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
