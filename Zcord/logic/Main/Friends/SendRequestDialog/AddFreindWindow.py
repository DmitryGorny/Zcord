from PyQt6 import QtWidgets, QtCore, QtGui
from logic.Main.Friends.SendRequestDialog.FriendWindowGUI import Ui_AddFriend
from logic.Main.Friends.FriendAdding import FriendAdding
from PyQt6.QtCore import QPropertyAnimation, QRect, QEasingCurve, QParallelAnimationGroup


class AddFriendWindow(QtWidgets.QDialog):
    isOpen = False
    def __init__(self, user):
            QtWidgets.QDialog.__init__(self)

            self.ui = Ui_AddFriend()
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


            self.ui.minimizeWindow_2.clicked.connect(self.on_click_hide)
            self.ui.closeWindowButton_2.clicked.connect(self.closeWindow)

            self.ui.AddFriend_button.clicked.connect(self.SendFriendshipRequest)

            self.__user = user

            AddFriendWindow.isOpen = True

            self.__senderAndReciever = []

    def getSenderAndReciver(self):
        return self.__senderAndReciever

    def clearSenderAndReciever(self):
        self.__senderAndReciever.clear()
    def closeWindow(self):
        AddFriendWindow.isOpen = False

        self.close()
    def SendFriendshipRequest(self):
        FriendsADD = FriendAdding(self.__user)

        if len(self.ui.FriendsNick_input.text()) == 0:
            self.ui.FriendsNick_input.setStyleSheet("""QLineEdit {
                                                         width:250px;
                                                        height:30px;
                                                        border: 2px solid #f5737a;
                                                        border-radius: 10px;
                                                        background-color:#323338;
                                                        font-size:16px;
                                                        color:#808994;
                                                        text-align:left;
                                                        padding-left:15px;
                                                        }""")

        isRequestSent = FriendsADD.sendRequest(self.ui.FriendsNick_input.text())

        if isRequestSent:
            self.ui.Status.setIcon(QtGui.QIcon("GUI/icon/done_outline_40dp_78A75A_FILL0_wght400_GRAD0_opsz40.svg"))
            self.ui.Status.setIconSize(QtCore.QSize(20, 20))
            self.__senderAndReciever = [self.__user.getNickName(), self.ui.FriendsNick_input.text()] #Возвращает ник отправителя и получателя
            self.close()
        else:
            self.ui.Status.setIcon(QtGui.QIcon("GUI/icon/warning_40dp_BB271A_FILL0_wght400_GRAD0_opsz40.svg"))
            self.ui.Status.setIconSize(QtCore.QSize(20, 20))

    def on_click_hide(self):
        self.showMinimized()

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
