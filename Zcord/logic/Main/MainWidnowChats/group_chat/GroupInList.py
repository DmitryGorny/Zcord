from PyQt6 import QtWidgets

from logic.Main.MainWidnowChats.group_chat.GroupInListQt import Ui_Form


class GroupInList(QtWidgets.QWidget):
    def __init__(self, name, chat_id: str, chat_ui):
        super(GroupInList, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.ui.user_logo.setText(name[0])
        self.ui.user_name.setText(name)

        self.username = name
        self._chat_id: str = chat_id
        self.chat_ui = chat_ui

        self.messageNumber = None

    def createUnseenMessageNumber(self, parent):
        self.messageNumber = QtWidgets.QLabel("0", parent=parent)
        self.messageNumber.setVisible(False)
        self.messageNumber.setFixedHeight(25)
        self.messageNumber.setFixedWidth(25)
        self.messageNumber.setStyleSheet("""color:black;
                                    font-size:18px;
                                    border:1px solid white;
                                    border-radius:10%;
                                    padding:0;
                                    padding-bottom:2px;
                                    text-align:center;
                                    background-color:white;""")

    @property
    def id(self):
        return self._chat_id
