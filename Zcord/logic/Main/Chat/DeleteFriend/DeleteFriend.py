from PyQt6 import QtWidgets, QtCore
from logic.Main.Chat.DeleteFriend.DeleteFriendGUI import Ui_DeleteFriend
from PyQt6.QtCore import QPropertyAnimation, QRect, QEasingCurve, QParallelAnimationGroup
from logic.Message import message_client


class DeleteFriend(QtWidgets.QDialog):
    isOpen = False
    def __init__(self, deleteFriendCallback, BlockFriendCallBack):
        super(DeleteFriend, self).__init__()
        self.ui = Ui_DeleteFriend()
        self.ui.setupUi(self)

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.resize(600, 400)  # Устанавливаем конечный размер окна
        self.setWindowOpacity(0)  # Начальная прозрачность

        # Получаем размеры экрана и рассчитываем центр
        screen = QtWidgets.QApplication.primaryScreen()  # Получаем главный экран
        screen_geometry = screen.availableGeometry()

        # Конечная геометрия окна (центрированное)
        self.end_geometry = QRect(
            screen_geometry.x() + (screen_geometry.width() - self.width()) // 2,  # Центрируем по горизонтали
            screen_geometry.y() + (screen_geometry.height() - self.height()) // 2,  # Центрируем по вертикали
            self.width(),
            self.height()
        )

        # Начальная геометрия окна (маленький размер в центре)
        self.start_geometry = QRect(
            self.end_geometry.center().x() - 1,  # Минимальный размер в центре экрана
            self.end_geometry.center().y() - 1,
            2,
            2
        )

        # Устанавливаем начальную геометрию окна
        self.setGeometry(self.start_geometry)

        # Создаем анимацию для геометрии (размер и позиция)
        self.geometry_animation = QPropertyAnimation(self, b"geometry")
        self.geometry_animation.setDuration(500)  # Длительность анимации
        self.geometry_animation.setStartValue(self.start_geometry)
        self.geometry_animation.setEndValue(self.end_geometry)
        self.geometry_animation.setEasingCurve(QEasingCurve.Type.OutBack)  # Эффект плавного выхода

        # Создаем анимацию для прозрачности
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(500)  # Длительность анимации
        self.opacity_animation.setStartValue(0)  # Начальная прозрачность
        self.opacity_animation.setEndValue(1)  # Конечная прозрачность

        # Группируем анимации
        self.animation_group = QParallelAnimationGroup()
        self.animation_group.addAnimation(self.geometry_animation)
        self.animation_group.addAnimation(self.opacity_animation)

        # Запускаем анимацию при показе окна
        self.animation_group.start()

        self.ui.Delete_button.clicked.connect(lambda x: self.deleteFriend(deleteFriendCallback))
        self.ui.Block_button.clicked.connect(lambda x: self.blockFriend(BlockFriendCallBack))
        self.ui.ReturnButtom.clicked.connect(self.closeWindow)

        DeleteFriend.isOpen = True

    def deleteFriend(self, callback):
        callback(True)
        self.closeWindow()

    def blockFriend(self, callback):
        callback()
        self.closeWindow()

    def closeWindow(self):
        self.close()
        DeleteFriend.isOpen = False

    def mousePressEvent(self, event):
        self.start = self.mapToGlobal(event.pos())
        self.pressing = True

    def mouseMoveEvent(self, event):
        if self.pressing:
            self.end = self.mapToGlobal(event.pos())
            self.movement = self.end-self.start
            self.move(self.mapToGlobal(self.movement))
            self.start = self.end

    def mouseReleaseEvent(self, event):
        self.pressing = False


