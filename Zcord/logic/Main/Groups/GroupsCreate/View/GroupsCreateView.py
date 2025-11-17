import math

from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QColor, QPainter

from logic.Main.Groups.GroupsCreate.View.CreateGroupQt import Ui_CreateGroup
from logic.Main.Groups.GroupsCreate.View.Widgets.CreateGroupFormQt import Ui_CreateGroupForm
from logic.Main.Groups.GroupsCreate.View.Widgets.GroupCreatedWidget import Ui_SuccessForm


class GroupsCreateView(QtWidgets.QWidget):
    send_form_model = pyqtSignal(str, bool, bool, bool, str)

    def __init__(self):
        super(GroupsCreateView, self).__init__()

        self._ui = Ui_CreateGroup()
        self._ui.setupUi(self)

        self._spinner = DotSpinner()
        self._spinner.hide()

        self._create_group_ui: Ui_CreateGroupForm
        self._init_create_group_ui()
        self._group_created_ui = Ui_SuccessForm()
        self._group_created_ui.setupUi(self)

        self._ui.stackedWidget.addWidget(self._group_created_ui.Wrapper)

        #Проверка на окончание создания группы
        self._form_was_sent: bool = False

    def _init_create_group_ui(self) -> None:
        self._create_group_ui = Ui_CreateGroupForm()
        self._create_group_ui.setupUi(self)
        self._ui.stackedWidget.addWidget(self._create_group_ui.CG_Wrapper)
        self._ui.stackedWidget.setCurrentWidget(self._create_group_ui.CG_Wrapper)

        self._create_group_ui.spinner_frame.setVisible(False)

        self._create_group_ui.spinner_layout.addWidget(self._spinner, alignment=Qt.AlignmentFlag.AlignCenter)

        self._spinner.setFixedSize(20, 20)
        self._create_group_ui.spinner_layout.setSpacing(0)
        self._create_group_ui.Errors.setHidden(True)

        self._create_group_ui.createGroup_button.clicked.connect(self.send_form)

        self._create_group_ui.is_password.toggled.connect(self._create_group_ui.password_wrapper.setVisible)
        self._create_group_ui.is_private.toggled.connect(lambda t: self._create_group_ui.is_password.setVisible(not t))

        self._create_group_ui.password_wrapper.setVisible(False)

    def send_form(self) -> None:  # TODO: Добавить проверку на спец. символы
        """Вьюшная проверка корректности формы"""
        group_name = self._create_group_ui.GroupName_input.text()
        password = self._create_group_ui.Password_input.text()

        is_private = self._create_group_ui.is_private.isChecked()
        is_invite_from_admin = self._create_group_ui.is_inviteGromAdmin.isChecked()
        is_password = self._create_group_ui.is_password.isChecked()

        if len(group_name) == 0:
            if self._create_group_ui.Errors.isHidden():
                self._create_group_ui.Errors.setHidden(False)
            self._create_group_ui.ErrorText.setText('Ошибка: поле "Название группы" не было заполнено')
            return

        if is_password:
            if self._create_group_ui.Errors.isHidden():
                self._create_group_ui.Errors.setHidden(False)

            if len(self._create_group_ui.Password_input.text()) == 0:
                self._create_group_ui.ErrorText.setText('Ошибка: Поле "Пароль" не было заполнено')
                return
            if len(self._create_group_ui.RepeatPassword_input.text()) == 0:
                self._create_group_ui.ErrorText.setText('Ошибка: Поле "Повторить пароль" не было заполнено')
                return
            if self._create_group_ui.Password_input.text().strip() != self._create_group_ui.RepeatPassword_input.text().strip():
                self._create_group_ui.ErrorText.setText('Ошибка: Пароли не совпадают')
                return

        if not self._create_group_ui.Errors.isHidden():
            self._create_group_ui.Errors.setHidden(True)

        self.send_form_model.emit(group_name, is_private, is_invite_from_admin, is_password, password)

    def name_error(self) -> None:
        if self._create_group_ui.Errors.isHidden():
            self._create_group_ui.Errors.setHidden(False)
        self._create_group_ui.ErrorText.setText("Ошибка: такое название группы уже существует")

    def get_widget(self) -> QtWidgets.QFrame:
        return self._ui.Column

    def creating_group(self) -> None:
        self._form_was_sent = True
        self._create_group_ui.spinner_frame.setVisible(True)
        self._spinner.show()

    def show_success_page(self) -> None:
        self._ui.stackedWidget.setCurrentWidget(self._group_created_ui.Wrapper)
        self._form_was_sent = False

    def reload_page(self) -> None:
        if not self._form_was_sent:
            self._init_create_group_ui()


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
