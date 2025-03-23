from PyQt6 import QtWidgets
from PyQt6.QtCore import QByteArray, Qt, QTimer, QPropertyAnimation
from logic.Main.Chat.ChatClass.Call import Ui_Form
from logic.Message import message_client
from logic.Voice import audio_send
import threading


class Call(QtWidgets.QDialog):
    def __init__(self, chatId, friendNick, user, voicepr):
        super(Call, self).__init__()
        self.__chatId = chatId
        self.__user = user
        self.__friendNickname = friendNick
        self.voicepr = voicepr
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.logo.setText(friendNick[0])
        self.ui.NickName.setText(friendNick)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.ui.DeclineCall_button.clicked.connect(self.decline_call_event)  # hide отображение виджета, а также отправка сообщения в чат об отклонении звонка

    def show_call_event(self):
        print("Пришел ивент звонка")
        self.show()
        self.exec()
        self.call_event_timer = threading.Timer(10.0, self.hide_call_event)

    def hide_call_event(self):
        self.close()

    def decline_call_event(self):
        try:
            if self.call_event_timer.is_alive():
                self.call_event_timer.cancel()
        except AttributeError:
            pass
        self.close()
        message_client.MessageConnection.send_message(f"__DECLINE-CALL__&{self.__chatId}&{self.__friendNickname}",
                                                      self.__user.getNickName())

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
