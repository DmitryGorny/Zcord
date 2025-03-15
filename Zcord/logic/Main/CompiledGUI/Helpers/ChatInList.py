from PyQt6 import QtWidgets, QtCore
from .ChatInListGUI import Ui_Form

class ChatInList(QtWidgets.QWidget):
    def __init__(self, logo, name, chat):
        super(ChatInList, self).__init__()

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.chat = chat

        self.ui.user_logo.setText(logo)
        self.ui.user_name.setText(name)

        self.changeIndicatorColor("grey")


    def changeIndicatorColor(self, color):
        qss = f"""background-color:{color};
                    border-radius:5%;
                    
                    """
        self.ui.ActivityIndicator_chatList.setStyleSheet(qss)
