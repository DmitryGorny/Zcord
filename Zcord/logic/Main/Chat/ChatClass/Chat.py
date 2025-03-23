import threading

from logic.Main.Chat.ChatClass.ChatGUI import Ui_Chat
from PyQt6 import QtWidgets
from logic.Main.Chat.Message.Message import Message
from PyQt6.QtCore import QByteArray, Qt, QTimer, QPropertyAnimation
from logic.Main.Chat.FriendRequestMessage.FriendReauestMessage import FriendRequestMessage
from logic.Message import message_client
from logic.Voice import audio_send
from logic.Main.Friends.FriendAdding import FriendAdding
from logic.Main.Chat.DeleteFriend.DeleteFriend import DeleteFriend
from logic.Main.Chat.ChatClass.AnimatedCall import AnimatedBorderButton
from logic.Main.Chat.ChatClass.CallGui import Call


class Chat(QtWidgets.QWidget):
    def __init__(self, chatId, friendNick, user, voicepr):
        super(Chat, self).__init__()
        self.voice_conn = None
        self.ui = Ui_Chat()
        self.ui.setupUi(self)
        self.voicepr = voicepr

        self.ui.Call.hide()
        self.__chatId = chatId
        self.__user = user
        self.__friendNickname = friendNick

        self.call_event_form = Call(self.__chatId, self.__friendNickname, self.__user, self.voicepr)
        self.call_event_form.ui.AcceptCall_button.clicked.connect(self.accept_call)  # просто подключение к звонку, но может зациклиться если вызывать call_voice
        self.ui.UsersNickInChat.setText(friendNick)
        self.ui.UsersLogoinChat.setText(friendNick[0])

        self.ui.User1_icon.setText(self.__user.getNickName()[0])
        self.ui.User2_icon.setText(friendNick[0])
        self.ui.user1_headphonesMute.hide()
        self.ui.user1_micMute.hide()

        self.ui.user2_micMute.hide()
        self.ui.user2_headphonesMute.hide()
        self.ui.widget_2.hide()

        self.installEventFilter(self)

        self.ui.Send_button.clicked.connect(self.sendMessage)

        self.ui.ChatScroll.setSpacing(10)
        self.ui.ChatScroll.setFocusPolicy(Qt.FocusPolicy.NoFocus)
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
        self.ui.User2_icon.setStyleSheet(self.default_icon)

        self.reset_timer_icon_1 = QTimer()
        self.reset_timer_icon_1.setSingleShot(True)
        self.reset_timer_icon_1.timeout.connect(self.reset_button_style_icon_1)
        self.reset_timer_icon_2 = QTimer()
        self.reset_timer_icon_2.setSingleShot(True)
        self.reset_timer_icon_2.timeout.connect(self.reset_button_style_icon_2)

        self.ui.InfoButton.clicked.connect(self.showDeleteFriendDialog)

        self.ui.ChatScroll.verticalScrollBar().valueChanged.connect(self.askForCachedMessages)

        self.ui.ChatScroll.setVerticalScrollMode(QtWidgets.QListWidget.ScrollMode.ScrollPerPixel)

        if self.__user.getFriends()[self.__friendNickname][1] == 1:
            self.ui.ChatInputLayout.setHidden(True)

        self.messageNumber = None

        self.unseenMessages = []

        self.scroll_pos = 0

    def askForCachedMessages(self, val):
        if val <= int(self.ui.ChatScroll.verticalScrollBar().maximum()/4):
            message_client.MessageConnection.send_message(f"__CACHED-REQUEST__&{self.__chatId}", self.__user.getNickName())


    def sendMessage(self):
        messageText = self.ui.Chat_input_.text()

        if len(messageText) == 0:
            return

        message_client.MessageConnection.send_message(messageText, self.__user.getNickName())
        self.ui.Chat_input_.clear()


    def createUnseenMessageNumber(self, parent):
        self.messageNumber = QtWidgets.QLabel("0", parent=parent)
        self.messageNumber.setVisible(False)

    def recieveMessage(self, sender, text, date, messageIndex = 1, wasSeen:int = 0, event: threading.Event = None): #Нужно еще 20 аргументов
        if self.ui.ChatScroll.verticalScrollBar().signalsBlocked():
            self.ui.ChatScroll.verticalScrollBar().blockSignals(False)

        if len(text) == 0:
            return

        message = Message(text, sender)
        message.ui.date_label.setText(date)

        global qss
        qss = ""
        if sender == self.__user.getNickName():
            qss = """QFrame {
                    background-color:rgba(38,40,45,255);
                    border-radius:25%;
                    border:2px solid white;
                    }
                    }"""

        if wasSeen == 0:
            message.ui.WasSeenlabel.setText("Unseen")
            self.unseenMessages.append(message.ui)

        if len(qss) != 0:
            message.ui.Message_.setStyleSheet(qss)

        widget = QtWidgets.QListWidgetItem()
        widget.setSizeHint(message.ui.Message_.sizeHint())

        if messageIndex == 1:
            self.ui.ChatScroll.addItem(widget)
        else:
            self.ui.ChatScroll.insertItem(0, widget)
            #self.scroll_pos = self.ui.ChatScroll.verticalScrollBar().value()

        self.ui.ChatScroll.setItemWidget(widget, message.ui.Message_)

        if messageIndex == 1:
            self.ui.ChatScroll.setCurrentItem(widget)

        if event is not None:
            event.set()

        return True

    def slotForScroll(self):
        self.ui.ChatScroll.verticalScrollBar().setValue(int(self.ui.ChatScroll.verticalScrollBar().maximum()/4))
    def addMessageOnTop(self, sender, text, date, index, wasSeen:int = 0, event = None): #Надубасил в код жестко
         self.recieveMessage(sender, text, date, index, wasSeen, event)

    def changeUnseenStatus(self, numberOfWidgets):
        print(numberOfWidgets, len(self.unseenMessages))
        if numberOfWidgets >= len(self.unseenMessages):
            numberOfWidgets = len(self.unseenMessages)
        try:
            for messageWidget in range(numberOfWidgets):
                self.unseenMessages[::-1][messageWidget].WasSeenlabel.setText("Seen")
            del self.unseenMessages[-(numberOfWidgets):]
        except Exception:
            return
    def sendFriendRequest(self):
        message_client.MessageConnection.send_message(f"__FRIEND-ADDING__&{self.__chatId}&{self.__friendNickname}", self.__user.getNickName())
        message_client.MessageConnection.addChat(f"{self.__chatId}")

    def showFriendRequestWidget(self, sender):
        message = FriendRequestMessage(sender, self.acceptFriendRequest, self.rejectRequest)

        widget = QtWidgets.QListWidgetItem(self.ui.ChatScroll)
        widget.setSizeHint(message.ui.Message_.sizeHint())

        self.ui.ChatScroll.addItem(widget)
        self.ui.ChatScroll.setItemWidget(widget, message.ui.Message_)
        self.ui.ChatScroll.setCurrentItem(widget)

    def acceptFriendRequest(self):
        friendAdding = FriendAdding(self.__user)

        friendAdding.acceptRequest(self.__friendNickname)

        message_client.MessageConnection.send_message(f"__ACCEPT-REQUEST__&{self.__chatId}&{self.__friendNickname}", self.__user.getNickName())

        self.startMessaging()

    def leave_call(self):
        self.voice_conn.close()
        self.ui.Call.hide()
        self.voice_conn = None

    def call_voice(self):
        if not self.voice_conn and not audio_send.VoiceConnection.is_running:
            self.voice_conn = audio_send.start_voice()
            self.voice_conn.speech_detected_icon1.connect(self.update_button_style_icon_1)
            self.voice_conn.speech_detected_icon2.connect(self.update_button_style_icon_2)
            self.voice_conn.mute_mic_icon2.connect(self.mute_mic_icon_2)
            self.voice_conn.mute_head_icon2.connect(self.mute_head_icon_2)

            self.voicepr.changer_input.connect(self.change_input_device)
            self.voicepr.changer_output.connect(self.change_output_device)
            self.voice_conn.icon_change.connect(self.show_friend_icon)
            self.voice_conn.stop_call_animation.connect(self.stop_call_animate_button)
            self.ui.Call.show()

            self.ui.widget_2.show()
            self.animate_call = AnimatedBorderButton(self.ui.User2_icon)
            self.animate_call.start_animation()

            message_client.MessageConnection.send_message(f"__CALL-EVENT__&{self.__chatId}&{self.__friendNickname}", self.__user.getNickName())
        else:
            print("Вы с кем-то уже разговариваете")

    #  Дубликат функции сверху, ещё не придумал как избавится от цикла сообщения кол_евент
    def accept_call(self):
        if not self.voice_conn and not audio_send.VoiceConnection.is_running:
            self.voice_conn = audio_send.start_voice()
            self.voice_conn.speech_detected_icon1.connect(self.update_button_style_icon_1)
            self.voice_conn.speech_detected_icon2.connect(self.update_button_style_icon_2)
            self.voice_conn.mute_mic_icon2.connect(self.mute_mic_icon_2)
            self.voice_conn.mute_head_icon2.connect(self.mute_head_icon_2)

            self.voicepr.changer_input.connect(self.change_input_device)
            self.voicepr.changer_output.connect(self.change_output_device)
            self.voice_conn.icon_change.connect(self.show_friend_icon)
            self.voice_conn.stop_call_animation.connect(self.stop_call_animate_button)
            self.ui.Call.show()

            self.call_event_form.close()

            self.ui.widget_2.show()
            self.animate_call = AnimatedBorderButton(self.ui.User2_icon)
            self.animate_call.start_animation()
        else:
            print("Вы с кем-то уже разговариваете")

    def stop_call_animate_button(self):
        self.animate_call.stop_animation()
        self.ui.User2_icon.setStyleSheet(self.default_icon)

    def mute_mic_icon_2(self, flg):
        if flg:
            self.ui.user2_micMute.show()
        else:
            self.ui.user2_micMute.hide()

    def mute_head_icon_2(self, flg):
        if flg:
            self.ui.user2_headphonesMute.show()
        else:
            self.ui.user2_headphonesMute.hide()

    def mute_mic(self):
        if not self.input_mute_flg:
            self.voice_conn.mute_mic(True)
            self.input_mute_flg = True
            self.ui.user1_micMute.show()
            self.voice_conn.send_service_bytes(b'MicMute')
        else:
            self.voice_conn.mute_mic(False)
            self.input_mute_flg = False
            self.ui.user1_micMute.hide()
            self.voice_conn.send_service_bytes(b'MicUnMute')

    def mute_headphones(self):
        if not self.output_mute_flg:
            self.voice_conn.mute_head(True)
            self.output_mute_flg = True
            self.ui.user1_headphonesMute.show()
            self.voice_conn.send_service_bytes(b'HeadMute')
        else:
            self.voice_conn.mute_head(False)
            self.output_mute_flg = False
            self.ui.user1_headphonesMute.hide()
            self.voice_conn.send_service_bytes(b'HeadUnMute')

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
            self.ui.widget_2.show()
        else:
            self.ui.widget_2.hide()

    def change_output_device(self, index_output_device):
        if self.voice_conn:
            self.voice_conn.change_device_output(index_output_device)

    def change_input_device(self, index_input_device):
        if self.voice_conn:
            self.voice_conn.change_device_input(index_input_device)

    def startMessaging(self):
        self.ui.ChatInputLayout.setHidden(False)
        self.clearLayout()
    def clearLayout(self):
        self.ui.ChatScroll.verticalScrollBar().blockSignals(True)
        self.ui.ChatScroll.clear()


    def rejectRequest(self, deleteFriend:bool = False):
        friendAdding = FriendAdding(self.__user)
        friendAdding.deleteFriendRequest(self.__friendNickname)
        friendAdding.rejectReques(self.__friendNickname, deleteFriend)

        message_client.MessageConnection.send_message(f"__REJECT-REQUEST__&{self.__chatId}&{self.__friendNickname}", self.__user.getNickName())

    def showDeleteFriendDialog(self):
        if not DeleteFriend.isOpen:
            deleteFriendDialog = DeleteFriend(self.rejectRequest, self.blockUser)

            deleteFriendDialog.show()
            deleteFriendDialog.exec()

    def blockUser(self):
        friendAdding = FriendAdding(self.__user)
        friendAdding.deleteFriendRequest(self.__friendNickname)
        friendAdding.BlockUser(self.__friendNickname)
        message_client.MessageConnection.send_message(f"__DELETE-REQUEST__&{self.__chatId}&{self.__friendNickname}", self.__user.getNickName())

    def getNickName(self):
        return self.__friendNickname

    def getChatWidget(self):
        return self.ui

    def getChatId(self):
        return self.__chatId
