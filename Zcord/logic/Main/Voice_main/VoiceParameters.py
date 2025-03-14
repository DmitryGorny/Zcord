# Form implementation generated from reading ui file 'VoiceParameters.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_VoiceParams(object):
    def setupUi(self, VoiceParams):
        VoiceParams.setObjectName("VoiceParams")
        VoiceParams.resize(901, 622)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(VoiceParams.sizePolicy().hasHeightForWidth())
        VoiceParams.setSizePolicy(sizePolicy)
        VoiceParams.setStyleSheet("background-color:black;\n"
"padding:0px;\n"
"margin:0px;")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(VoiceParams)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.settingsWrapper = QtWidgets.QFrame(parent=VoiceParams)
        self.settingsWrapper.setStyleSheet("background-color:rgba(16,19,23,255);")
        self.settingsWrapper.setObjectName("settingsWrapper")
        self.settings = QtWidgets.QVBoxLayout(self.settingsWrapper)
        self.settings.setContentsMargins(25, 25, 25, -1)
        self.settings.setSpacing(0)
        self.settings.setObjectName("settings")
        self.MicroAndHeadphones = QtWidgets.QFrame(parent=self.settingsWrapper)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.MicroAndHeadphones.sizePolicy().hasHeightForWidth())
        self.MicroAndHeadphones.setSizePolicy(sizePolicy)
        self.MicroAndHeadphones.setStyleSheet("QLabel {\n"
"    color:white;\n"
"    font-size:18px;\n"
"}")
        self.MicroAndHeadphones.setObjectName("MicroAndHeadphones")
        self.hboxlayout = QtWidgets.QHBoxLayout(self.MicroAndHeadphones)
        self.hboxlayout.setContentsMargins(-1, 1, -1, 0)
        self.hboxlayout.setObjectName("hboxlayout")
        self.Headphones = QtWidgets.QFrame(parent=self.MicroAndHeadphones)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Headphones.sizePolicy().hasHeightForWidth())
        self.Headphones.setSizePolicy(sizePolicy)
        self.Headphones.setObjectName("Headphones")
        self._3 = QtWidgets.QVBoxLayout(self.Headphones)
        self._3.setObjectName("_3")
        self.ChooseHeadphones = QtWidgets.QFrame(parent=self.Headphones)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ChooseHeadphones.sizePolicy().hasHeightForWidth())
        self.ChooseHeadphones.setSizePolicy(sizePolicy)
        self.ChooseHeadphones.setStyleSheet("QLabel {\n"
"    color:white;\n"
"    font-size:18px;\n"
"}")
        self.ChooseHeadphones.setObjectName("ChooseHeadphones")
        self._4 = QtWidgets.QVBoxLayout(self.ChooseHeadphones)
        self._4.setContentsMargins(1, 1, 1, 1)
        self._4.setSpacing(15)
        self._4.setObjectName("_4")
        self.label = QtWidgets.QLabel(parent=self.ChooseHeadphones)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self._4.addWidget(self.label)
        self.ChooseHeadPhonesBox = QtWidgets.QComboBox(parent=self.ChooseHeadphones)
        self.ChooseHeadPhonesBox.setMinimumSize(QtCore.QSize(0, 40))
        self.ChooseHeadPhonesBox.setStyleSheet("QComboBox {\n"
"    background-color: #2d2d30; /* Тёмно-серый фон */\n"
"    border: 1px solid #3c3c3e; /* Цвет обводки чуть светлее фона */\n"
"    padding: 5px 10px; /* Отступы для текста */\n"
"    font: 20px;\n"
"    color: #ffffff; /* Белый цвет текста */\n"
"}\n"
"\n"
"QComboBox:hover {\n"
"    border: 1px solid orange; /* Голубая обводка при наведении */\n"
"}\n"
"\n"
"QComboBox::drop-down {\n"
"    subcontrol-origin: padding;\n"
"    subcontrol-position: top right; /* Стрелка справа */\n"
"    width: 25px; /* Ширина области стрелки */\n"
"    border-left: 1px solid #3c3c3e; /* Разделитель между стрелкой и текстом */\n"
"}\n"
"\n"
"QComboBox::down-arrow {\n"
"    image: url(GUI/icon/chevron_right_28dp_FFFFFF_FILL0_wght400_GRAD0_opsz24.svg); \n"
"}\n"
"\n"
"QComboBox QAbstractItemView {\n"
"    background-color: #1e1e1e; /* Тёмный фон выпадающего списка */\n"
"    border: 1px solid #3c3c3e; /* Контур выпадающего списка */\n"
"    selection-background-color: #444;\n"
"    selection-color: orange; /* Белый цвет текста при выделении */\n"
"    color:  #ffffff; /* Белый текст для элементов */\n"
"    padding: 5px; /* Отступы внутри выпадающего списка */\n"
"    outline: none; /* Убираем контур */\n"
"}\n"
"\n"
"QComboBox QAbstractItemView::item {\n"
"    padding: 6px 10px; /* Дополнительные отступы внутри элементов */\n"
"}\n"
"\n"
"\n"
"QComboBox QAbstractItemView::item:selected {\n"
"    background-color: orange; /* Синий фон выделенного элемента */\n"
"    color: #ffffff; /* Белый текст */\n"
"}\n"
"")
        self.ChooseHeadPhonesBox.setIconSize(QtCore.QSize(28, 28))
        self.ChooseHeadPhonesBox.setDuplicatesEnabled(False)
        self.ChooseHeadPhonesBox.setObjectName("ChooseHeadPhonesBox")
        self._4.addWidget(self.ChooseHeadPhonesBox)
        self._3.addWidget(self.ChooseHeadphones)
        self.ChooseVolume = QtWidgets.QFrame(parent=self.Headphones)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ChooseVolume.sizePolicy().hasHeightForWidth())
        self.ChooseVolume.setSizePolicy(sizePolicy)
        self.ChooseVolume.setObjectName("ChooseVolume")
        self.ChooseVolume132 = QtWidgets.QVBoxLayout(self.ChooseVolume)
        self.ChooseVolume132.setContentsMargins(0, 15, 0, 0)
        self.ChooseVolume132.setSpacing(15)
        self.ChooseVolume132.setObjectName("ChooseVolume132")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_4 = QtWidgets.QLabel(parent=self.ChooseVolume)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout.addWidget(self.label_4, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.VolimeOfHeadphonesLabel = QtWidgets.QLabel(parent=self.ChooseVolume)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.VolimeOfHeadphonesLabel.sizePolicy().hasHeightForWidth())
        self.VolimeOfHeadphonesLabel.setSizePolicy(sizePolicy)
        self.VolimeOfHeadphonesLabel.setObjectName("VolimeOfHeadphonesLabel")
        self.horizontalLayout.addWidget(self.VolimeOfHeadphonesLabel, 0, QtCore.Qt.AlignmentFlag.AlignRight)
        self.ChooseVolume132.addLayout(self.horizontalLayout)
        self.VolumeOHeadphonesSlider = QtWidgets.QSlider(parent=self.ChooseVolume)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.VolumeOHeadphonesSlider.sizePolicy().hasHeightForWidth())
        self.VolumeOHeadphonesSlider.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setKerning(True)
        self.VolumeOHeadphonesSlider.setFont(font)
        self.VolumeOHeadphonesSlider.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.SplitHCursor))
        self.VolumeOHeadphonesSlider.setAutoFillBackground(False)
        self.VolumeOHeadphonesSlider.setStyleSheet("QSlider{\n"
"                background-color:rgba(16,19,23,255);\n"
"            }\n"
"            QSlider::groove:horizontal {  \n"
"                height: 10px;\n"
"                margin: 0px;\n"
"                border-radius: 5px;\n"
"                background: #B0AEB1;\n"
"            }\n"
"            QSlider::handle:horizontal {\n"
"                background: #fff;\n"
"                border: 1px solid #E3DEE2;\n"
"                width: 17px;\n"
"                margin: -5px 0; \n"
"                border-radius: 8px;\n"
"            }\n"
"            QSlider::sub-page:qlineargradient {\n"
"                background: #3B99FC;\n"
"                border-radius: 5px;\n"
"            }")
        self.VolumeOHeadphonesSlider.setMinimum(0)
        self.VolumeOHeadphonesSlider.setMaximum(30)
        self.VolumeOHeadphonesSlider.setProperty("value", 10)
        self.VolumeOHeadphonesSlider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.VolumeOHeadphonesSlider.setInvertedAppearance(False)
        self.VolumeOHeadphonesSlider.setInvertedControls(False)
        self.VolumeOHeadphonesSlider.setObjectName("VolumeOHeadphonesSlider")
        self.ChooseVolume132.addWidget(self.VolumeOHeadphonesSlider)
        self._3.addWidget(self.ChooseVolume)
        self.hboxlayout.addWidget(self.Headphones)
        self.Micro = QtWidgets.QFrame(parent=self.MicroAndHeadphones)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Micro.sizePolicy().hasHeightForWidth())
        self.Micro.setSizePolicy(sizePolicy)
        self.Micro.setObjectName("Micro")
        self._2 = QtWidgets.QVBoxLayout(self.Micro)
        self._2.setSpacing(7)
        self._2.setObjectName("_2")
        self.ChooseMicro = QtWidgets.QFrame(parent=self.Micro)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ChooseMicro.sizePolicy().hasHeightForWidth())
        self.ChooseMicro.setSizePolicy(sizePolicy)
        self.ChooseMicro.setStyleSheet("QLabel {\n"
"    color:white;\n"
"    font-size:18px;\n"
"}")
        self.ChooseMicro.setObjectName("ChooseMicro")
        self._5 = QtWidgets.QVBoxLayout(self.ChooseMicro)
        self._5.setContentsMargins(1, 1, 1, 1)
        self._5.setSpacing(15)
        self._5.setObjectName("_5")
        self.label_2 = QtWidgets.QLabel(parent=self.ChooseMicro)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName("label_2")
        self._5.addWidget(self.label_2, 0, QtCore.Qt.AlignmentFlag.AlignRight)
        self.ChooseMicroBox = QtWidgets.QComboBox(parent=self.ChooseMicro)
        self.ChooseMicroBox.setMinimumSize(QtCore.QSize(0, 40))
        self.ChooseMicroBox.setStyleSheet("QComboBox {\n"
"    background-color: #2d2d30; /* Тёмно-серый фон */\n"
"    border: 1px solid #3c3c3e; /* Цвет обводки чуть светлее фона */\n"
"    padding: 5px 10px; /* Отступы для текста */\n"
"    font: 20px;\n"
"    color: #ffffff; /* Белый цвет текста */\n"
"}\n"
"\n"
"QComboBox:hover {\n"
"    border: 1px solid orange; /* Голубая обводка при наведении */\n"
"}\n"
"\n"
"QComboBox::drop-down {\n"
"    subcontrol-origin: padding;\n"
"    subcontrol-position: top right; /* Стрелка справа */\n"
"    width: 25px; /* Ширина области стрелки */\n"
"    border-left: 1px solid #3c3c3e; /* Разделитель между стрелкой и текстом */\n"
"}\n"
"\n"
"QComboBox::down-arrow {\n"
"    image: url(GUI/icon/chevron_right_28dp_FFFFFF_FILL0_wght400_GRAD0_opsz24.svg); \n"
"}\n"
"\n"
"QComboBox QAbstractItemView {\n"
"    background-color: #1e1e1e; /* Тёмный фон выпадающего списка */\n"
"    border: 1px solid #3c3c3e; /* Контур выпадающего списка */\n"
"    selection-background-color: #444;\n"
"    selection-color: orange; /* Белый цвет текста при выделении */\n"
"    color:  #ffffff; /* Белый текст для элементов */\n"
"    padding: 5px; /* Отступы внутри выпадающего списка */\n"
"    outline: none; /* Убираем контур */\n"
"}\n"
"\n"
"QComboBox QAbstractItemView::item {\n"
"    padding: 6px 10px; /* Дополнительные отступы внутри элементов */\n"
"}\n"
"\n"
"\n"
"QComboBox QAbstractItemView::item:selected {\n"
"    background-color: orange; /* Синий фон выделенного элемента */\n"
"    color: #ffffff; /* Белый текст */\n"
"}\n"
"")
        self.ChooseMicroBox.setIconSize(QtCore.QSize(28, 28))
        self.ChooseMicroBox.setDuplicatesEnabled(False)
        self.ChooseMicroBox.setObjectName("ChooseMicroBox")
        self._5.addWidget(self.ChooseMicroBox)
        self._2.addWidget(self.ChooseMicro)
        self.ChooseVolumeOfMic = QtWidgets.QFrame(parent=self.Micro)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ChooseVolumeOfMic.sizePolicy().hasHeightForWidth())
        self.ChooseVolumeOfMic.setSizePolicy(sizePolicy)
        self.ChooseVolumeOfMic.setObjectName("ChooseVolumeOfMic")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.ChooseVolumeOfMic)
        self.verticalLayout_5.setContentsMargins(0, 15, 0, 0)
        self.verticalLayout_5.setSpacing(15)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_5 = QtWidgets.QLabel(parent=self.ChooseVolumeOfMic)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_2.addWidget(self.label_5, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.label_6 = QtWidgets.QLabel(parent=self.ChooseVolumeOfMic)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_2.addWidget(self.label_6, 0, QtCore.Qt.AlignmentFlag.AlignRight)
        self.verticalLayout_5.addLayout(self.horizontalLayout_2)
        self.VolumeOfMicSlider = QtWidgets.QSlider(parent=self.ChooseVolumeOfMic)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.VolumeOfMicSlider.sizePolicy().hasHeightForWidth())
        self.VolumeOfMicSlider.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setKerning(True)
        self.VolumeOfMicSlider.setFont(font)
        self.VolumeOfMicSlider.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.SplitHCursor))
        self.VolumeOfMicSlider.setAutoFillBackground(False)
        self.VolumeOfMicSlider.setStyleSheet("QSlider{\n"
"                background-color:rgba(16,19,23,255);\n"
"            }\n"
"            QSlider::groove:horizontal {  \n"
"                height: 10px;\n"
"                margin: 0px;\n"
"                border-radius: 5px;\n"
"                background: #B0AEB1;\n"
"            }\n"
"            QSlider::handle:horizontal {\n"
"                background: #fff;\n"
"                border: 1px solid #E3DEE2;\n"
"                width: 17px;\n"
"                margin: -5px 0; \n"
"                border-radius: 8px;\n"
"            }\n"
"            QSlider::sub-page:qlineargradient {\n"
"                background: #3B99FC;\n"
"                border-radius: 5px;\n"
"            }")
        self.VolumeOfMicSlider.setMinimum(0)
        self.VolumeOfMicSlider.setMaximum(30)
        self.VolumeOfMicSlider.setSingleStep(1)
        self.VolumeOfMicSlider.setProperty("value", 10)
        self.VolumeOfMicSlider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.VolumeOfMicSlider.setInvertedAppearance(False)
        self.VolumeOfMicSlider.setInvertedControls(False)
        self.VolumeOfMicSlider.setObjectName("VolumeOfMicSlider")
        self.verticalLayout_5.addWidget(self.VolumeOfMicSlider)
        self._2.addWidget(self.ChooseVolumeOfMic)
        self.hboxlayout.addWidget(self.Micro)
        self.settings.addWidget(self.MicroAndHeadphones, 0, QtCore.Qt.AlignmentFlag.AlignTop)
        self.NoiseReduce = QtWidgets.QFrame(parent=self.settingsWrapper)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.NoiseReduce.sizePolicy().hasHeightForWidth())
        self.NoiseReduce.setSizePolicy(sizePolicy)
        self.NoiseReduce.setStyleSheet("")
        self.NoiseReduce.setObjectName("NoiseReduce")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.NoiseReduce)
        self.verticalLayout.setContentsMargins(25, 20, 25, 0)
        self.verticalLayout.setSpacing(20)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_7 = QtWidgets.QLabel(parent=self.NoiseReduce)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy)
        self.label_7.setStyleSheet("QLabel {\n"
"    color:white;\n"
"    font-size:18px;\n"
"}")
        self.label_7.setObjectName("label_7")
        self.verticalLayout.addWidget(self.label_7, 0, QtCore.Qt.AlignmentFlag.AlignTop)
        self.label_8 = QtWidgets.QLabel(parent=self.NoiseReduce)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy)
        self.label_8.setStyleSheet("QLabel {\n"
"    color:white;\n"
"    font-size:15px;\n"
"}")
        self.label_8.setObjectName("label_8")
        self.verticalLayout.addWidget(self.label_8)
        self.horizontalFrame = QtWidgets.QFrame(parent=self.NoiseReduce)
        self.horizontalFrame.setObjectName("horizontalFrame")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.horizontalFrame)
        self.horizontalLayout_4.setContentsMargins(0, -1, 0, 0)
        self.horizontalLayout_4.setSpacing(25)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.NoiseReduceWrapper = QtWidgets.QFrame(parent=self.horizontalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.NoiseReduceWrapper.sizePolicy().hasHeightForWidth())
        self.NoiseReduceWrapper.setSizePolicy(sizePolicy)
        self.NoiseReduceWrapper.setMinimumSize(QtCore.QSize(60, 30))
        self.NoiseReduceWrapper.setMaximumSize(QtCore.QSize(16777215, 30))
        self.NoiseReduceWrapper.setStyleSheet("QFrame {\n"
"background-color:grey;\n"
"border-radius:15%;\n"
"}")
        self.NoiseReduceWrapper.setObjectName("NoiseReduceWrapper")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.NoiseReduceWrapper)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.pushButton = QtWidgets.QPushButton(parent=self.NoiseReduceWrapper)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setMinimumSize(QtCore.QSize(30, 30))
        self.pushButton.setStyleSheet("QPushButton {\n"
"background-repeat :no-repeat;\n"
"background-position: center;\n"
"background-image:url(GUI/icon/check_30dp_FFFFFF_FILL0_wght400_GRAD0_opsz24.svg);\n"
"border-radius:15%;\n"
"padding:0px;\n"
"margin:0px;\n"
"background-color:white;\n"
"}\n"
"")
        self.pushButton.setIconSize(QtCore.QSize(24, 24))
        self.pushButton.setCheckable(True)
        self.pushButton.setChecked(False)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_3.addWidget(self.pushButton, 0, QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.horizontalLayout_4.addWidget(self.NoiseReduceWrapper, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.pushButton_2 = QtWidgets.QPushButton(parent=self.horizontalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_2.sizePolicy().hasHeightForWidth())
        self.pushButton_2.setSizePolicy(sizePolicy)
        self.pushButton_2.setMinimumSize(QtCore.QSize(100, 32))
        self.pushButton_2.setMaximumSize(QtCore.QSize(100, 16777215))
        self.pushButton_2.setStyleSheet("background-color:rgba(38,40,45,255);;\n"
"color:white;\n"
"border-radius:10%;\n"
"font-size:18px;\n"
"border:2px solid white;")
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_4.addWidget(self.pushButton_2)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.VolumeCheckWithNoiseReduceSlider = QtWidgets.QSlider(parent=self.horizontalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.VolumeCheckWithNoiseReduceSlider.sizePolicy().hasHeightForWidth())
        self.VolumeCheckWithNoiseReduceSlider.setSizePolicy(sizePolicy)
        self.VolumeCheckWithNoiseReduceSlider.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setKerning(True)
        self.VolumeCheckWithNoiseReduceSlider.setFont(font)
        self.VolumeCheckWithNoiseReduceSlider.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
        self.VolumeCheckWithNoiseReduceSlider.setAutoFillBackground(False)
        self.VolumeCheckWithNoiseReduceSlider.setStyleSheet("QSlider{\n"
"                background-color:rgba(16,19,23,255);\n"
"            }\n"
"            QSlider::groove:horizontal {  \n"
"                height: 10px;\n"
"                margin: 0px;\n"
"                border-radius: 5px;\n"
"                background: #B0AEB1;\n"
"            }\n"
"            QSlider::handle:horizontal {\n"
"                background:none;\n"
"            }\n"
"            QSlider::sub-page:qlineargradient {\n"
"                background: rgba(10, 227, 10, 0.39);\n"
"                border-radius: 5px;\n"
"            }")
        self.VolumeCheckWithNoiseReduceSlider.setMinimum(0)
        self.VolumeCheckWithNoiseReduceSlider.setMaximum(100)
        self.VolumeCheckWithNoiseReduceSlider.setProperty("value", 0)
        self.VolumeCheckWithNoiseReduceSlider.setSliderPosition(0)
        self.VolumeCheckWithNoiseReduceSlider.setTracking(False)
        self.VolumeCheckWithNoiseReduceSlider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.VolumeCheckWithNoiseReduceSlider.setInvertedAppearance(False)
        self.VolumeCheckWithNoiseReduceSlider.setInvertedControls(False)
        self.VolumeCheckWithNoiseReduceSlider.setTickPosition(QtWidgets.QSlider.TickPosition.NoTicks)
        self.VolumeCheckWithNoiseReduceSlider.setObjectName("VolumeCheckWithNoiseReduceSlider")
        self.horizontalLayout_6.addWidget(self.VolumeCheckWithNoiseReduceSlider)
        self.horizontalLayout_4.addLayout(self.horizontalLayout_6)
        self.verticalLayout.addWidget(self.horizontalFrame)
        self.settings.addWidget(self.NoiseReduce, 0, QtCore.Qt.AlignmentFlag.AlignTop)
        self.InputMode = QtWidgets.QFrame(parent=self.settingsWrapper)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.InputMode.sizePolicy().hasHeightForWidth())
        self.InputMode.setSizePolicy(sizePolicy)
        self.InputMode.setObjectName("InputMode")
        self.InputModedad = QtWidgets.QVBoxLayout(self.InputMode)
        self.InputModedad.setContentsMargins(25, 20, 25, 0)
        self.InputModedad.setSpacing(15)
        self.InputModedad.setObjectName("InputModedad")
        self.label_9 = QtWidgets.QLabel(parent=self.InputMode)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy)
        self.label_9.setStyleSheet("QLabel {\n"
"    color:white;\n"
"    font-size:18px;\n"
"}")
        self.label_9.setObjectName("label_9")
        self.InputModedad.addWidget(self.label_9)
        self.Choose = QtWidgets.QFrame(parent=self.InputMode)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Choose.sizePolicy().hasHeightForWidth())
        self.Choose.setSizePolicy(sizePolicy)
        self.Choose.setObjectName("Choose")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.Choose)
        self.verticalLayout_3.setContentsMargins(0, -1, 0, -1)
        self.verticalLayout_3.setSpacing(20)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.radioButton = QtWidgets.QRadioButton(parent=self.Choose)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.radioButton.sizePolicy().hasHeightForWidth())
        self.radioButton.setSizePolicy(sizePolicy)
        self.radioButton.setStyleSheet("QRadioButton {\n"
"color:white;\n"
"font-size:20px;\n"
"}\n"
"\n"
"QRadioButton::indicator {\n"
"    width: 18px;\n"
"    height: 18px;\n"
"    border-radius: 9px;\n"
"    border: 2px solid #b9bbbe;\n"
"    background: transparent;\n"
"}\n"
"\n"
"QRadioButton::indicator:hover {\n"
"    border: 2px solid #dcddde;\n"
"}\n"
"\n"
"QRadioButton::indicator:checked {\n"
"    background: grey;\n"
"}")
        self.radioButton.setChecked(True)
        self.radioButton.setObjectName("radioButton")
        self.verticalLayout_3.addWidget(self.radioButton)
        self.radioButton_2 = QtWidgets.QRadioButton(parent=self.Choose)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.radioButton_2.sizePolicy().hasHeightForWidth())
        self.radioButton_2.setSizePolicy(sizePolicy)
        self.radioButton_2.setStyleSheet("QRadioButton {\n"
"color:white;\n"
"font-size:20px;\n"
"}\n"
"\n"
"QRadioButton::indicator {\n"
"    width: 18px;\n"
"    height: 18px;\n"
"    border-radius: 9px;\n"
"    border: 2px solid #b9bbbe;\n"
"    background: transparent;\n"
"}\n"
"\n"
"QRadioButton::indicator:hover {\n"
"    border: 2px solid #dcddde;\n"
"}\n"
"\n"
"QRadioButton::indicator:checked {\n"
"    background: grey;\n"
"}")
        self.radioButton_2.setObjectName("radioButton_2")
        self.verticalLayout_3.addWidget(self.radioButton_2)
        self.InputModedad.addWidget(self.Choose)
        self.settings.addWidget(self.InputMode, 0, QtCore.Qt.AlignmentFlag.AlignTop)
        self.settings.setStretch(0, 1)
        self.settings.setStretch(1, 2)
        self.settings.setStretch(2, 4)
        self.verticalLayout_2.addWidget(self.settingsWrapper)

        self.retranslateUi(VoiceParams)
        QtCore.QMetaObject.connectSlotsByName(VoiceParams)

    def retranslateUi(self, VoiceParams):
        _translate = QtCore.QCoreApplication.translate
        VoiceParams.setWindowTitle(_translate("VoiceParams", "Form"))
        self.label.setText(_translate("VoiceParams", "Устройство вывода"))
        self.label_4.setText(_translate("VoiceParams", "Громкость звука:"))
        self.VolimeOfHeadphonesLabel.setText(_translate("VoiceParams", "1.0"))
        self.label_2.setText(_translate("VoiceParams", "Устройство ввода (микрофон)"))
        self.label_5.setText(_translate("VoiceParams", "Громкость микрофона:"))
        self.label_6.setText(_translate("VoiceParams", "1.0"))
        self.label_7.setText(_translate("VoiceParams", "Шумоподавление"))
        self.label_8.setText(_translate("VoiceParams", "Подваление шумов микрофона нейросетью"))
        self.pushButton_2.setText(_translate("VoiceParams", "Проверка "))
        self.label_9.setText(_translate("VoiceParams", "Режим ввода"))
        self.radioButton.setText(_translate("VoiceParams", "По голосу"))
        self.radioButton_2.setText(_translate("VoiceParams", "По нажатию"))
