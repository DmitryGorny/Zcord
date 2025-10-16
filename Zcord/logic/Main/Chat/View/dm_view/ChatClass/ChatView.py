from typing import List

from PyQt6 import QtCore, QtWidgets

from logic.Main.Chat.View.IView.IView import BaseChatView
from logic.Main.Chat.View.dm_view.ChatClass.ChatGUI import Ui_Chat


class ChatView(BaseChatView):

    def __init__(self, chatId, friend_id, user, controller): #TODO: Добавить id второго юзера
        super(ChatView, self).__init__(chatId, user, controller)
        self.ui = Ui_Chat()
        self.ui.setupUi(self)

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

    def getNickName(self):
        return self.__friendNickname

    @property
    def friend_id(self):
        return self._friend_id

