from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import QPropertyAnimation, QRect, QEasingCurve
from .MiniProfileGUI import Ui_Form
from .ChangeStatusGUI import Ui_Menu
from PyQt6.QtGui import QColor, QPainter, QBrush
from logic.Main.ActivitySatus.Activity import Online, Hidden, DisturbBlock, AFK, Status
from logic.Message.message_client import MessageConnection
from ...client.ClientConnections.ClientConnections import ClientConnections


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

@singleton
class MiniProfile(QtWidgets.QDialog): #TODO: Сделать MVC
    def __init__(self, centerOfApp, user):
        super().__init__()

        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.setFixedSize(300, 430)

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.centerOfApp = centerOfApp

        self.ui.logo.setText(user.getNickName()[0])
        self.ui.NickName.setText(user.getNickName())

        self.activityMenu = StatusWidget(self, user)
        self.ui.Activity.installEventFilter(self)
        self.ui.ChangeActivity.clicked.connect(self.show_or_close_activity_menu)
        self.ui.ChangeActivity.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.ui.Activity.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)

    def eventFilter(self, obj, event):
        if obj is self.ui.Activity:
            if event.type() == QtCore.QEvent.Type.MouseButtonPress:
                self.show_or_close_activity_menu()
        else:
            self.activityMenu.close_menu()
            return False

        return super().eventFilter(obj, event)

    def show_or_close_activity_menu(self):
        if not self.activityMenu.isOpended:
            self.activityMenu.show_menu()
        else:
            self.activityMenu.close_menu()

    def showEvent(self, event):
        """Анимация появления окна."""
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(500)  # Длительность анимации
        self.animation.setStartValue(self.calculateStartGeometry())
        self.animation.setEndValue(self.calculateFinalGeometry())
        self.animation.setEasingCurve(QEasingCurve.Type.OutBack)
        self.animation.start()
        #self.animation.finished.connect(self.center_window)

    def calculateStartGeometry(self):
        parent_center = self.parent().rect().center()

        start_x = parent_center.x() + 10
        start_y = parent_center.y() + 10

        return QRect(start_x, start_y, 20, 20)


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

    def change_activity_color(self, color):
        activity_qss = f"""background-color:{color};
                        border-radius:15px;
                        color:White;
                        border:6px solid rgba(16,19,23,255);
                        """

        activity2_qss = f"""background-color:{color};
                            border-radius:7%;
                            color:White;
                            """
        self.ui.ActivityIndicator.setStyleSheet(activity2_qss)
        self.ui.ActivityIndicator_2.setStyleSheet(activity_qss)

    def change_status_text(self, text):
        self.ui.ChangeActivity.setText(text)

@singleton
class Overlay(QtWidgets.QWidget):
    def __init__(self, dialog, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 150);")  # Полупрозрачный черный цвет
        self.dialogWnidow = dialog

    def paintEvent(self, event):
        """Переопределяем метод рисования для корректного отображения overlay."""
        painter = QPainter(self)
        painter.setBrush(QBrush(QColor(0, 0, 0, 150)))  # Цвет и прозрачность
        painter.drawRect(self.rect())

    def mousePressEvent(self, event):
        if QtCore.Qt.MouseButton.LeftButton == event.button():
            self.dialogWnidow.close()
            self.close()


class StatusWidget(QtWidgets.QMenu):
    def __init__(self, miniProfile, user):
        super().__init__()

        self.ui = Ui_Menu()
        self.ui.setupUi(self)

        self.miniProfile = miniProfile

        self.isOpended = False

        self._user = user
        print(self._user.statuses[1])
        self.createButton("В сети", self._user.statuses[0], self.clicked, "green")
        self.createButton("Не активен", self._user.statuses[3], self.clicked, "yellow")
        self.createButton("Не беспокоить", self._user.statuses[1], self.clicked, "red")
        self.createButton("Невидимка", self._user.statuses[2], self.clicked, "grey")


    def show_menu(self):
        self.isOpended = True
        button_pos = self.miniProfile.mapToGlobal(self.miniProfile.rect().bottomRight() + QtCore.QPoint(-8, -120))
        self.exec(button_pos)

    def clicked(self, actvity_status):
        if isinstance(actvity_status, Online):
            ClientConnections.send_service_message(msg_type="USER-STATUS", extra_data={'user-status': 'USER-ONLINE'})
            self.miniProfile.change_activity_color("#008000")
            self.miniProfile.change_status_text("В сети")
            self._user.status = actvity_status
            return

        if isinstance(actvity_status, DisturbBlock):
            ClientConnections.send_service_message(msg_type="USER-STATUS", extra_data={'user-status': 'USER-DISTRUB-BLOCK'})
            self.miniProfile.change_activity_color("red")
            self.miniProfile.change_status_text("Не беспокоить")
            self._user.status = actvity_status
            return

        if isinstance(actvity_status, Hidden):
            ClientConnections.send_service_message(msg_type="USER-STATUS", extra_data={'user-status': 'USER-HIDDEN'})
            self.miniProfile.change_activity_color("grey")
            self.miniProfile.change_status_text("Невидимка")
            self._user.status = actvity_status
            return

        if isinstance(actvity_status, AFK):
            ClientConnections.send_service_message(msg_type="USER-STATUS", extra_data={'user-status': 'USER-AFK'})
            self.miniProfile.change_activity_color("yellow")
            self.miniProfile.change_status_text("Не активен")
            self._user.status = actvity_status
            return

    def close_menu(self) -> bool:
        self.isOpended = False
        self.close()
        return True

    def mousePressEvent(self, event):
        if self.rect().contains(event.pos()):
            event.ignore()
        else:
            super().mousePressEvent(event)

    def createButton(self, name, statusType, callback, color):
        frame = QtWidgets.QFrame()
        frame.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)

        layout = QtWidgets.QHBoxLayout()
        buttonOption = self.MenuOption(name, statusType, callback)
        indicator = self.Indicator(color)

        layout.addWidget(indicator)
        layout.addWidget(buttonOption)

        frame.setLayout(layout)

        self.ui.Wrapper.addWidget(frame)


    class MenuOption(QtWidgets.QPushButton):
        clicked = QtCore.pyqtSignal(Status)
        def __init__(self, name, statusType, callback):
            super().__init__()
            self.setText(name)
            self._statusType = statusType
            self.clicked.connect(callback)
            self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

        def mousePressEvent(self, e):
            print(self._statusType)
            self.clicked.emit(self._statusType)

    class Indicator(QtWidgets.QPushButton):
        def __init__(self, color):
            super().__init__()
            self.qss = f"""
                           background-color:{color};
                           border-radius:7%;
                           color:White;
                        """

            self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
            self.setMinimumSize(15, 15)
            self.setMaximumSize(15, 15)
            self.setStyleSheet(self.qss)








