import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QSlider, QWidget
from PyQt6.QtCore import Qt
from logic.Main.Voice_main.VoiceParameters import Ui_VoiceParams
from logic.Main.Parameters.Parameters import Ui_Parameters


class ParamsWindow(QMainWindow):
    def __init__(self):
        super(ParamsWindow, self).__init__()

        self.ui_pr = Ui_Parameters()
        self.ui_pr.setupUi(self)

        self.voicepr_widget = QWidget()
        self.voicepr = Ui_VoiceParams()
        self.voicepr.setupUi(self.voicepr_widget)

        self.ui_pr.OptionWidget.addWidget(self.voicepr_widget)

        self.ui_pr.pushButton.clicked.connect(self.show_voice_params)

    def show_voice_params(self):
        print(1)
        self.ui_pr.OptionWidget.setCurrentWidget(self.voicepr_widget)

