from PyQt6 import QtWidgets,QtCore
from logic.Errors.ErrorDialog.UserError.ErrorWindow import Ui_Error

class UserError(QtWidgets.QDialog):
    def __init__(self):
        super(UserError, self).__init__()
        self.ui = Ui_Error()
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.ui.setupUi(self)


        self.ui.pushButton.clicked.connect(self.closeOnClick)


    def closeOnClick(self):
        self.close()

    def mousePressEvent(self, event):
        self.start = self.mapToGlobal(event.pos())
        self.pressing = True

    def mouseMoveEvent(self, event):
        if self.pressing:
            self.end = self.mapToGlobal(event.pos())
            self.movement = self.end-self.start
            self.move(self.mapToGlobal(self.movement))
            self.start = self.end
    def mouseReleaseEvent(self, event):
        self.pressing = False

