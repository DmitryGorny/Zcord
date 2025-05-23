# Form implementation generated from reading ui file 'Parameters.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Parameters(object):
    def setupUi(self, Parameters):
        Parameters.setObjectName("Parameters")
        Parameters.resize(1011, 663)
        Parameters.setStyleSheet("background-color:black;\n"
"padding:0px;\n"
"margin:0px;")
        self.verticalLayout = QtWidgets.QVBoxLayout(Parameters)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.MAIN = QtWidgets.QFrame(parent=Parameters)
        self.MAIN.setObjectName("MAIN")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.MAIN)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.TopBar = QtWidgets.QFrame(parent=self.MAIN)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.TopBar.sizePolicy().hasHeightForWidth())
        self.TopBar.setSizePolicy(sizePolicy)
        self.TopBar.setMinimumSize(QtCore.QSize(0, 100))
        self.TopBar.setStyleSheet("background-color:rgba(34,35,39,255);")
        self.TopBar.setObjectName("TopBar")
        self.TopBar_10 = QtWidgets.QHBoxLayout(self.TopBar)
        self.TopBar_10.setContentsMargins(35, -1, -1, -1)
        self.TopBar_10.setObjectName("TopBar_10")
        self.backButton = QtWidgets.QPushButton(parent=self.TopBar)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.backButton.sizePolicy().hasHeightForWidth())
        self.backButton.setSizePolicy(sizePolicy)
        self.backButton.setMinimumSize(QtCore.QSize(50, 50))
        self.backButton.setMouseTracking(False)
        self.backButton.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
        self.backButton.setStyleSheet("QPushButton {\n"
"    color: white; /* Белый цвет текста */\n"
"    text-align: center; /* Выравнивание текста по центру */\n"
"    font-size: 16px; /* Размер шрифта */\n"
"    border-radius: 15px; /* Закругленные углы */\n"
"    border: 2px solid rgba(58, 60, 65, 255);\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color:rgba(58, 60, 65, 255);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color:  rgba(28, 30, 35, 255);\n"
"}\n"
"\n"
"QPushButton::icon {\n"
"    width: 16px; /* Ширина иконки */\n"
"    height: 16px; /* Высота иконки */\n"
"    margin-right: 5px; /* Отступ справа от иконки */\n"
"}")
        self.backButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("GUI/icon/keyboard_backspace_30dp_E8EAED_FILL0_wght400_GRAD0_opsz24.svg"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.backButton.setIcon(icon)
        self.backButton.setIconSize(QtCore.QSize(50, 50))
        self.backButton.setObjectName("backButton")
        self.TopBar_10.addWidget(self.backButton)
        self.label_1 = QtWidgets.QLabel(parent=self.TopBar)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_1.sizePolicy().hasHeightForWidth())
        self.label_1.setSizePolicy(sizePolicy)
        self.label_1.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.label_1.setAutoFillBackground(False)
        self.label_1.setStyleSheet("color:white;\n"
"border:none;\n"
"font-size:30px;")
        self.label_1.setObjectName("label_1")
        self.TopBar_10.addWidget(self.label_1, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.verticalLayout_2.addWidget(self.TopBar)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.DialogColumn = QtWidgets.QFrame(parent=self.MAIN)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.DialogColumn.sizePolicy().hasHeightForWidth())
        self.DialogColumn.setSizePolicy(sizePolicy)
        self.DialogColumn.setMinimumSize(QtCore.QSize(300, 0))
        self.DialogColumn.setMaximumSize(QtCore.QSize(300, 16777215))
        self.DialogColumn.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.DialogColumn.setStyleSheet("background-color:rgba(38,40,45,255);")
        self.DialogColumn.setObjectName("DialogColumn")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.DialogColumn)
        self.verticalLayout_4.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetDefaultConstraint)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.pushButton_2 = QtWidgets.QPushButton(parent=self.DialogColumn)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_2.sizePolicy().hasHeightForWidth())
        self.pushButton_2.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(-1)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setStyleSheet("QPushButton {\n"
"    background-color: rgba(38, 40, 45, 255);\n"
"    border: 2px solid rgba(58, 60, 65, 255);\n"
"    border-radius: 15px;\n"
"    color: white;\n"
"    padding: 10px 20px;\n"
"    font-size: 16px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: rgba(58, 60, 65, 255);\n"
"    border: 2px solid rgba(78, 80, 85, 255);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: rgba(28, 30, 35, 255);\n"
"    border: 2px solid rgba(48, 50, 55, 255);\n"
"}")
        self.pushButton_2.setObjectName("pushButton_2")
        self.verticalLayout_4.addWidget(self.pushButton_2)
        self.pushButton = QtWidgets.QPushButton(parent=self.DialogColumn)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(-1)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton.setFont(font)
        self.pushButton.setStyleSheet("QPushButton {\n"
"    background-color: rgba(38, 40, 45, 255);\n"
"    border: 2px solid rgba(58, 60, 65, 255);\n"
"    border-radius: 15px;\n"
"    color: white;\n"
"    padding: 10px 20px;\n"
"    font-size: 16px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: rgba(58, 60, 65, 255);\n"
"    border: 2px solid rgba(78, 80, 85, 255);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: rgba(28, 30, 35, 255);\n"
"    border: 2px solid rgba(48, 50, 55, 255);\n"
"}")
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout_4.addWidget(self.pushButton)
        self.pushButton_3 = QtWidgets.QPushButton(parent=self.DialogColumn)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_3.sizePolicy().hasHeightForWidth())
        self.pushButton_3.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(-1)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_3.setFont(font)
        self.pushButton_3.setStyleSheet("QPushButton {\n"
"    background-color: rgba(38, 40, 45, 255);\n"
"    border: 2px solid rgba(58, 60, 65, 255);\n"
"    border-radius: 15px;\n"
"    color: white;\n"
"    padding: 10px 20px;\n"
"    font-size: 16px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: rgba(58, 60, 65, 255);\n"
"    border: 2px solid rgba(78, 80, 85, 255);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: rgba(28, 30, 35, 255);\n"
"    border: 2px solid rgba(48, 50, 55, 255);\n"
"}")
        self.pushButton_3.setObjectName("pushButton_3")
        self.verticalLayout_4.addWidget(self.pushButton_3)
        self.horizontalLayout.addWidget(self.DialogColumn)
        self.OptionWidget = QtWidgets.QStackedWidget(parent=self.MAIN)
        self.OptionWidget.setObjectName("OptionWidget")
        self.page_15 = QtWidgets.QWidget()
        self.page_15.setObjectName("page_15")
        self.OptionWidget.addWidget(self.page_15)
        self.page_16 = QtWidgets.QWidget()
        self.page_16.setObjectName("page_16")
        self.OptionWidget.addWidget(self.page_16)
        self.horizontalLayout.addWidget(self.OptionWidget)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout.addWidget(self.MAIN)

        self.retranslateUi(Parameters)
        QtCore.QMetaObject.connectSlotsByName(Parameters)

    def retranslateUi(self, Parameters):
        _translate = QtCore.QCoreApplication.translate
        Parameters.setWindowTitle(_translate("Parameters", "Form"))
        self.label_1.setText(_translate("Parameters", "Настройки приложения"))
        self.pushButton_2.setText(_translate("Parameters", "Настройки чата"))
        self.pushButton.setText(_translate("Parameters", "Настройки голоса"))
        self.pushButton_3.setText(_translate("Parameters", "Хуй знает ещё не придумал"))
