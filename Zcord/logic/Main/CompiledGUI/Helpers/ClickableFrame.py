from PyQt6 import QtWidgets, QtCore

class ClikableFrame(QtWidgets.QFrame):
    def __init__(self, text):
        super(ClikableFrame, self).__init__()
        self.text = text

    clicked = QtCore.pyqtSignal()

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)

        self.clicked.emit()
