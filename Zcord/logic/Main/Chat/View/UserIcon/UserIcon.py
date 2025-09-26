from PyQt6 import QtWidgets

from logic.Main.Chat.View.UserIcon.UserIconQt import Ui_Icon


class UserIcon(QtWidgets.QWidget):
    def __init__(self, client):
        super().__init__()

        self.ui = Ui_Icon()
        self.ui.setupUi(self)
        self.ui.User2_icon_2.setText(client['user'][0])
        self.ui.user2_headphonesMute_2.hide()
        self.ui.user2_micMute_2.hide()
        self.ui.widget_2.show()

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
