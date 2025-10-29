from PyQt6 import QtWidgets
from PyQt6.QtCore import QPoint, Qt, QTimer, QPropertyAnimation
from logic.Main.Chat.View.CallDialog.CallGUI import Ui_Call


class Call(QtWidgets.QDialog):
    def __init__(self, callback, nickname):
        super(Call, self).__init__()
        self.call_dialog = Ui_Call()
        self.call_dialog.setupUi(self)
        self.call_dialog.logo.setText(nickname[0])
        self.call_dialog.NickName.setText(nickname)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.call_dialog.AcceptCall_button.clicked.connect(callback)
        self.call_dialog.DeclineCall_button.clicked.connect(self.hide_call_event)  # hide отображение виджета, а также отправка сообщения в чат об отклонении звонка

        self.pressing = False

    def show_call_event(self):
        print("Пришел ивент звонка")
        self.show()
        self.exec()

    def hide_call_event(self):
        self.hide()

    def mousePressEvent(self, event):
        self.start = self.mapToGlobal(event.pos())
        self.pressing = True

    def mouseMoveEvent(self, event):
        if self.pressing:
            self.end = self.mapToGlobal(event.pos())
            self.movement = self.end - self.start
            self.move(self.mapToGlobal(self.movement))
            self.start = self.end

    def mouseReleaseEvent(self, event):
        self.pressing = False
