from PyQt6 import QtWidgets
from PyQt6.QtCore import QTimer
from logic.Main.Chat.View.UserIcon.UserIconQt import Ui_Icon


class UserIcon(QtWidgets.QWidget):
    def __init__(self, client):
        super().__init__()

        self.ui = Ui_Icon()
        self.ui.setupUi(self)
        self.ui.User2_icon_2.setText(client['user'][0].upper())
        self.ui.user2_headphonesMute_2.hide()
        self.ui.user2_micMute_2.hide()
        self.ui.widget_2.show()

        self.default_icon = f"""
                            border-color: "#8f8f91";
                            """
        self.active_icon = f"""
                            border-color: "#3ba55d";
                            """

        self.reset_timer_icon = QTimer()
        self.reset_timer_icon.setSingleShot(True)
        self.reset_timer_icon.timeout.connect(self.default_animation)

    def mute_head(self, flg):
        if flg:
            self.ui.user2_headphonesMute_2.show()
        else:
            self.ui.user2_headphonesMute_2.hide()

    def mute_mic(self, flg):
        if flg:
            self.ui.user2_micMute_2.show()
        else:
            self.ui.user2_micMute_2.hide()

    def speech_animation(self, is_speech):
        if is_speech:
            self.ui.User2_icon_2.setStyleSheet(self.active_icon)
            self.reset_timer_icon.start(500)
        else:
            self.reset_timer_icon.start(0)

    def default_animation(self):
        self.ui.User2_icon_2.setStyleSheet(self.default_icon)
