# Form implementation generated from reading ui file 'Message.ui'
#
# Created by: PyQt6 UI code generator 6.7.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(431, 112)
        self.Message_ = QtWidgets.QFrame(parent=Form)
        self.Message_.setGeometry(QtCore.QRect(10, 20, 411, 81))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Message_.sizePolicy().hasHeightForWidth())
        self.Message_.setSizePolicy(sizePolicy)
        self.Message_.setMinimumSize(QtCore.QSize(400, 50))
        self.Message_.setStyleSheet("background-color:rgba(38,40,45,255);\n"
"border-radius:25%;")
        self.Message_.setObjectName("Message_")
        self.Message = QtWidgets.QVBoxLayout(self.Message_)
        self.Message.setContentsMargins(35, -1, -1, 15)
        self.Message.setSpacing(2)
        self.Message.setObjectName("Message")
        self.User = QtWidgets.QFrame(parent=self.Message_)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.User.sizePolicy().hasHeightForWidth())
        self.User.setSizePolicy(sizePolicy)
        self.User.setObjectName("User")
        self._2 = QtWidgets.QHBoxLayout(self.User)
        self._2.setContentsMargins(-1, 0, -1, 5)
        self._2.setSpacing(15)
        self._2.setObjectName("_2")
        self.UserLogo = QtWidgets.QPushButton(parent=self.User)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.UserLogo.sizePolicy().hasHeightForWidth())
        self.UserLogo.setSizePolicy(sizePolicy)
        self.UserLogo.setMinimumSize(QtCore.QSize(30, 30))
        self.UserLogo.setMaximumSize(QtCore.QSize(30, 30))
        self.UserLogo.setStyleSheet("background-color:pink;\n"
"border-radius:15%;\n"
"font-size:18px;\n"
"")
        self.UserLogo.setObjectName("UserLogo")
        self._2.addWidget(self.UserLogo)
        self.Users_Name = QtWidgets.QLabel(parent=self.User)
        self.Users_Name.setStyleSheet("color:white;\n"
"font-size:18px;")
        self.Users_Name.setObjectName("Users_Name")
        self._2.addWidget(self.Users_Name)
        self.Message.addWidget(self.User)
        self.Message_Text = QtWidgets.QLabel(parent=self.Message_)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Message_Text.sizePolicy().hasHeightForWidth())
        self.Message_Text.setSizePolicy(sizePolicy)
        self.Message_Text.setStyleSheet("color:white;\n"
"font-size:16px;\n"
"margin-left:47px;")
        self.Message_Text.setObjectName("Message_Text")
        self.Message.addWidget(self.Message_Text)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.UserLogo.setText(_translate("Form", "U"))
        self.Users_Name.setText(_translate("Form", "User2"))
        self.Message_Text.setText(_translate("Form", "Text of the message"))