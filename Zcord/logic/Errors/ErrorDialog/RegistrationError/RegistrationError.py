from logic.Errors.ErrorDialog.RegistrationError.RegistrationErrorWindow import Ui_Registrationerror
from PyQt6 import QtWidgets,QtCore

class RegistrationError(QtWidgets.QDialog):
    def __init__(self):
        super(RegistrationError, self).__init__()

        self.ui = Ui_Registrationerror()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.ui.pushButton.clicked.connect(self.closeOnClick)

    def closeOnClick(self):
        self.close()
