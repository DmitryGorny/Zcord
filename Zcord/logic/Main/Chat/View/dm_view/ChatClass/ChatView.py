from PyQt6 import QtCore, QtWidgets
from logic.Main.Chat.View.CallDialog.CallView import Call
from logic.Main.Chat.View.dm_view.GroupInviteDialog.GroupInviteController import GroupInviteController
from logic.Main.Chat.View.IView.IView import BaseChatView
from logic.Main.Chat.View.UserIcon.UserIcon import UserIcon
from logic.Main.Chat.View.dm_view.ChatClass.ChatGUI import Ui_Chat
from logic.Main.miniProfile.MiniProfile import Overlay


class ChatView(BaseChatView):

    def __init__(self, chatId, friend_id, user, controller, is_group):
        super(ChatView, self).__init__(chatId, user, controller, is_group)
        self.ui = Ui_Chat()
        self.ui.setupUi(self)

        # Войс GUI
        self.ui.Call.hide()

        self._friend_id = friend_id

        friend = next(filter(lambda x: x['id'] == friend_id, self._user.getFriends()))
        self.__friendNickname = friend['nickname']

        self.ui.UsersNickInChat.setText(self.__friendNickname)
        self.ui.UsersLogoinChat.setText(self.__friendNickname[0])

        self.ui.MAIN_ChatLayout.setContentsMargins(0, 0, 0, 0)

        self.ui.Send_button.clicked.connect(self.send_message)

        self.ui.ChatScroll.setSpacing(10)
        self.ui.ChatScroll.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.ui.ChatScroll.setSelectionMode(QtWidgets.QListWidget.SelectionMode.NoSelection)

        self.ui.Chat_input_.returnPressed.connect(self.send_message)

        self.ui.ChatScroll.verticalScrollBar().valueChanged.connect(self.ask_for_cached_messages)

        self.ui.ChatScroll.setVerticalScrollMode(QtWidgets.QListWidget.ScrollMode.ScrollPerPixel)

        """Окно приходящего звонка"""
        self.call_dialog = Call(self.start_call, self.__friendNickname)
        self.ui.CallButton.clicked.connect(self.start_call)

        # Подключение кнопок войса
        """Окно чата"""
        self.ui.leaveCall.clicked.connect(self.stop_call)
        self.ui.muteMic.clicked.connect(self.mute_mic_self)
        self.ui.muteHeadphones.clicked.connect(self.mute_head_self)
        self.ui.InviteToGroup.clicked.connect(self.show_group_invite)
        self.ui.videoCall.clicked.connect(self.assign_room)

        self._group_invite_dial_controller: GroupInviteController = GroupInviteController(self._user, self._friend_id)

        self._groups_dialog = self._group_invite_dial_controller.get_widget()
        self._groups_overlay = Overlay(self._groups_dialog)
        self._groups_overlay.setParent(self.ui.Column)
        self._groups_dialog.setParent(self.ui.Column)

        self._groups_dialog.close()
        self._groups_overlay.close()

    #  абстрактно здесь будет класс VOICE GUI
    def start_call(self):
        if self._controller.get_voice_flg():
            return

        self.ui.Call.show()

        """Дальше здесь показана анимация дозвона до собеседника (но перед эти необходимо сделать синхронизацию 
        иконок пользователей с сервером)"""
        client = {
            "user_id": self._friend_id,
            "user": self.__friendNickname
        }

        newcomer = UserIcon(client, self._user, pre_create=True)
        self.client_icons[int(client["user_id"])] = newcomer
        self.ui.UsersFiled_layout.addWidget(newcomer.ui.widget_2, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)

        self._controller.start_call(self._user, self._chat_id)
        self.call_dialog.hide_call_event()

    def getNickName(self):
        return self.__friendNickname

    @property
    def friend_id(self):
        return self._friend_id

    def show_group_invite(self):
        self._group_invite_dial_controller.reload_model()
        new_rect = QtCore.QRect(
            self.ui.Column.rect().x(),
            self.ui.Column.rect().y(),
            self.ui.Column.width(),
            self.ui.Column.height()
        )
        self._groups_overlay.setGeometry(new_rect)

        self._groups_overlay.show()
        self._groups_dialog.raise_()

        self._groups_dialog.exec()

    def close_group_dialog(self):
        if self._groups_overlay.isVisible():
            self._groups_overlay.close()
            self._groups_dialog.close()


