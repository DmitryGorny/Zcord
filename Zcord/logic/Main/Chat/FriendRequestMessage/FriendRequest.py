# Form implementation generated from reading ui file 'FriendRequest.ui'
#
# Created by: PyQt6 UI code generator 6.7.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(549, 372)
        self.Message_ = QtWidgets.QFrame(parent=Form)
        self.Message_.setGeometry(QtCore.QRect(10, 20, 500, 160))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Message_.sizePolicy().hasHeightForWidth())
        self.Message_.setSizePolicy(sizePolicy)
        self.Message_.setMinimumSize(QtCore.QSize(500, 160))
        self.Message_.setMaximumSize(QtCore.QSize(16777215, 160))
        self.Message_.setStyleSheet("QFrame {\n"
"background-color:rgba(38,40,45,255);\n"
"border-radius:25%;\n"
"}\n"
"\n"
"QFrame:acrtive {\n"
"    border:none;\n"
"}")
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
        self._2.setContentsMargins(0, 0, -1, 5)
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
        self.label = QtWidgets.QLabel(parent=self.Message_)
        self.label.setStyleSheet("font-size:20px;\n"
"color:white;")
        self.label.setObjectName("label")
        self.Message.addWidget(self.label)
        self.horizontalFrame = QtWidgets.QFrame(parent=self.Message_)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.horizontalFrame.sizePolicy().hasHeightForWidth())
        self.horizontalFrame.setSizePolicy(sizePolicy)
        self.horizontalFrame.setStyleSheet("QPushButton {\n"
"border:3px solid white;\n"
"border-radius:10%;\n"
"color:white;\n"
"font-size:18px;\n"
"}")
        self.horizontalFrame.setObjectName("horizontalFrame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalFrame)
        self.horizontalLayout.setContentsMargins(0, -1, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.AcceptButton = QtWidgets.QPushButton(parent=self.horizontalFrame)
        self.AcceptButton.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.AcceptButton.setStyleSheet("background-color:white;\n"
"color:rgba(38,40,45,255);")
        self.AcceptButton.setObjectName("AcceptButton")
        self.horizontalLayout.addWidget(self.AcceptButton)
        self.RejectButton = QtWidgets.QPushButton(parent=self.horizontalFrame)
        self.RejectButton.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.RejectButton.setStyleSheet("background-color:#BB271A;\n"
"border-color:#BB271A;\n"
"")
        self.RejectButton.setObjectName("RejectButton")
        self.horizontalLayout.addWidget(self.RejectButton)
        self.Message.addWidget(self.horizontalFrame)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.UserLogo.setText(_translate("Form", "U"))
        self.Users_Name.setText(_translate("Form", "User2"))
        self.label.setText(_translate("Form", "Вам отправлено приглашение в друзья"))
        self.AcceptButton.setText(_translate("Form", "Принять"))
        self.RejectButton.setText(_translate("Form", "Отклонить"))
