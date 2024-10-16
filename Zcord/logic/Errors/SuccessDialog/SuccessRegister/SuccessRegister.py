from logic.Errors.SuccessDialog.SuccessRegister.SuccessRegisterWindow import Ui_SuccessRegister
from PyQt6 import QtWidgets,QtCore

class SuccessRegister(QtWidgets.QDialog):
    def __init__(self):
        super(SuccessRegister, self).__init__()
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.ui = Ui_SuccessRegister()
        self.ui.setupUi(self)


        self.ui.Ok_button.clicked.connect(self.closeOnClick)

    def closeOnClick(self):
        self.close()
