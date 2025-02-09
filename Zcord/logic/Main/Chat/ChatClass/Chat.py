from logic.Main.Chat.ChatClass.ChatGUI import Ui_Chat
from PyQt6 import QtWidgets, QtCore
from logic.Main.Chat.Message.Message import Message
from logic.Message import message_client
from logic.Voice import audio_send
from PyQt6.QtGui import QColor


class Chat(QtWidgets.QWidget):
    def __init__(self, chatId, friendNick, user):
        super(Chat, self).__init__()
        self.voice_conn = None
        self.ui = Ui_Chat()
        self.ui.setupUi(self)
        self.ui.Call.hide()
        self.__chatId = chatId
        self.__user = user
        self.__friendNickname = friendNick

        self.ui.UsersNickInChat.setText(friendNick)
        self.ui.UsersLogoinChat.setText(friendNick[0])

        self.ui.User1_icon.setText(self.__user.getNickName()[0])
        self.ui.User2_icon.setText(friendNick[0])
        self.ui.User2_icon.hide()

        self.installEventFilter(self)

        self.ui.Send_button.clicked.connect(self.sendMessage)

        self.ui.ChatScroll.setSpacing(10)
        self.ui.ChatScroll.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.ui.ChatScroll.setSelectionMode(QtWidgets.QListWidget.SelectionMode.NoSelection)

        self.ui.Chat_input_.returnPressed.connect(self.sendMessage)

        self.ui.CallButton.clicked.connect(self.call_voice)
        self.ui.leaveCall.clicked.connect(self.leave_call)

        self.ui.muteMic.clicked.connect(self.mute_mic)
        self.input_mute_flg = False

        self.ui.muteHeadphones.clicked.connect(self.mute_headphones)
        self.output_mute_flg = False

        self.default_icon = f"""
                            border-color: "#8f8f91";
                            """
        self.active_icon = f"""
                            border-color: "#3ba55d";
                            """

        self.reset_timer_icon_1 = QtCore.QTimer()
        self.reset_timer_icon_1.setSingleShot(True)
        self.reset_timer_icon_1.timeout.connect(self.reset_button_style_icon_1)
        self.reset_timer_icon_2 = QtCore.QTimer()
        self.reset_timer_icon_2.setSingleShot(True)
        self.reset_timer_icon_2.timeout.connect(self.reset_button_style_icon_2)

    def sendMessage(self):
        messageText = self.ui.Chat_input_.text()

        if len(messageText) == 0:
            return

        message_client.MessageConnection.send_message(messageText, self.__user.getNickName())
        message = Message(messageText, self.__user.getNickName())

        widget = QtWidgets.QListWidgetItem(self.ui.ChatScroll)
        widget.setSizeHint(message.ui.Message_.sizeHint())

        self.ui.ChatScroll.addItem(widget)
        self.ui.ChatScroll.setItemWidget(widget, message.ui.Message_)
        self.ui.ChatScroll.setCurrentItem(widget)
        self.ui.Chat_input_.clear()

    def recieveMessage(self, sender, text):
        if len(text) == 0:
            return
        message = Message(text, sender)

        widget = QtWidgets.QListWidgetItem(self.ui.ChatScroll)
        widget.setSizeHint(message.ui.Message_.sizeHint())

        self.ui.ChatScroll.addItem(widget)
        self.ui.ChatScroll.setItemWidget(widget, message.ui.Message_)
        self.ui.ChatScroll.setCurrentItem(widget)

        return True

    def leave_call(self):
        self.voice_conn.close()
        self.ui.Call.hide()
        self.voice_conn = None

    def call_voice(self):
        if not self.voice_conn and not audio_send.VoiceConnection.is_running:
            self.voice_conn = audio_send.start_voice()
            self.voice_conn.speech_detected_icon1.connect(self.update_button_style_icon_1)
            self.voice_conn.speech_detected_icon2.connect(self.update_button_style_icon_2)
            self.voice_conn.icon_change.connect(self.show_friend_icon)
            self.ui.Call.show()
        else:
            print("Вы с кем-то уже разговариваете")

    def mute_mic(self):
        if not self.input_mute_flg:
            self.voice_conn.mute_mic(True)
            self.input_mute_flg = True
        else:
            self.voice_conn.mute_mic(False)
            self.input_mute_flg = False

    def mute_headphones(self):
        if not self.output_mute_flg:
            self.voice_conn.mute_head(True)
            self.output_mute_flg = True
        else:
            self.voice_conn.mute_head(False)
            self.output_mute_flg = False

    def update_button_style_icon_1(self, is_speech):
        if is_speech:
            self.ui.User1_icon.setStyleSheet(self.active_icon)
            self.reset_timer_icon_1.start(500)
        else:
            self.reset_timer_icon_1.start(0)

    def reset_button_style_icon_1(self):
        self.ui.User1_icon.setStyleSheet(self.default_icon)

    def update_button_style_icon_2(self, is_speech):
        if is_speech:
            self.ui.User2_icon.setStyleSheet(self.active_icon)
            self.reset_timer_icon_2.start(500)
        else:
            self.reset_timer_icon_2.start(0)

    def reset_button_style_icon_2(self):
        self.ui.User2_icon.setStyleSheet(self.default_icon)

    def show_friend_icon(self, is_show):
        if is_show:
            self.ui.User2_icon.show()
        else:
            self.ui.User2_icon.hide()

    def clearLayout(self):
        self.ui.ChatScroll.clear()

    def getNickName(self):
        return self.__friendNickname

    def getChatWidget(self):
        return self.ui

    def getChatId(self):
        return self.__chatId
