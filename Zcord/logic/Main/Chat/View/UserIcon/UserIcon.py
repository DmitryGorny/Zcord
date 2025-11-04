from PyQt6.QtWidgets import QFrame, QWidget
from PyQt6.QtCore import QTimer, Qt, QPoint

from logic.Main.Chat.View.Animation.AnimatedCall import AnimatedBorderButton
from logic.Main.Chat.View.UserIcon.MiniUserIconQt import Ui_Mini_Icon
from logic.Main.Chat.View.UserIcon.UserIconQt import Ui_Icon
from logic.Main.Chat.View.UserIcon.ContextMenuIcon import Ui_Frame
from logic.client.SettingController.settings_controller import VoiceSettingsController


class UserFrame(QFrame, Ui_Frame):
    def __init__(self, user_id):
        super().__init__()
        self.setupUi(self)

        self.settings = VoiceSettingsController()
        self.user_id = user_id
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)

        self.SliderVoice.valueChanged.connect(self.change_volume)
        self.SliderVoice.setValue(int(self.settings.output_volume_friend(self.user_id) * 10))
        self.change_volume()
        #self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        #self.setStyleSheet("background-color: #242429; border-radius: 20px;")

    def show_near_button(self, button):
        """Показывает фрейм рядом с кнопкой, заблокированным для передвижения"""
        global_pos = button.mapToGlobal(QPoint(0, button.height()))  # снизу от кнопки
        self.move(global_pos)
        self.show()

    def change_volume(self):
        current_volume = self.SliderVoice.value() / 10.0
        self.HeadphonesVolume.setText(f"{current_volume}")
        self.settings.save_friend_voice(self.user_id, self.SliderVoice.value())


class UserIcon(QWidget):
    def __init__(self, client, user, pre_create=False):
        super().__init__()

        self.ui = Ui_Icon()
        self.ui.setupUi(self)

        self.ui.User2_icon_2.setText(client['user'][0].upper())
        self.ui.user2_headphonesMute_2.hide()
        self.ui.user2_micMute_2.hide()

        if pre_create:
            self.animate_call = AnimatedBorderButton(self.ui.User2_icon_2)

        self.ui.widget_2.show()

        self.default_icon = f"""
                            border-color: white;
                            """
        self.active_icon = f"""
                            border-color: "#3ba55d";
                            """

        self.reset_timer_icon = QTimer()
        self.reset_timer_icon.setSingleShot(True)
        self.reset_timer_icon.timeout.connect(self.default_animation)

        # TODO создавать специальное окно для себя
        # создаём фрейм для иконки с её параметрами
        if str(user.id) != str(client["user_id"]):
            self.frame = UserFrame(client["user_id"])
            self.ui.User2_icon_2.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.ui.User2_icon_2.customContextMenuRequested.connect(self.on_right_click)

    def on_right_click(self, pos):
        # показать фрейм возле кнопки
        self.frame.show_near_button(self.ui.User2_icon_2)

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
            self.reset_timer_icon.stop()  # отменить таймер, если активен
            self.default_animation()  # сразу вернуть иконку

    def default_animation(self):
        self.ui.User2_icon_2.setStyleSheet(self.default_icon)


class MiniUserIcon(QWidget):
    def __init__(self, user_id, username):
        super().__init__()

        self.ui = Ui_Mini_Icon()
        self.ui.setupUi(self)

        self.ui.UsersLogoinChat.setText(username[0].upper())
        self.ui.UsersLogoinChat.show()
