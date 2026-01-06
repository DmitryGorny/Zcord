from typing import List

from PyQt6 import QtCore, QtWidgets

from logic.Authorization.User.chat.GroupMember import GroupMember
from logic.Main.Chat.View.CallDialog.CallView import Call
from logic.Main.Chat.View.IView.IView import IView, BaseChatView
from logic.Main.Chat.View.UserIcon.UserIcon import UserIcon
from logic.Main.Chat.View.group_view.Group.GroupQt import Ui_Group
from logic.Main.Chat.View.group_view.GroupSettings.GroupSettingsController import GroupSettingsController
from logic.Main.Chat.View.group_view.UserInviteDialog.UserInviteController import UserInviteController
from logic.Main.Chat.View.group_view.members_column.MembersColumnController import MembersColumnController
from logic.Main.miniProfile.MiniProfile import Overlay


class GroupView(BaseChatView):  # TODO: Сделать ui private
    def __init__(self, chatId, group_name, user, controller, members, is_private, is_password, is_admin_invite,
                 admin_id, date_of_creation):
        super(GroupView, self).__init__(chatId, user, controller)

        self.ui = Ui_Group()
        self.ui.setupUi(self)
        self.ui.GroupName.setText(group_name)
        self.ui.GroupIcon.setText(group_name[0])

        self._group_name = group_name

        self.ui.MAIN_ChatLayout.setContentsMargins(0, 0, 0, 0)

        self.ui.Send_button.clicked.connect(self.send_message)

        self.ui.ChatScroll.setSpacing(10)
        self.ui.ChatScroll.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.ui.ChatScroll.setSelectionMode(QtWidgets.QListWidget.SelectionMode.NoSelection)

        self.ui.Chat_input_.returnPressed.connect(self.send_message)

        self.ui.ChatScroll.verticalScrollBar().valueChanged.connect(self.ask_for_cached_messages)

        self.ui.ChatScroll.setVerticalScrollMode(QtWidgets.QListWidget.ScrollMode.ScrollPerPixel)

        self._users: List[GroupMember] = members.copy()
        self.ui.members_number.setText('{} участников,'.format(len(self._users)))

        self._admin_id = admin_id

        self.ui.Call.hide()

        """Приглашения в группу"""
        self._invite_dial_controller: UserInviteController = UserInviteController(self._user, self._chat_id,
                                                                                  self._users)
        self._invite_dialog = self._invite_dial_controller.get_widget()
        self._invite_overlay = Overlay(self._invite_dialog)
        self._invite_overlay.setParent(self.ui.Column)
        self._invite_dialog.setParent(self.ui.Column)

        self._invite_dialog.close()
        self._invite_overlay.close()

        self.ui.invite_user.clicked.connect(self.invite_users)

        """Окно приходящего звонка"""
        self.call_dialog = Call(self.start_call, self._user.getNickName())
        self.ui.CallButton.clicked.connect(self.start_call)

        # Подключение кнопок войса
        """Окно чата"""
        self.ui.leaveCall.clicked.connect(self.stop_call)
        self.ui.muteMic.clicked.connect(self.mute_mic_self)
        self.ui.muteHeadphones.clicked.connect(self.mute_head_self)

        """Участники группы"""
        self._online_users_number = 0
        self.ui.online_members_number.setText('{} в сети'.format(self._online_users_number))

        self.ui.members_column.setHidden(True)
        self._members_column_controller = MembersColumnController(self.ui.members_column, self.ui.members_list,
                                                                  self._user, self.chat_id)
        self._members_column_controller.setup_members(self._users, self._admin_id)
        self.ui.show_members.clicked.connect(self.show_hide_members_column)
        self.ui.leave_group.clicked.connect(self.leave_group)

        """Настройки группы"""
        self._settings_controller: GroupSettingsController = GroupSettingsController(self._user.id,
                                                                                     self._chat_id,
                                                                                     self._group_name,
                                                                                     is_private,
                                                                                     is_admin_invite,
                                                                                     is_password,
                                                                                     date_of_creation)
        self._settings_dialog = self._settings_controller.get_settings_widget()
        self._settings_overlay = Overlay(self._settings_dialog)
        self._settings_overlay.setParent(self.ui.Column)
        self._settings_dialog.setParent(self.ui.Column)

        self._settings_dialog.close()
        self._settings_overlay.close()

        self.ui.show_settings.clicked.connect(self.show_settings)

        """Информация о группе"""

        self._info_dialog = self._settings_controller.get_info_widget()
        self._info_overlay = Overlay(self._info_dialog)
        self._info_dialog.setParent(self.ui.Column)
        self._info_overlay.setParent(self.ui.Column)

        self._info_dialog.close()
        self._info_overlay.close()

        self.ui.info.clicked.connect(self.show_info)

    @property
    def group_name(self) -> str:
        return self._group_name

    @property
    def get_users(self):
        return self._users.copy()

    def start_call(self):
        if self._controller.get_voice_flg():
            return

        self.ui.Call.show()

        """Дальше здесь показана анимация дозвона до собеседника (но перед эти необходимо сделать синхронизацию 
        иконок пользователей с сервером)"""
        client = {
            "user_id": self._user.id,
            "user": self._user.getNickName()
        }

        newcomer = UserIcon(client, self._user, pre_create=True)
        self.client_icons[int(client["user_id"])] = newcomer
        self.ui.UsersFiled_layout.addWidget(newcomer.ui.widget_2, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)

        self._controller.start_call(self._user, self._chat_id)
        self.call_dialog.hide_call_event()

    def invite_users(self):
        self._invite_dial_controller.reload_model()
        new_rect = QtCore.QRect(
            self.ui.Column.rect().x(),
            self.ui.Column.rect().y(),
            self.ui.Column.width(),
            self.ui.Column.height()
        )
        self._invite_overlay.setGeometry(new_rect)

        self._invite_overlay.show()
        self._invite_dialog.raise_()

        self._invite_dialog.exec()

    def show_settings(self):

        if str(self._admin_id) != str(self._user.id):
            return
        self._settings_controller.reload_settings_model()
        new_rect = QtCore.QRect(
            self.ui.Column.rect().x(),
            self.ui.Column.rect().y(),
            self.ui.Column.width(),
            self.ui.Column.height()
        )
        self._settings_overlay.setGeometry(new_rect)

        self._settings_overlay.show()
        self._settings_dialog.raise_()

        self._settings_dialog.exec()

    def show_info(self):
        self._settings_controller.reload_info_model()
        new_rect = QtCore.QRect(
            self.ui.Column.rect().x(),
            self.ui.Column.rect().y(),
            self.ui.Column.width(),
            self.ui.Column.height()
        )
        self._info_overlay.setGeometry(new_rect)

        self._info_overlay.show()
        self._info_dialog.raise_()

        self._info_dialog.exec()

    def close_invite_dialog(self):
        if self._invite_overlay.isVisible():
            self._invite_overlay.close()
            self._invite_dialog.close()

    def admin_changed_settings(self, new_settings: dict) -> None:
        # Передавать методы связанные с правами пользователей и отображением GUI в settings controller через сигналы
        self._settings_controller.admin_changed_settings(new_settings)

    def leave_group(self) -> None:
        self._controller.leave_group(str(self._user.id), self._chat_id)

    def add_member_to_group(self, member: GroupMember) -> None:
        self._users.append(member)
        self._members_column_controller.add_user(member, self._admin_id)

    def show_number_of_members(self) -> None:
        if self._online_users_number > len(self._users):
            self._online_users_number = len(self._users)
            self.ui.online_members_number.setText('{} в сети'.format(self._online_users_number))
        self.ui.members_number.setText('{} участников,'.format(len(self._users)))

    def group_member_offline(self, user_id: str) -> None:
        self._members_column_controller.change_activity_color(user_id, 'grey')
        self._online_users_number -= 1
        self.ui.online_members_number.setText('{} в сети'.format(self._online_users_number))

    def group_member_online(self, member_id: str):
        self._members_column_controller.change_activity_color(member_id, 'green')
        self._online_users_number += 1
        self.ui.online_members_number.setText('{} в сети'.format(self._online_users_number))

    def remove_member(self, member_id: str):
        try:
            member = next(filter(lambda x: x.user_id == member_id, self._users))
        except StopIteration:
            print('[GroupView]')
            return
        self._users.remove(member)
        self.show_number_of_members()
        self._members_column_controller.remove_user(member_id)

    def group_member_status_changed(self, member_id: str, color: str):
        self._members_column_controller.change_activity_color(member_id, color)

    def show_hide_members_column(self) -> None:
        self._members_column_controller.show_hide_members_column()

    def change_admin(self, new_admin_id: str) -> None:
        for user in self._users:
            if user.user_id == new_admin_id:
                user.is_admin = True
            elif user.user_id == self._admin_id:
                user.is_admin = False
        self._members_column_controller.change_admin(self._users, str(new_admin_id))
        self._admin_id = new_admin_id

    def group_settings_changed_fail(self, error_text: str) -> None:
        self._settings_controller.data_sent_error(error_text)

    def change_group_name(self, new_name: str) -> None:
        self.ui.GroupName.setText(new_name)
        self._group_name = new_name

    def __str__(self):
        return self._chat_id
