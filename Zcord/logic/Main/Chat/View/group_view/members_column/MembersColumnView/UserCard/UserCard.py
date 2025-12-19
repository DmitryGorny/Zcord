from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QHBoxLayout, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontMetrics

from logic.Main.Chat.View.group_view.members_column.MembersColumnView.UserCard.UserCardQt import Ui_Form


class ElidedLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._full_text = text
        self.setToolTip(text)
        self.setFixedWidth(75)

    def setText(self, text):
        self._full_text = text
        self.setToolTip(text)
        self._update_elide()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_elide()

    def _update_elide(self):
        metrics = QFontMetrics(self.font())
        elided = metrics.elidedText(
            self._full_text,
            Qt.TextElideMode.ElideRight,
            self.width()
        )
        super().setText(elided)


class UserCard(QWidget):
    def __init__(self, username="Имя пользователя", parent=None):
        super().__init__(parent)

        self.setStyleSheet("""
            QWidget {
                border-radius: 18px;
            }
        """)

        self._ui = Ui_Form()
        self._ui.setupUi(self)

        self._ui.nick_name.setText(username)
        self._ui.member_wrapper.setFixedWidth(250)

        font = QFont()
        font.setPointSize(12)
        font.setWeight(QFont.Weight.Medium)
        self._ui.nick_name.setFont(font)

        self._ui.nick_name.setStyleSheet("color: white; font-size:14px;")

        self._ui.user_logo.setText(username[0])
        self._ui.is_admin.hide()
        self._ui.kick_user.hide()

        self.change_activity('grey')

    def add_is_admin(self):
        self._ui.is_admin.show()

    def add_kick_button(self):
        self._ui.kick_user.show()

    def connect_kick_button(self, cb):
        self._ui.kick_user.clicked.connect(cb)

    def get_widget(self) -> QFrame:
        return self._ui.member_wrapper

    def change_activity(self, color) -> None:
        self._ui.ActivityIndicator_chatList.setStyleSheet(f"""background-color:{color};
                                                            border-radius:5%;
                                                            """)
