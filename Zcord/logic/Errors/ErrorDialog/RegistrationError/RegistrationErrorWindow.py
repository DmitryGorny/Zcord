# Form implementation generated from reading ui file 'RegistrationError.ui'
#
# Created by: PyQt6 UI code generator 6.7.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Registrationerror(object):
    def setupUi(self, Registrationerror):
        Registrationerror.setObjectName("Registrationerror")
        Registrationerror.resize(450, 200)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Registrationerror.sizePolicy().hasHeightForWidth())
        Registrationerror.setSizePolicy(sizePolicy)
        Registrationerror.setMinimumSize(QtCore.QSize(450, 200))
        Registrationerror.setMaximumSize(QtCore.QSize(450, 200))
        self.Wrapper = QtWidgets.QFrame(parent=Registrationerror)
        self.Wrapper.setGeometry(QtCore.QRect(0, 0, 450, 200))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Wrapper.sizePolicy().hasHeightForWidth())
        self.Wrapper.setSizePolicy(sizePolicy)
        self.Wrapper.setMinimumSize(QtCore.QSize(450, 200))
        self.Wrapper.setMaximumSize(QtCore.QSize(450, 200))
        self.Wrapper.setStyleSheet("background-color:rgba(38,40,45,255);\n"
"border-radius:50px;\n"
"border:3px solid #BB271A;")
        self.Wrapper.setObjectName("Wrapper")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.Wrapper)
        self.verticalLayout.setContentsMargins(0, 45, 0, 35)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.TextAndIcon_2 = QtWidgets.QFrame(parent=self.Wrapper)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.TextAndIcon_2.sizePolicy().hasHeightForWidth())
        self.TextAndIcon_2.setSizePolicy(sizePolicy)
        self.TextAndIcon_2.setMinimumSize(QtCore.QSize(200, 50))
        self.TextAndIcon_2.setStyleSheet("border:0;")
        self.TextAndIcon_2.setObjectName("TextAndIcon_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.TextAndIcon_2)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.pushButton_2 = QtWidgets.QPushButton(parent=self.TextAndIcon_2)
        self.pushButton_2.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("GUI/icon/warning_40dp_BB271A_FILL0_wght400_GRAD0_opsz40.svg"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.pushButton_2.setIcon(icon)
        self.pushButton_2.setIconSize(QtCore.QSize(40, 40))
        self.pushButton_2.setObjectName("pushButton_2")
        self.verticalLayout_2.addWidget(self.pushButton_2)
        self.ErrorMes = QtWidgets.QLabel(parent=self.TextAndIcon_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ErrorMes.sizePolicy().hasHeightForWidth())
        self.ErrorMes.setSizePolicy(sizePolicy)
        self.ErrorMes.setStyleSheet("font-size:20px;\n"
"color:white;")
        self.ErrorMes.setObjectName("ErrorMes")
        self.verticalLayout_2.addWidget(self.ErrorMes)
        self.verticalLayout.addWidget(self.TextAndIcon_2, 0, QtCore.Qt.AlignmentFlag.AlignHCenter|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.pushButton = QtWidgets.QPushButton(parent=self.Wrapper)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setMinimumSize(QtCore.QSize(150, 30))
        self.pushButton.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.pushButton.setStyleSheet("QPushButton {\n"
"height:30px;\n"
"border: 2px solid #323338;\n"
"border-radius: 10px;\n"
"background-color:#323338;\n"
"font-size:18px;\n"
"color:#808994;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"background-color:#656c76;\n"
"color:black;\n"
"}")
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton, 0, QtCore.Qt.AlignmentFlag.AlignHCenter|QtCore.Qt.AlignmentFlag.AlignBottom)

        self.retranslateUi(Registrationerror)
        QtCore.QMetaObject.connectSlotsByName(Registrationerror)

    def retranslateUi(self, Registrationerror):
        _translate = QtCore.QCoreApplication.translate
        Registrationerror.setWindowTitle(_translate("Registrationerror", "Dialog"))
        self.ErrorMes.setText(_translate("Registrationerror", "Никнейм (логин) занят"))
        self.pushButton.setText(_translate("Registrationerror", "Окей"))
