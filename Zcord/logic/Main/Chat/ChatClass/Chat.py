from logic.Main.Chat.ChatClass.ChatGUI import Ui_Chat
from PyQt6 import QtWidgets, QtCore
from logic.Main.Chat.Message.Message import Message
from logic.Main.Chat.FriendRequestMessage.FriendReauestMessage import FriendRequestMessage
from logic.Message import message_client
from logic.Main.Friends.FriendAdding import FriendAdding
from logic.Main.Chat.DeleteFriend.DeleteFriend import DeleteFriend


class Chat(QtWidgets.QWidget):
    def __init__(self, chatId, friendNick, user):
        super(Chat, self).__init__()

        self.ui = Ui_Chat()
        self.ui.setupUi(self)

        self.__chatId = chatId
        self.__user = user
        self.__friendNickname = friendNick

        self.ui.UsersNickInChat.setText(friendNick)
        self.ui.UsersLogoinChat.setText(friendNick[0])

        self.installEventFilter(self)

        self.ui.Send_button.clicked.connect(self.sendMessage)

        self.ui.ChatScroll.setSpacing(10)
        self.ui.ChatScroll.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.ui.ChatScroll.setSelectionMode(QtWidgets.QListWidget.SelectionMode.NoSelection)

        self.ui.Chat_input_.returnPressed.connect(self.sendMessage)

        self.ui.InfoButton.clicked.connect(self.showDeleteFriendDialog)

        if self.__user.getFriends()[self.__friendNickname][1] == 1:
            self.ui.ChatInputLayout.setHidden(True)

        self.messageNumber = None

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


    def createUnseenMessageNumber(self, parent):
        self.messageNumber = QtWidgets.QLabel("0", parent=parent)
        self.messageNumber.setVisible(False)

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

    def sendFriendRequest(self):
        message_client.MessageConnection.send_message(f"__FRIEND-ADDING__&{self.__chatId}&{self.__friendNickname}", self.__user.getNickName())
        message_client.MessageConnection.addChat(self.__chatId)

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

    def startMessaging(self):
        self.ui.ChatInputLayout.setHidden(False)
        self.clearLayout()
    def clearLayout(self):
        self.ui.ChatScroll.clear()

    def rejectRequest(self, deleteFriend:bool = False):
        friendAdding = FriendAdding(self.__user)

        friendAdding.rejectReques(self.__friendNickname, deleteFriend)

        message_client.MessageConnection.send_message(f"__REJECT-REQUEST__&{self.__chatId}&{self.__friendNickname}", self.__user.getNickName())

    def showDeleteFriendDialog(self):
        if not DeleteFriend.isOpen:
            deleteFriendDialog = DeleteFriend(self.rejectRequest, self.blockUser)

            deleteFriendDialog.show()
            deleteFriendDialog.exec()

    def blockUser(self):
        friendAdding = FriendAdding(self.__user)
        friendAdding.BlockUser(self.__friendNickname)
        message_client.MessageConnection.send_message(f"__DELETE-REQUEST__&{self.__chatId}&{self.__friendNickname}", self.__user.getNickName())

    def getNickName(self):
        return self.__friendNickname

    def getChatWidget(self):
        return self.ui

    def getChatId(self):
        return self.__chatId
