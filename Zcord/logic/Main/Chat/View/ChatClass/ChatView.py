import threading
from logic.Main.Chat.View.ChatClass.ChatGUI import Ui_Chat
from PyQt6 import QtWidgets, QtCore
from logic.Main.Chat.View.Message.Message import Message
from logic.Main.Chat.View.FriendRequestMessage.FriendReauestMessage import FriendRequestMessage
from logic.Main.Chat.View.DeleteFriend.DeleteFriend import DeleteFriend



class ChatView(QtWidgets.QWidget):
    messageReceived = QtCore.pyqtSignal(str, str, str, int, int)
    clear_layout = QtCore.pyqtSignal()

    def __init__(self, chatId, friend_nick, user, controller):
        super(ChatView, self).__init__()
        #Сигналы
        self.messageReceived.connect(self.recieveMessage)

        #Сигналы

        self.ui = Ui_Chat()
        self.ui.setupUi(self)

        self._controller = controller

        self.__chatId = chatId
        self.__user = user
        self.__friendNickname = friend_nick

        self.ui.UsersNickInChat.setText(friend_nick)
        self.ui.UsersLogoinChat.setText(friend_nick[0])

        self.installEventFilter(self)

        self.ui.Send_button.clicked.connect(self.sendMessage)

        self.ui.ChatScroll.setSpacing(10)
        self.ui.ChatScroll.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.ui.ChatScroll.setSelectionMode(QtWidgets.QListWidget.SelectionMode.NoSelection)

        self.ui.Chat_input_.returnPressed.connect(self.sendMessage)

        self.ui.InfoButton.clicked.connect(self.showDeleteFriendDialog)

        self.ui.ChatScroll.verticalScrollBar().valueChanged.connect(self.askForCachedMessages)

        self.ui.ChatScroll.setVerticalScrollMode(QtWidgets.QListWidget.ScrollMode.ScrollPerPixel)

        #if self.__user.getFriends()[self.__friendNickname][1] == 1: TODO: Вернуть после переработки
            #self.ui.ChatInputLayout.setHidden(True)

        self.messageNumber = None

        self.unseenMessages = []

        self.scroll_pos = 0


    def askForCachedMessages(self, val):
        if val <= int(self.ui.ChatScroll.verticalScrollBar().maximum()/4):
            self._controller.ask_for_cached_message()


    def sendMessage(self):
        message_text = self.ui.Chat_input_.text()

        if len(message_text) == 0:
            return

        self._controller.send_message(message_text)
        self.ui.Chat_input_.clear()

    @QtCore.pyqtSlot(str, str, str, int, int)
    def recieveMessage(self, sender, text, date, messageIndex=1, wasSeen:int = 0, event: threading.Event = None): #Нужно еще 20 аргументов
        if self.ui.ChatScroll.verticalScrollBar().signalsBlocked():
            self.ui.ChatScroll.verticalScrollBar().blockSignals(False)

        if len(text) == 0:
            return

        message = Message(text, sender)
        message.ui.date_label.setText(date)

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
        if numberOfWidgets >= len(self.unseenMessages):
            numberOfWidgets = len(self.unseenMessages)
        try:
            for messageWidget in range(numberOfWidgets):
                self.unseenMessages[::-1][messageWidget].WasSeenlabel.setText("Seen")
            del self.unseenMessages[-(numberOfWidgets):]
        except Exception:
            return
    def sendFriendRequest(self):
        self._controller.send_friend_request(self.__chatId, self.__friendNickname)

    def showFriendRequestWidget(self, sender):
        message = FriendRequestMessage(sender, self.acceptFriendRequest, self.rejectRequest)

        widget = QtWidgets.QListWidgetItem(self.ui.ChatScroll)
        widget.setSizeHint(message.ui.Message_.sizeHint())

        self.ui.ChatScroll.addItem(widget)
        self.ui.ChatScroll.setItemWidget(widget, message.ui.Message_)
        self.ui.ChatScroll.setCurrentItem(widget)

    def acceptFriendRequest(self):
        self._controller.accept_request(self.__user, self.__friendNickname)
        self.startMessaging()

    def startMessaging(self):
        self.ui.ChatInputLayout.setHidden(False)
        self.clearLayout()

    def clearLayout(self):
        self.ui.ChatScroll.verticalScrollBar().blockSignals(True)
        self.ui.ChatScroll.clear()

    def rejectRequest(self, deleteFriend: bool = False):
        self._controller.reject_request(self.__user, self.__friendNickname, deleteFriend)

    def showDeleteFriendDialog(self):
        if not DeleteFriend.isOpen:
            deleteFriendDialog = DeleteFriend(self)

            deleteFriendDialog.show()
            deleteFriendDialog.exec()

    def blockUser(self):
        self._controller.block_user(self.__user, self.__friendNickname)

    def getNickName(self):
        return self.__friendNickname

    def getChatWidget(self):
        return self.ui

    def getChatId(self):
        return self.__chatId
